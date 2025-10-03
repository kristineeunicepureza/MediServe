# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F  # FIX: Ensures F is imported
from .models import UserProfile, Medicine, Order, OrderItem


# NOTE: Placeholder models/forms for other features (Post, Feedback) are assumed or will be added later.


# --- Core Authentication and Navigation Views (1, 2, 3, 4) ---

def splash_screen(request):
    return render(request, 'core/splash.html')


def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('main_menu')
            else:
                # IMPORTANT FIX CONFIRMED: This message covers both 'wrong password' and 'user not found'
                messages.error(request, "Invalid username or password. Please try again.")
        else:
            # Handle invalid form submission (e.g., empty fields)
            messages.error(request, "Please enter both username and password.")

        # Always re-render the page on failure to show the message
        return render(request, 'core/login.html', {'form': form})

    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


@transaction.atomic
def signup_page(request):
    if request.method == 'POST':
        # (3.x) Registration logic as previously provided...
        try:
            user = User.objects.create_user(username=request.POST['username'], password=request.POST['password'])
            UserProfile.objects.create(
                user=user,
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                middle_initial=request.POST.get('middle_initial', ''),
                date_of_birth=request.POST['date_of_birth'],
                sex=request.POST['sex'],
                is_senior='senior_citizen_id' in request.FILES,
                is_pwd='pwd_id' in request.FILES,
            )
            login(request, user)
            messages.success(request, "Registration successful! Welcome to MediServe.")
            return redirect('main_menu')
        except Exception as e:
            if 'user' in locals(): user.delete()
            messages.error(request, f"Registration failed: {e}")
            return redirect('signup')
    return render(request, 'core/signup.html')


@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('splash')


@login_required
def main_menu(request):
    # (4.0 & 5.0) Logic to redirect to user or admin menu
    is_admin = request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.is_admin)

    if is_admin:
        # Placeholder data for Admin Menu (5.6 Recent Brangay Announcement Preview)
        context = {'recent_announcement': "New protocol for inventory check starting tomorrow."}
        return render(request, 'core/admin_menu.html', context)  # (5.0)
    else:
        # Placeholder data for User Menu (4.3 Recent Brangay Announcement Preview)
        context = {'recent_announcement': "Vaccination drive scheduled this Friday."}
        return render(request, 'core/main_menu.html', context)  # (4.0)


# --- Medicine Catalog and Ordering Views (7, 8, 9, 12) ---

@login_required
def medicine_list_view(request):
    # (7.0)
    medicines = Medicine.objects.all().order_by('name')
    context = {'medicines': medicines}
    return render(request, 'core/medicine_list.html', context)


@login_required
def medicine_info_view(request, medicine_id):
    # (8.0)
    medicine = get_object_or_404(Medicine, pk=medicine_id)
    context = {'medicine': medicine}
    return render(request, 'core/medicine_info.html', context)


@login_required
def add_to_order(request, medicine_id):
    # (8.5 & 7.4) Logic as previously provided...
    if request.method == 'POST':
        medicine = get_object_or_404(Medicine, pk=medicine_id)
        quantity = int(request.POST.get('amount', 1))
        special_request = request.POST.get('special_request', '')
        # ... [Logic to add/update OrderItem and Order total] ...
        try:
            if quantity <= 0:
                messages.error(request, "Quantity must be at least 1.")
                return redirect('medicine_info', medicine_id=medicine.id)
            order, created = Order.objects.get_or_create(user=request.user, status='Pending',
                                                         defaults={'total_price': 0.00})

            order_item, item_created = OrderItem.objects.get_or_create(
                order=order,
                medicine=medicine,
                defaults={'quantity': 0, 'unit_price': medicine.price, 'special_request': special_request}
            )

            # Recalculate old subtotal if updating
            old_subtotal = order_item.quantity * order_item.unit_price

            # Update quantity and calculate new subtotal
            if not item_created:
                order_item.quantity += quantity
                order_item.special_request = special_request
            else:
                order_item.quantity = quantity

            order_item.save()

            new_subtotal = order_item.quantity * order_item.unit_price

            # Update Order Total safely using F()
            if not item_created:
                order.total_price = F('total_price') - old_subtotal + new_subtotal
            else:
                order.total_price = F('total_price') + new_subtotal

            order.save()
            messages.success(request, f"{quantity} x {medicine.name} added to your order.")
            return redirect('medicine_list')
        except Exception as e:
            messages.error(request, f"Could not add to order: {e}")

    return redirect('medicine_list')


