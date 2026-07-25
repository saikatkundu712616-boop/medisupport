from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
   
    
    # Medicine URLs
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/create/', views.medicine_create, name='medicine_create'),
    path('medicines/<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/<int:pk>/update/', views.medicine_update, name='medicine_update'),
    path('medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('medicines/<int:pk>/stock-movement/', views.medicine_stock_movement, name='medicine_stock_movement'),
    
    # Customer URLs
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    
    # Sale URLs
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/<int:pk>/delete/', views.sale_delete, name='sale_delete'),

    path('orders/', views.admin_order_management, name='admin_order_management'),
    path('order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('order/<int:order_id>/invoice/', views.admin_order_invoice, name='admin_order_invoice'),
    path('orders/export/', views.admin_order_export, name='admin_order_export'),
    path('orders/bulk-action/', views.admin_bulk_order_action, name='admin_bulk_order_action'),

    # API URLs
    path('api/get-medicine-details/', views.get_medicine_details, name='get_medicine_details'),
]