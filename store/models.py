from django.db import models

# Create your models herefrom django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 
from decimal import Decimal
import uuid
import random
import string
from datetime import datetime

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
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
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

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


    

class CustomerOrder(models.Model):
    PENDING = 'PEN'
    PROCESSING = 'PRO'
    SHIPPED = 'SHP'
    DELIVERED = 'DEL'
    CANCELLED = 'CAN'
    RETURNED = 'RET'
    REFUNDED = 'REF'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
        (RETURNED, 'Returned'),
        (REFUNDED, 'Refunded'),
    ]
    
    PAYMENT_PENDING = 'PEN'
    PAID = 'PAID'
    FAILED = 'FLD'
    REFUNDED = 'REF'
    
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Payment Pending'),
        (PAID, 'Paid'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, db_index=True)
    
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    shipping_address = models.TextField()
    billing_address = models.TextField(blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    payment_status = models.CharField(max_length=4, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    order_status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=PENDING)
    
    order_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    cancelled_date = models.DateTimeField(null=True, blank=True)
    
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    courier_name = models.CharField(max_length=100, blank=True, null=True)
    tracking_url = models.URLField(blank=True, null=True)
    
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        # self.calculate_totals()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f'ORD-{date_str}-{random_str}'

    def calculate_totals(self):
        if not self.pk:
           return  # Skip if order isn't saved yet
        items = self.items.all()
        if not items.exists():
          return
        self.subtotal = sum(item.total for item in items)
        self.discount_amount = sum(item.discount for item in items)
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = (taxable_amount * self.tax_rate) / 100
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount + self.shipping_charge
        self.grand_total = self.total_amount

    def get_status_badge(self):
        status_colors = {
            'PEN': 'warning',
            'PRO': 'info',
            'SHP': 'primary',
            'DEL': 'success',
            'CAN': 'danger',
            'RET': 'secondary',
            'REF': 'secondary'
        }
        return status_colors.get(self.order_status, 'secondary')

    def can_cancel(self):
        return self.order_status in ['PEN', 'PRO'] and not self.is_deleted

class OrderItem(models.Model):
    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    medicine_name = models.CharField(max_length=200, blank=True)
    batch_number = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.medicine_name and self.medicine:
            self.medicine_name = self.medicine.name
            self.batch_number = self.medicine.batch_number
        self.total = (self.quantity * self.price) - self.discount + (self.quantity * self.tax)
        super().save(*args, **kwargs)

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=3, choices=CustomerOrder.STATUS_CHOICES)
    note = models.TextField(blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.user.username}"

    def get_total(self):
        return sum(item.get_total() for item in self.items.all())

    def get_item_count(self):
        return self.items.count()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'medicine']

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity}"

    def get_total(self):
        return self.quantity * self.medicine.selling_price

class UserWishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'medicine']

    def __str__(self):
        return f"{self.user.username} - {self.medicine.name}"

# ==================== USER ADDRESS (NEW) ====================
class UserAddress(models.Model):
    """✅ ADDED - UserAddress model was missing"""
    HOME = 'HOM'
    WORK = 'WRK'
    OTHER = 'OTH'
    
    ADDRESS_TYPES = [
        (HOME, 'Home'),
        (WORK, 'Work'),
        (OTHER, 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=3, choices=ADDRESS_TYPES, default=HOME)
    address_label = models.CharField(max_length=50, blank=True)
    
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    address_line1 = models.TextField()
    address_line2 = models.TextField(blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')
    
    latitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    is_default = models.BooleanField(default=False)
    is_billing = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "User Addresses"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.address_line1[:30]}..."

    def save(self, *args, **kwargs):
        if self.is_default:
            UserAddress.objects.filter(
                user=self.user, is_default=True
            ).exclude(id=self.id).update(is_default=False)
        if self.is_billing:
            UserAddress.objects.filter(
                user=self.user, is_billing=True
            ).exclude(id=self.id).update(is_billing=False)
        super().save(*args, **kwargs)

    def get_full_address(self):
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        if self.landmark:
            parts.append(f"Landmark: {self.landmark}")
        parts.append(f"{self.city}, {self.state} - {self.pincode}")
        parts.append(self.country)
        return ", ".join(parts)

