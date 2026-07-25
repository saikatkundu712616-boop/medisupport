from django.contrib import admin

# Register your models here.
from django.utils.html import format_html
from .models import (
    Category,  Medicine, Customer, 
   Sale, SaleItem, StockMovement,    Order,
    OrderItem,
    OrderStatusHistory,
)
admin.site.register(Category)
admin.site.register(Medicine)
admin.site.register(Customer)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(StockMovement)
admin.site.register(Order)
admin.site.register(OrderItem)  
admin.site.register(OrderStatusHistory)