@login_required
def order_list_view(request):
    # (9.0)
    try:
        current_order = Order.objects.get(user=request.user, status='Pending')
        order_items = current_order.items.select_related('medicine')
        current_order.refresh_from_db()
        context = {'order': current_order, 'items': order_items, 'total': current_order.total_price}
    except Order.DoesNotExist:
        context = {'order': None, 'items': [], 'total': 0.00}
    return render(request, 'core/order_list.html', context)


@login_required
def remove_order_item(request, item_id):
    # (9.4) Logic as previously provided...
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, pk=item_id)
        current_order = order_item.order

        cost_to_remove = order_item.quantity * order_item.unit_price
        current_order.total_price = F('total_price') - cost_to_remove
        current_order.save()
        current_order.refresh_from_db()

        item_name = order_item.medicine.name
        order_item.delete()

        if current_order.items.count() == 0:
            current_order.delete()
            messages.info(request, "Your cart is now empty.")
            return redirect('main_menu')

        messages.success(request, f"Removed {item_name} from your order.")
        return redirect('order_list')
    return redirect('order_list')


@login_required
def order_checkout_view(request):
    # (12.0) Pre-confirmation/Review page
    try:
        current_order = Order.objects.get(user=request.user, status='Pending')
        items = current_order.items.select_related('medicine').all()
        if not items.exists():
            messages.error(request, "Your order is empty.")
            return redirect('order_list')
        context = {'order': current_order, 'items': items}
        return render(request, 'core/order_confirmation.html', context)
    except Order.DoesNotExist:
        messages.error(request, "No pending order found to checkout.")
        return redirect('main_menu')


@login_required
@transaction.atomic
def process_order(request):
    # Final processing/stock deduction
    try:
        current_order = Order.objects.select_for_update().get(user=request.user, status='Pending')
        items = current_order.items.select_related('medicine').all()

        # 1. Stock Check
        for item in items:
            item.medicine.refresh_from_db()
            if item.quantity > item.medicine.stock_quantity:
                messages.error(request,
                               f"Checkout failed. Insufficient stock ({item.medicine.stock_quantity} available) for {item.medicine.name}.")
                return redirect('order_list')

        # 2. Update stock
        for item in items:
            Medicine.objects.filter(pk=item.medicine.pk).update(stock_quantity=F('stock_quantity') - item.quantity)

        # 3. Change Order Status to 'Processing'
        current_order.status = 'Processing'
        current_order.save()

        messages.success(request,
                         f"Order #{current_order.id} submitted successfully! Your order number will be displayed shortly.")
        return redirect('queue_page')  # Redirect to the Queue Page (15.0)

    except Order.DoesNotExist:
        messages.error(request, "No pending order found.")
        return redirect('main_menu')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred during checkout: {e}")
        return redirect('order_list')


# --- User Profile and Tools Views (6, 10, 13, 14, 15, 16) ---

@login_required
def profile_view(request):
    # 1. Safely retrieve or create the UserProfile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # FIX APPLIED HERE to satisfy NOT NULL constraints on date_of_birth and sex
        user_profile = UserProfile.objects.create(
            user=request.user,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            # Database requires a non-null value for DateField and CharField
            date_of_birth='2000-01-01', # Provide a safe default date
            sex='Other',                # Provide a safe default for sex
        )
        messages.info(request, "Your missing profile record was created. Please review and save your details.")

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update UserProfile fields
                user_profile.first_name = request.POST.get('first_name', user_profile.first_name)
                user_profile.last_name = request.POST.get('last_name', user_profile.last_name)
                middle_initial_val = request.POST.get('middle_initial')
                user_profile.middle_initial = middle_initial_val if middle_initial_val else None
                user_profile.date_of_birth = request.POST.get('date_of_birth', user_profile.date_of_birth)
                user_profile.sex = request.POST.get('sex', user_profile.sex)
                user_profile.save()

                # Update core Django User model fields for name sync
                request.user.first_name = user_profile.first_name
                request.user.last_name = user_profile.last_name
                request.user.save()

            messages.success(request, "Your profile has been updated successfully! 👍")
            return redirect('profile_view')

        except Exception as e:
            messages.error(request, f"There was an error updating your profile: {e}")
            return redirect('profile_view')

    context = {
        'profile': user_profile,
    }

    return render(request, 'core/profile_view.html', context)

# ... (The rest of your core/views.py file remains unchanged)
@login_required
def medicine_history_view(request):
    # (10.0) Placeholder for viewing past orders
    past_orders = Order.objects.filter(user=request.user).exclude(status='Pending').order_by('-order_date')[:10]
    context = {'past_orders': past_orders}
    return render(request, 'core/medicine_history.html', context)


