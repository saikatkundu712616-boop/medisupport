from django.db import models

# Create your models herefrom django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Medicine(models.Model):
    # Medicine Types
    TABLET = 'TAB'
    CAPSULE = 'CAP'
    SYRUP = 'SYR'
    INJECTION = 'INJ'
    CREAM = 'CRM'
    DROPS = 'DRP'
    OTHER = 'OTH'
    
    MEDICINE_TYPES = [
        (TABLET, 'Tablet'),
        (CAPSULE, 'Capsule'),
        (SYRUP, 'Syrup'),
        (INJECTION, 'Injection'),
        (CREAM, 'Cream'),
        (DROPS, 'Drops'),
        (OTHER, 'Other'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='medicines')
    
    medicine_type = models.CharField(max_length=3, choices=MEDICINE_TYPES, default=TABLET)
    generic_name = models.CharField(max_length=200, blank=True)
    manufacturer = models.CharField(max_length=200)
    composition = models.TextField(blank=True, help_text="Active ingredients and composition")
    
    # Pricing
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Stock
    quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    
    # Additional info
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='medicines/', blank=True, null=True)
    
    # Prescription required
    prescription_required = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.batch_number}"

    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    def get_discounted_price(self):
        if self.discount_percentage > 0:
            return self.selling_price - (self.selling_price * self.discount_percentage / 100)
        return self.selling_price

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Sale(models.Model):
    COMPLETED = 'COM'
    PENDING = 'PEN'
    CANCELLED = 'CAN'
    
    STATUS_CHOICES = [
        (COMPLETED, 'Completed'),
        (PENDING, 'Pending'),
        (CANCELLED, 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales')
    invoice_number = models.CharField(max_length=50, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=COMPLETED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sale {self.invoice_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        self.due_amount = self.total_amount - self.paid_amount - self.discount
        super().save(*args, **kwargs)

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.medicine.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.selling_price) - self.discount
        super().save(*args, **kwargs)

class StockMovement(models.Model):
    INWARD = 'IN'
    OUTWARD = 'OUT'
    
    MOVEMENT_TYPES = [
        (INWARD, 'Inward'),
        (OUTWARD, 'Outward'),
    ]

    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_movements')
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    reference = models.CharField(max_length=100)  # Sale or Purchase invoice number
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movement_type} - {self.medicine.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        if self.movement_type == self.INWARD:
            self.medicine.quantity += self.quantity
        else:
            self.medicine.quantity -= self.quantity
        self.medicine.save()
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('PEN', 'Pending'),
        ('PRO', 'Processing'),
        ('SHP', 'Shipped'),
        ('DEL', 'Delivered'),
        ('CAN', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PEN', 'Pending'),
        ('PAID', 'Paid'),
        ('FAIL', 'Failed'),
        ('REF', 'Refunded'),
    ]

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)

    customer_address = models.TextField(blank=True)

    order_status = models.CharField(
        max_length=3,
        choices=STATUS_CHOICES,
        default='PEN'
    )

    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='PEN'
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

    order_date = models.DateTimeField(auto_now_add=True)
    delivered_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = "ORD" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    medicine = models.ForeignKey(
        Medicine,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.order.order_number} - {self.medicine.name}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )

    status = models.CharField(max_length=3, choices=Order.STATUS_CHOICES)
    note = models.TextField(blank=True)

    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"