# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- 1, 2, 3. Core Authentication and Navigation Pages ---
    path('', views.splash_screen, name='splash'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('main_menu/', views.main_menu, name='main_menu'),
    path('logout/', views.logout_user, name='logout'),

    # --- 7, 8, 9, 12. Medicine Catalog and Ordering Flow ---
    path('medicine/browse/', views.medicine_list_view, name='medicine_list'),
    path('medicine/info/<int:medicine_id>/', views.medicine_info_view, name='medicine_info'),
    path('order/add/<int:medicine_id>/', views.add_to_order, name='add_to_order'),
    path('order/current/', views.order_list_view, name='order_list'),
    path('order/remove/<int:item_id>/', views.remove_order_item, name='remove_order_item'),
    path('order/checkout/', views.order_checkout_view, name='order_checkout'),
    path('order/process/', views.process_order, name='process_order'),

    # --- 6, 10, 13, 14. User Profile and Tools ---
    path('profile/', views.profile_view, name='profile_view'),
    path('history/', views.medicine_history_view, name='medicine_history'),
    path('settings/', views.settings_view, name='settings'),
    path('feedback/', views.feedback_view, name='feedback'),

    # --- 11. Announcements ---
    path('announcements/', views.announcements_view, name='announcements'),
    path('announcements/add/', views.add_post, name='add_post'),
    path('announcements/edit/<int:post_id>/', views.edit_post, name='edit_post'),

    # --- 15, 16. Post-Order & Delivery Flow ---
    path('queue/', views.queue_page, name='queue_page'),
    path('delivery/', views.delivery_page, name='delivery_page'),

    # --- 5, 17, 18, 19. Admin/Staff Views (FIXED TO MANAGEMENT/) ---
    path('management/menu/', views.admin_menu_view, name='admin_menu'),
    path('management/stock/', views.medicine_stock_view, name='medicine_stock'),
    path('management/stock/edit/<int:medicine_id>/', views.edit_medicine_view, name='edit_medicine'),
    path('management/analytics/', views.analytics_view, name='analytics'),
    path('management/records/', views.medicine_records_view, name='medicine_records'),
]