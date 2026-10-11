from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_medicines, name='search_medicines'),
    
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Medicines
    path('medicines/', views.medicine_list, name='medicines'),
    path('medicine/<int:pk>/', views.medicine_detail, name='medicine_detail'),

    path('brand/<str:brand>/', views.brand_products, name='brand_products'),

    
    # Cart
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:medicine_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:medicine_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:medicine_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Orders
    path('orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    
  # ===== LAB TESTS =====
    path('lab-tests/', views.lab_tests, name='lab_tests'),
    path('lab-tests/book/', views.lab_booking_form, name='lab_booking_form'),
    path('lab-tests/book/submit/', views.book_lab_test, name='book_lab_test'),
    path('lab-tests/payment/', views.lab_payment, name='lab_payment'),
    path('lab-tests/payment/process/', views.lab_payment_process, name='lab_payment_process'),
    path('lab-tests/success/', views.lab_booking_success, name='lab_booking_success'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:medicine_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:medicine_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Prescription Upload
    path('upload-prescription/', views.upload_prescription, name='upload_prescription'),
    
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.category_details, name='category_details'),
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
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
       # ===== CHECKOUT & ORDERS =====
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('buy-now/<int:medicine_id>/', views.buy_now, name='buy_now'),

    # ===== ADDRESS URLS (✅ ADD THESE) =====
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/create/', views.address_create, name='address_create'),
    path('addresses/<int:pk>/update/', views.address_update, name='address_update'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('addresses/<int:pk>/set-default/', views.address_set_default, name='address_set_default'),
    # #aidoctor
    # path('ai-doctor/', views.ai_doctor, name='ai_doctor'),
    # path('symptom-checker/', views.symptom_checker, name='symptom_checker'),
    # path('lab-packages/', views.lab_packages, name='lab_packages'),
    # path('wellness/', views.wellness, name='wellness'),
    # path('health-insurance/', views.health_insurance, name='health_insurance'),
    path('category/<str:category_name>/', views.category_count, name='category_count'),
    # API URLs
    path('api/get-medicine-details/', views.get_medicine_details, name='get_medicine_details'),
]