@login_required
def settings_view(request):
    # (13.0) Placeholder for settings
    return render(request, 'core/settings.html')


@login_required
def feedback_view(request):
    # (14.0) Placeholder for feedback form
    if request.method == 'POST':
        messages.success(request, "Thank you for your feedback! It has been submitted.")
        return redirect('main_menu')
    return render(request, 'core/feedback.html')


@login_required
def queue_page(request):
    # (15.0) Placeholder for real-time queue
    current_order = Order.objects.filter(user=request.user, status__in=['Processing', 'Shipped']).last()
    context = {
        'current_number': 42,  # Mock data
        'estimated_wait': "15-20 minutes",  # Mock data
        'current_order': current_order
    }
    return render(request, 'core/queue_page.html', context)


@login_required
def delivery_page(request):
    # (16.0) User/Admin view based on role
    is_admin = request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.is_admin)
    if is_admin:
        # (16.1) Admin View
        processing_orders = Order.objects.filter(status='Processing').order_by('order_date')
        context = {'orders': processing_orders}
        return render(request, 'core/admin_delivery_view.html', context)
    else:
        # (16.2) User View
        user_orders = Order.objects.filter(user=request.user, status__in=['Processing', 'Shipped']).order_by(
            '-order_date')
        context = {'user_orders': user_orders}
        return render(request, 'core/user_delivery_view.html', context)


# --- Announcement Views (11) ---

@login_required
def announcements_view(request):
    # (11.0) Placeholder
    is_admin = request.user.is_superuser or (hasattr(request.user, 'userprofile') and request.user.userprofile.is_admin)
    context = {
        'announcements': [
            {'title': 'New Store Hours', 'date': 'Oct 1', 'content': 'We are now open until 8 PM.'},
            {'title': 'Flu Vaccine Drive', 'date': 'Sept 28', 'content': 'Sign up for the flu shot next week.'},
        ],
        'is_admin': is_admin
    }
    return render(request, 'core/announcements.html', context)


@login_required
def add_post(request):
    # (11.2, 11.4) Admin Only
    if request.user.userprofile.is_admin and request.method == 'POST':
        # Placeholder logic
        messages.success(request, "Announcement posted successfully.")
        return redirect('announcements')
    return render(request, 'core/announcements.html')  # Redirect back to the page


@login_required
def edit_post(request, post_id):
    # (11.5) Admin Only
    if request.user.userprofile.is_admin and request.method == 'POST':
        # Placeholder logic
        messages.success(request, f"Announcement {post_id} updated successfully.")
        return redirect('announcements')
    messages.error(request, "You do not have permission to edit posts.")
    return redirect('announcements')


# --- Admin/Staff Views (5, 17, 18, 19) ---

@login_required
def admin_menu_view(request):
    # (5.0) Logic is handled by main_menu redirect. This view simply renders the admin template.
    context = {'recent_announcement': "New protocol for inventory check starting tomorrow."}
    return render(request, 'core/admin_menu.html', context)


@login_required
def medicine_stock_view(request):
    # (17.0)
    medicines = Medicine.objects.all().order_by('name')
    context = {'medicines': medicines}
    return render(request, 'core/medicine_stock.html', context)


@login_required
def edit_medicine_view(request, medicine_id):
    # (17.4, 17.5) Placeholder
    medicine = get_object_or_404(Medicine, pk=medicine_id)
    if request.method == 'POST':
        # Placeholder update logic
        messages.success(request, f"{medicine.name} updated successfully.")
        return redirect('medicine_stock')

    context = {'medicine': medicine}
    return render(request, 'core/edit_medicine.html', context)


@login_required
def analytics_view(request):
    # (18.0) Placeholder
    context = {
        'monthly_sales': [1200, 1500, 1800, 2500],
        'top_sellers': [{'name': 'Paracetamol', 'count': 500}, {'name': 'Amoxicillin', 'count': 350}]
    }
    return render(request, 'core/analytics.html', context)


@login_required
def medicine_records_view(request):
    # (19.0) Placeholder
    context = {
        'records': [
            {'id': 1, 'medicine': 'Paracetamol', 'action': 'Stock In', 'date': '2024-09-01', 'qty': 1000},
            {'id': 2, 'medicine': 'Amoxicillin', 'action': 'Price Change', 'date': '2024-09-15', 'old': 25.00,
             'new': 28.00},
        ]
    }
    return render(request, 'core/medicine_records.html', context)