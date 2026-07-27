from django.contrib import admin

# Register your models here.
from django.utils.html import format_html
from .models import *

admin.site.register(Category)
admin.site.register(Medicine)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(StockMovement)
admin.site.register(Order)
admin.site.register(OrderItem)  
admin.site.register(OrderStatusHistory)
admin.site.register(CustomerOrder)
admin.site.register(UserWishlist)
admin.site.register(Cart)
admin.site.register(CartItem)
