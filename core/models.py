# core/models.py

from django.db import models  # <-- MANDATORY FIX for NameError
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # Added null=True for flexibility in database
    middle_initial = models.CharField(max_length=1, blank=True, null=True)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=10)
    is_senior = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "User Profiles"


# --- NEW MEDICINE AND ORDER MODELS ---

class Medicine(models.Model):
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True, null=True)
    dosage = models.CharField(max_length=50)  # e.g., '500mg', '10ml'
    formulation = models.CharField(max_length=50)  # e.g., 'Tablet', 'Capsule', 'Syrup'
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"

    class Meta:
        verbose_name_plural = "Medicines"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_request = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.medicine.name}"