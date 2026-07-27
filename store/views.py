
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from decimal import Decimal
import json
import random
import string

from .models import *
from .forms import (
    UserRegistrationForm, CategoryForm, 
    MedicineForm, CustomerForm,  SaleForm,
    OrderCreateForm
)
def header(request):
    return render(request, 'Store/header.html')

def home(request):
    """Home page with featured medicines"""
    featured_medicines = Medicine.objects.filter(is_active=True)[:8]
    categories = Category.objects.annotate(
        medicine_count=Count('medicines')
    ).filter(medicine_count__gt=0)[:6]
    
    # Get cart count for authenticated users
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.items.count()
    
    context = {
        'featured_medicines': featured_medicines,
        'categories': categories,
        'cart_count': cart_count,
    }
    return render(request, 'Store/home.html', context)

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_staff or user.is_superuser:
                return redirect("store:admin_dashboard")
            else:
                return redirect("store:home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "Store/login.html")

def user_register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('store:home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create customer profile
            Customer.objects.create(
                user=user,
                name=f"{user.first_name} {user.last_name}",
                email=user.email,
                phone=request.POST.get('phone', '')
            )
            
            # Create cart for user
            Cart.objects.create(user=user)
            
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to MediSupport.')
            return redirect('store:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'Store/register.html', {'form': form})

@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('store:login')

@login_required
def user_profile(request):
    """User profile view with edit functionality"""
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('store:profile')
    
    # Get order count
    orders_count = CustomerOrder.objects.filter(user=user).count()
    
    context = {
        'user': user,
        'orders_count': orders_count,
    }
    return render(request, 'Store/profile.html', context)

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('store:profile')
        
        if new_password1 != new_password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('store:profile')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('store:profile')
        
        request.user.set_password(new_password1)
        request.user.save()
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Password changed successfully!')
        return redirect('store:profile')
    
    return redirect('profile')


def medicine_list(request):
    """List all medicines with filters and pagination"""
    medicines = Medicine.objects.filter(is_active=True).select_related('category')
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        medicines = medicines.filter(
            Q(name__icontains=search_query) |
            Q(generic_name__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(batch_number__icontains=search_query)
        )
    
    # Category filter
    categories = Category.objects.annotate(
        medicine_count=Count('medicines', filter=Q(medicines__is_active=True))
    )
    selected_categories = request.GET.getlist('category')
    if selected_categories:
        medicines = medicines.filter(category_id__in=selected_categories)
    
    # Price filter
    max_price = request.GET.get('max_price')
    if max_price and max_price.isdigit():
        medicines = medicines.filter(selling_price__lte=int(max_price))
    
    # Stock filter
    in_stock = request.GET.get('in_stock')
    if in_stock == 'true':
        medicines = medicines.filter(quantity__gt=0)
    
    # Sorting
    sort = request.GET.get('sort', 'popular')
    if sort == 'price_low':
        medicines = medicines.order_by('selling_price')
    elif sort == 'price_high':
        medicines = medicines.order_by('-selling_price')
    elif sort == 'newest':
        medicines = medicines.order_by('-created_at')
    else:
        medicines = medicines.order_by('-id')
    
    # Pagination
    paginator = Paginator(medicines, 12)
    page = request.GET.get('page')
    medicines_page = paginator.get_page(page)
    
    # Get cart count
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.items.count()
    
    context = {
        'medicines': medicines_page,
        'categories': categories,
        'selected_categories': selected_categories,
        'search_query': search_query,
        'max_price': max_price or 5000,
        'in_stock': in_stock,
        'sort': sort,
        'cart_count': cart_count,
    }
    return render(request, 'store/medicines.html', context)

def medicine_detail(request, pk):
    """Medicine detail view"""
    medicine = get_object_or_404(Medicine, pk=pk, is_active=True)
    
    # Get related medicines (same category)
    related_medicines = Medicine.objects.filter(
        category=medicine.category, 
        is_active=True
    ).exclude(id=pk)[:6]
    
    # Check if in wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = UserWishlist.objects.filter(
            user=request.user, 
            medicine=medicine
        ).exists()
    
    # Get cart count
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.items.count()
    
    context = {
        'medicine': medicine,
        'related_medicines': related_medicines,
        'in_wishlist': in_wishlist,
        'cart_count': cart_count,
    }
    return render(request, 'medicine_detail.html', context)

def category_products(request, slug):
    """View products by category"""
    category = get_object_or_404(Category, slug=slug)
    medicines = Medicine.objects.filter(category=category, is_active=True)
    
    context = {
        'category': category,
        'medicines': medicines,
    }
    return render(request, 'category_products.html', context)

def brand_products(request, brand):
    """View products by brand"""
    medicines = Medicine.objects.filter(manufacturer__icontains=brand, is_active=True)
    
    context = {
        'brand': brand,
        'medicines': medicines,
    }
    return render(request, 'brand_products.html', context)

def search_medicines(request):
    """Search medicines"""
    query = request.GET.get('q', '')
    if query:
        medicines = Medicine.objects.filter(
            Q(name__icontains=query) |
            Q(generic_name__icontains=query) |
            Q(manufacturer__icontains=query),
            is_active=True
        )
    else:
        medicines = Medicine.objects.none()
    
    context = {
        'query': query,
        'medicines': medicines,
    }
    return render(request, 'store/search_results.html', context)


def category_list(request):
    """List all categories"""
    categories = Category.objects.annotate(
        medicine_count=Count('medicines', filter=Q(medicines__is_active=True))
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'Store/categories.html', context)

# ==================== CART VIEWS ====================

@login_required
def view_cart(request):
    """View shopping cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('medicine')
    
    total = sum(item.get_total() for item in cart_items)
    item_count = cart_items.count()
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
        'cart_count': item_count,
    }
    return render(request, 'Store/cart.html', context)

@login_required
def add_to_cart(request, medicine_id):
    """Add medicine to cart"""
    medicine = get_object_or_404(Medicine, pk=medicine_id, is_active=True)
    
    if medicine.quantity <= 0:
        messages.error(request, f'Sorry, {medicine.name} is out of stock.')
        return redirect('medicine_detail', pk=medicine_id)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if item already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        medicine=medicine,
        defaults={'quantity': 1}
    )
    
    if not created:
        if cart_item.quantity < medicine.quantity:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'{medicine.name} quantity updated in cart.')
        else:
            messages.warning(request, f'Only {medicine.quantity} items available.')
    else:
        messages.success(request, f'{medicine.name} added to cart.')
    
    # Update session cart count
    request.session['cart_count'] = cart.items.count()
    
    return redirect('store:view_cart')

@login_required
def remove_from_cart(request, medicine_id):
    """Remove item from cart"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, medicine_id=medicine_id)
    
    medicine_name = cart_item.medicine.name
    cart_item.delete()
    
    messages.success(request, f'{medicine_name} removed from cart.')
    request.session['cart_count'] = cart.items.count()
    
    return redirect('store:view_cart')

@login_required
def update_cart(request, medicine_id):
    """Update cart item quantity"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, cart=cart, medicine_id=medicine_id)
        
        if quantity <= 0:
            cart_item.delete()
            messages.info(request, 'Item removed from cart.')
        elif quantity <= cart_item.medicine.quantity:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully.')
        else:
            messages.warning(request, f'Only {cart_item.medicine.quantity} items available.')
        
        request.session['cart_count'] = cart.items.count()
    
    return redirect('store:view_cart')

@login_required
def checkout(request):
    """Checkout view"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related('medicine')
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('view_cart')
    
    total = sum(item.get_total() for item in cart_items)
    
    if request.method == 'POST':
        # Create order
        order = CustomerOrder.objects.create(
            user=request.user,
            customer_name=request.POST.get('customer_name', request.user.get_full_name()),
            customer_email=request.POST.get('customer_email', request.user.email),
            customer_phone=request.POST.get('customer_phone', ''),
            shipping_address=request.POST.get('shipping_address', ''),
            billing_address=request.POST.get('billing_address', ''),
            subtotal=total,
            grand_total=total + 40,  # Add delivery charges
            shipping_charge=40,
            order_status='PEN',
            payment_status='PEN'
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                medicine=item.medicine,
                quantity=item.quantity,
                price=item.medicine.selling_price,
                total=item.get_total()
            )
            
            # Update stock
            medicine = item.medicine
            medicine.quantity -= item.quantity
            medicine.save()
        
        # Clear cart
        cart_items.delete()
        request.session['cart_count'] = 0
        
        messages.success(request, f'Order #{order.order_number} placed successfully!')
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'delivery_charge': 40,
        'grand_total': total + 40,
    }
    return render(request, 'checkout.html', context)

# ==================== ORDER VIEWS ====================

@login_required
def my_orders(request):
    """View user's orders"""
    orders = CustomerOrder.objects.filter(user=request.user).order_by('-order_date')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    context = {
        'orders': orders,
        'status': status_filter,
    }
    return render(request, 'Store/my_orders.html', context)

@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(CustomerOrder, pk=order_id, user=request.user)
    items = order.items.all()
    
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'Store/order_detail.html', context)

@login_required
def cancel_order(request, order_id):
    """Cancel an order"""
    order = get_object_or_404(CustomerOrder, pk=order_id, user=request.user)
    
    if order.order_status not in ['PEN', 'PRO']:
        messages.error(request, 'This order cannot be cancelled.')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        order.order_status = 'CAN'
        order.cancelled_date = timezone.now()
        order.save()
        
        # Restore stock
        for item in order.items.all():
            medicine = item.medicine
            medicine.quantity += item.quantity
            medicine.save()
        
        # Create status history
        OrderStatusHistory.objects.create(
            order=order,
            status='CAN',
            note=f"Order cancelled by customer: {request.POST.get('reason', 'No reason provided')}",
            changed_by=request.user
        )
        
        messages.success(request, f'Order #{order.order_number} cancelled successfully.')
        return redirect('store:my_orders')
    
    context = {
        'order': order,
    }
    return render(request, 'Store/cancel_order.html', context)

# ==================== LAB TESTS ====================

def lab_tests(request):
    """Lab tests page"""
    context = {
        'tests': [
            {'name': 'Complete Blood Count', 'price': 499, 'description': '30 tests included'},
            {'name': 'HbA1c Test', 'price': 399, 'description': '3 tests included'},
            {'name': 'Fasting Blood Sugar', 'price': 199, 'description': '1 test included'},
            {'name': 'Lipid Profile', 'price': 599, 'description': '8 tests included'},
            {'name': 'Liver Function Test', 'price': 799, 'description': '12 tests included'},
            {'name': 'Kidney Function Test', 'price': 699, 'description': '10 tests included'},
            {'name': 'Thyroid Profile', 'price': 899, 'description': '5 tests included'},
            {'name': 'Vitamin D Test', 'price': 999, 'description': '1 test included'},
        ]
    }
    return render(request, 'lab_tests.html', context)

# ==================== WISHLIST VIEWS ====================

@login_required
def wishlist(request):
    """View user's wishlist"""
    wishlist_items = UserWishlist.objects.filter(user=request.user).select_related('medicine')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'wishlist.html', context)

@login_required
def add_to_wishlist(request, medicine_id):
    """Add medicine to wishlist"""
    medicine = get_object_or_404(Medicine, pk=medicine_id, is_active=True)
    
    wishlist_item, created = UserWishlist.objects.get_or_create(
        user=request.user,
        medicine=medicine
    )
    
    if created:
        messages.success(request, f'{medicine.name} added to wishlist.')
    else:
        messages.info(request, f'{medicine.name} is already in your wishlist.')
    
    return redirect('medicine_detail', pk=medicine_id)

@login_required
def remove_from_wishlist(request, medicine_id):
    """Remove medicine from wishlist"""
    wishlist_item = get_object_or_404(UserWishlist, user=request.user, medicine_id=medicine_id)
    medicine_name = wishlist_item.medicine.name
    wishlist_item.delete()
    
    messages.success(request, f'{medicine_name} removed from wishlist.')
    return redirect('wishlist')

# ==================== PRESCRIPTION UPLOAD ====================

@login_required
def upload_prescription(request):
    """Upload prescription view"""
    if request.method == 'POST' and request.FILES.get('prescription'):
        prescription_file = request.FILES['prescription']
        
        # Here you would handle the file upload
        # Save to model or cloud storage
        
        messages.success(request, 'Prescription uploaded successfully! We will verify it shortly.')
        return redirect('home')
    
    return render(request, 'upload_prescription.html')

# ==================== ADMIN VIEWS (For Staff) ====================

@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Statistics
    total_medicines = Medicine.objects.count()
    total_orders = CustomerOrder.objects.count()
    total_users = User.objects.count()
    total_categories = Category.objects.count()
    
    # Recent orders
    recent_orders = CustomerOrder.objects.order_by('-order_date')[:10]
    
    # Low stock medicines
    low_stock = Medicine.objects.filter(quantity__lte=10)[:10]
    
    context = {
        'total_medicines': total_medicines,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_categories': total_categories,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def admin_medicines(request):
    """Admin medicine management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    medicines = Medicine.objects.all().order_by('-created_at')
    
    context = {
        'medicines': medicines,
    }
    return render(request, 'admin/medicines.html', context)

@login_required
def admin_medicine_create(request):
    """Admin create medicine"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('admin_medicines')
    else:
        form = MedicineForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin/medicine_form.html', context)

@login_required
def admin_medicine_edit(request, pk):
    """Admin edit medicine"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('admin_medicines')
    else:
        form = MedicineForm(instance=medicine)
    
    context = {
        'form': form,
        'medicine': medicine,
    }
    return render(request, 'admin/medicine_form.html', context)

@login_required
def admin_medicine_delete(request, pk):
    """Admin delete medicine"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('admin_medicines')
    
    context = {
        'medicine': medicine,
    }
    return render(request, 'admin/medicine_confirm_delete.html', context)

# ==================== API VIEWS ====================

@login_required
def api_medicine_details(request):
    """API endpoint for medicine details"""
    medicine_id = request.GET.get('id')
    if medicine_id:
        try:
            medicine = Medicine.objects.get(id=medicine_id, is_active=True)
            data = {
                'id': medicine.id,
                'name': medicine.name,
                'price': float(medicine.selling_price),
                'mrp': float(medicine.mrp),
                'stock': medicine.quantity,
                'image': medicine.image.url if medicine.image else None,
                'category': medicine.category.name,
                'generic_name': medicine.generic_name,
            }
            return JsonResponse({'success': True, 'data': data})
        except Medicine.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Medicine not found'})
    return JsonResponse({'success': False, 'error': 'No medicine ID provided'})

@login_required
def api_cart_count(request):
    """API endpoint for cart count"""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.items.count() if cart else 0
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})

# ==================== CATEGORY MANAGEMENT (Admin) ====================

@login_required
def admin_categories(request):
    """Admin category management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    categories = Category.objects.annotate(
        medicine_count=Count('medicines')
    ).order_by('name')
    
    context = {
        'categories': categories,
    }
    return render(request, 'admin/categories.html', context)

@login_required
def admin_category_create(request):
    """Admin create category"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
    }
    return render(request, 'admin/category_form.html', context)

@login_required
def admin_category_edit(request, pk):
    """Admin edit category"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'admin/category_form.html', context)

@login_required
def admin_category_delete(request, pk):
    """Admin delete category"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    category = get_object_or_404(Category, pk=pk)
    
    if category.medicines.count() > 0:
        messages.error(request, 'Cannot delete category with medicines. Remove or reassign medicines first.')
        return redirect('admin_categories')
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('admin_categories')
    
    context = {
        'category': category,
    }
    return render(request, 'admin/category_confirm_delete.html', context)

# ==================== ORDER MANAGEMENT (Admin) ====================

@login_required
def admin_orders(request):
    """Admin order management"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    orders = CustomerOrder.objects.all().order_by('-order_date')
    
    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    # Statistics
    stats = {
        'total': CustomerOrder.objects.count(),
        'pending': CustomerOrder.objects.filter(order_status='PEN').count(),
        'processing': CustomerOrder.objects.filter(order_status='PRO').count(),
        'shipped': CustomerOrder.objects.filter(order_status='SHP').count(),
        'delivered': CustomerOrder.objects.filter(order_status='DEL').count(),
        'cancelled': CustomerOrder.objects.filter(order_status='CAN').count(),
    }
    
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'stats': stats,
        'status_choices': CustomerOrder.STATUS_CHOICES,
    }
    return render(request, 'admin/orders.html', context)

@login_required
def admin_order_detail(request, order_id):
    """Admin order detail view"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    order = get_object_or_404(CustomerOrder, pk=order_id)
    items = order.items.all()
    status_history = OrderStatusHistory.objects.filter(order=order).order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('order_status')
            if new_status in dict(CustomerOrder.STATUS_CHOICES):
                order.order_status = new_status
                order.save()
                
                OrderStatusHistory.objects.create(
                    order=order,
                    status=new_status,
                    note=f"Status updated to {dict(CustomerOrder.STATUS_CHOICES)[new_status]} by admin",
                    changed_by=request.user
                )
                
                messages.success(request, 'Order status updated successfully!')
                return redirect('admin_order_detail', order_id=order.id)
        
        elif action == 'cancel_order':
            order.order_status = 'CAN'
            order.cancelled_date = timezone.now()
            order.save()
            
            # Restore stock
            for item in order.items.all():
                medicine = item.medicine
                medicine.quantity += item.quantity
                medicine.save()
            
            OrderStatusHistory.objects.create(
                order=order,
                status='CAN',
                note=f"Order cancelled by admin: {request.POST.get('reason', 'No reason provided')}",
                changed_by=request.user
            )
            
            messages.success(request, 'Order cancelled successfully!')
            return redirect('admin_orders')
        
        elif action == 'update_payment':
            payment_status = request.POST.get('payment_status')
            if payment_status in dict(CustomerOrder.PAYMENT_STATUS_CHOICES):
                order.payment_status = payment_status
                order.save()
                messages.success(request, 'Payment status updated successfully!')
                return redirect('admin_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'items': items,
        'status_history': status_history,
        'status_choices': CustomerOrder.STATUS_CHOICES,
        'payment_choices': CustomerOrder.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'admin/order_detail.html', context)



def generate_sample_data(request):
    """Generate sample data for testing (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Create categories
    categories = [
        {'name': 'Antibiotics', 'description': 'Medicines used to treat bacterial infections'},
        {'name': 'Pain Relief', 'description': 'Medicines for pain management'},
        {'name': 'Vitamins', 'description': 'Nutritional supplements and vitamins'},
        {'name': 'Diabetes Care', 'description': 'Medicines for diabetes management'},
        {'name': 'Cardiac Care', 'description': 'Medicines for heart health'},
        {'name': 'Cold & Flu', 'description': 'Medicines for cold and flu symptoms'},
    ]
    
    created_categories = []
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        created_categories.append(category)
    
    # Create sample medicines
    medicines_data = [
        {'name': 'Amoxicillin 500mg', 'category': 'Antibiotics', 'price': 120, 'stock': 100},
        {'name': 'Azithromycin 250mg', 'category': 'Antibiotics', 'price': 85, 'stock': 80},
        {'name': 'Ciprofloxacin 500mg', 'category': 'Antibiotics', 'price': 95, 'stock': 60},
        {'name': 'Paracetamol 500mg', 'category': 'Pain Relief', 'price': 25, 'stock': 200},
        {'name': 'Ibuprofen 400mg', 'category': 'Pain Relief', 'price': 35, 'stock': 150},
        {'name': 'Diclofenac 50mg', 'category': 'Pain Relief', 'price': 30, 'stock': 120},
        {'name': 'Vitamin C 500mg', 'category': 'Vitamins', 'price': 45, 'stock': 90},
        {'name': 'Vitamin D3 2000IU', 'category': 'Vitamins', 'price': 55, 'stock': 75},
        {'name': 'Metformin 500mg', 'category': 'Diabetes Care', 'price': 40, 'stock': 85},
        {'name': 'Insulin Injection', 'category': 'Diabetes Care', 'price': 250, 'stock': 50},
    ]
    
    for med_data in medicines_data:
        category = Category.objects.get(name=med_data['category'])
        medicine, created = Medicine.objects.get_or_create(
            name=med_data['name'],
            defaults={
                'category': category,
                'generic_name': med_data['name'],
                'manufacturer': 'Sample Pharma',
                'batch_number': f'BATCH{random.randint(1000, 9999)}',
                'purchase_price': med_data['price'] * 0.7,
                'selling_price': med_data['price'],
                'mrp': med_data['price'] * 1.2,
                'quantity': med_data['stock'],
                'reorder_level': 20,
                'expiry_date': timezone.now().date() + timedelta(days=365),
                'is_active': True,
            }
        )
    
    return JsonResponse({'success': True, 'message': 'Sample data generated successfully!'})

# ==================== ERROR HANDLERS ====================

def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)

# ==================== CONTEXT PROCESSORS ====================

def cart_count(request):
    """Context processor for cart count"""
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = cart.items.count()
    return {'cart_count': count}

def categories_nav(request):
    """Context processor for navigation categories"""
    categories = Category.objects.filter(
        medicines__is_active=True
    ).distinct()[:8]
    return {'nav_categories': categories}

# from .models import * 
# from .forms import (
#     UserRegistrationForm, CategoryForm,
#     MedicineForm, CustomerForm,
#     SaleForm, SaleItemForm, StockSearchForm
# )
# def index(request):
#     return render(request, 'store/home.html')
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.utils import timezone
# from datetime import timedelta
# from django.db.models import Sum

@login_required
def admin_dashboard(request):

    # Admin Dashboard
    if request.user.is_staff or request.user.is_superuser:

        total_medicines = Medicine.objects.count()
        low_stock_count = Medicine.objects.filter(quantity__lte=10).count()
        expired_count = Medicine.objects.filter(expiry_date__lt=timezone.now().date()).count()

        recent_sales = Sale.objects.order_by('-sale_date')[:10]
       

        sales_data = []
        for i in range(6, -1, -1):
            date = timezone.now().date() - timedelta(days=i)

            daily_sales = Sale.objects.filter(
                sale_date__date=date,
                status='COM'
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            sales_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'total': float(daily_sales)
            })

        context = {
            'total_medicines': total_medicines,
            'low_stock_count': low_stock_count,
            'expired_count': expired_count,
            'recent_sales': recent_sales,
            'sales_data': sales_data,
        }

        return render(request, 'store/dashboard.html', context)

    # Customer Home Page
    return render(request, 'store/home.html')

# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Registration successful!')
#             return redirect('/dashboard')
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'store/register.html', {'form': form})

# def user_login(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")

#         user = authenticate(request, username=username, password=password)

#         if user is not None:
#             login(request, user)
#             messages.success(request, "Login Successful")
#             return redirect("/dashboard")
#         else:
#             messages.error(request, "Invalid Username or Password")

#     return render(request, "store/login.html")

# @login_required
# def user_logout(request):
#     logout(request)
#     messages.info(request, 'Logged out successfully.')
#     return redirect('/')

# # Category Views
# @login_required
# def category_list(request):
#     categories = Category.objects.all()
#     return render(request, 'store/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('store:category_list')
    else:
        form = CategoryForm()
    return render(request, 'store/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('store:category_list')

    else:
        form = CategoryForm(instance=category)
    return render(request, 'store/category_form.html', {'form': form, 'title': 'Update Category'})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('store:category_list')

    return render(request, 'store/category_confirm_delete.html', {'object': category})

# # Medicine Views
# @login_required
# def medicine_list(request):
#     search_query = request.GET.get('search', '')
#     category_id = request.GET.get('category', '')
    
#     medicines = Medicine.objects.select_related('category', 'supplier')
    
#     if search_query:
#         medicines = medicines.filter(
#             Q(name__icontains=search_query) |
#             Q(generic_name__icontains=search_query) |
#             Q(batch_number__icontains=search_query)
#         )
    
#     if category_id:
#         medicines = medicines.filter(category_id=category_id)
    
#     categories = Category.objects.all()
    
#     return render(request, 'store/medicine_list.html', {
#         'medicines': medicines,
#         'categories': categories,
#         'search_query': search_query,
#         'selected_category': category_id
#     })

@login_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        if form.is_valid():
            medicine = form.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'store/medicine_form.html', {'form': form, 'title': 'Add Medicine'})

@login_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'store/medicine_form.html', {'form': form, 'title': 'Update Medicine'})

# @login_required
# def medicine_detail(request, pk):
#     medicine = get_object_or_404(Medicine, pk=pk)
#     stock_movements = medicine.stock_movements.order_by('-created_at')[:20]
#     return render(request, 'store/medicine_detail.html', {
#         'medicine': medicine,
#         'stock_movements': stock_movements
#     })

@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('medicine_list')
    return render(request, 'store/medicine_confirm_delete.html', {'object': medicine})

# Customer Views
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'store/customer_list.html', {'customers': customers})

@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'store/customer_form.html', {'form': form, 'title': 'Add Customer'})

@login_required
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'store/customer_form.html', {'form': form, 'title': 'Update Customer'})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customer_list')
    return render(request, 'store/customer_confirm_delete.html', {'object': customer})


# Sale Views
@login_required
def sale_list(request):
    sales = Sale.objects.select_related('customer').order_by('-sale_date')
    return render(request, 'store/sale_list.html', {'sales': sales})

@login_required
def sale_create(request):
    if request.method == 'POST':
        sale_form = SaleForm(request.POST)
        if sale_form.is_valid():
            sale = sale_form.save(commit=False)
            sale.total_amount = Decimal('0.00')
            sale.save()
            
            # Process items from JSON
            items_data = request.POST.get('items_data')
            if items_data:
                items = json.loads(items_data)
                total = Decimal('0.00')
                for item in items:
                    medicine = Medicine.objects.get(id=item['medicine'])
                    quantity = int(item['quantity'])
                    selling_price = Decimal(item['selling_price'])
                    discount = Decimal(item.get('discount', 0))
                    
                    if medicine.quantity < quantity:
                        messages.error(request, f'Insufficient stock for {medicine.name}')
                        sale.delete()
                        return redirect('sale_create')
                    
                    SaleItem.objects.create(
                        sale=sale,
                        medicine=medicine,
                        quantity=quantity,
                        selling_price=selling_price,
                        discount=discount,
                        total=(quantity * selling_price) - discount
                    )
                    
                    # Update medicine stock
                    medicine.quantity -= quantity
                    medicine.save()
                    
                    total += (quantity * selling_price) - discount
                
                sale.total_amount = total
                sale.save()
                
                messages.success(request, 'Sale completed successfully!')
                return redirect('sale_list')
    else:
        sale_form = SaleForm()
    
    medicines = Medicine.objects.filter(is_active=True, quantity__gt=0)
    customers = Customer.objects.all()
    return render(request, 'store/sale_create.html', {
        'sale_form': sale_form,
        'medicines': medicines,
        'customers': customers
    })

@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'store/sale_detail.html', {'sale': sale})

@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        # Reverse stock movements
        for item in sale.items.all():
            medicine = item.medicine
            medicine.quantity += item.quantity
            medicine.save()
        sale.delete()
        messages.success(request, 'Sale deleted successfully!')
        return redirect('sale_list')
    return render(request, 'store/sale_confirm_delete.html', {'object': sale})

# Inventory Management Views
@login_required
def inventory_dashboard(request):
    total_medicines = Medicine.objects.count()
    total_value = Medicine.objects.aggregate(
        total=Sum('quantity', field='quantity * selling_price')
    )['total'] or 0
    
    low_stock = Medicine.objects.filter(quantity__lte=10)
    expired = Medicine.objects.filter(expiry_date__lt=timezone.now().date())
    expiring_soon = Medicine.objects.filter(
        expiry_date__gte=timezone.now().date(),
        expiry_date__lte=timezone.now().date() + timedelta(days=30)
    )
    
    context = {
        'total_medicines': total_medicines,
        'total_value': total_value,
        'low_stock': low_stock,
        'expired': expired,
        'expiring_soon': expiring_soon,
        'low_stock_count': low_stock.count(),
        'expired_count': expired.count(),
        'expiring_soon_count': expiring_soon.count(),
    }
    return render(request, 'store/inventory_dashboard.html', context)

# @login_required
# def inventory_medicine_search(request):
#     form = StockSearchForm(request.GET)
#     medicines = Medicine.objects.select_related('category', 'supplier')
    
#     if form.is_valid():
#         if form.cleaned_data.get('medicine'):
#             medicines = medicines.filter(id=form.cleaned_data['medicine'].id)
#         if form.cleaned_data.get('category'):
#             medicines = medicines.filter(category=form.cleaned_data['category'])
#         if form.cleaned_data.get('expiry_before'):
#             medicines = medicines.filter(expiry_date__lte=form.cleaned_data['expiry_before'])
#         if form.cleaned_data.get('expiry_after'):
#             medicines = medicines.filter(expiry_date__gte=form.cleaned_data['expiry_after'])
#         if form.cleaned_data.get('low_stock'):
#             medicines = medicines.filter(quantity__lte=10)
    
#     return render(request, 'store/inventory_search.html', {
#         'form': form,
#         'medicines': medicines
#     })

@login_required
def medicine_stock_movement(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    movements = medicine.stock_movements.order_by('-created_at')
    return render(request, 'store/medicine_stock_movement.html', {
        'medicine': medicine,
        'movements': movements
    })


# API Views for dynamic form handling
@login_required
def get_medicine_details(request):
    medicine_id = request.GET.get('medicine_id')
    if medicine_id:
        medicine = get_object_or_404(Medicine, id=medicine_id)
        data = {
            'name': medicine.name,
            'selling_price': float(medicine.selling_price),
            'purchase_price': float(medicine.purchase_price),
            'quantity': medicine.quantity,
            'batch_number': medicine.batch_number,
            'expiry_date': medicine.expiry_date.strftime('%Y-%m-%d') if medicine.expiry_date else None
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Medicine not found'}, status=404)

# Add these views to store/views.py

@login_required
def admin_order_management(request):

    
    # Get all orders
    orders = Order.objects.all().order_by('-order_date')
    
    # Filters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        orders = orders.filter(order_status=status_filter)
    
    if date_filter:
        orders = orders.filter(order_date__date=date_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query)
        )
    
    # Statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status='PEN').count()
    processing_orders = Order.objects.filter(order_status='PRO').count()
    shipped_orders = Order.objects.filter(order_status='SHP').count()
    delivered_orders = Order.objects.filter(order_status='DEL').count()
    cancelled_orders = Order.objects.filter(order_status='CAN').count()
    
    # Recent orders
    recent_orders = orders[:10]
    
    context = {
        'orders': orders,
        'recent_orders': recent_orders,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        'status_choices': Order.STATUS_CHOICES,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
    }
    return render(request, 'store/admin_order_management.html', context)

# @login_required
# def admin_order_detail(request, order_id):
#     """Admin view for order details with management options"""
#     if not request.user.is_staff:
#         messages.error(request, 'You do not have permission to view this page.')
#         return redirect('store:home')
    
#     order = get_object_or_404(Order, id=order_id)
#     items = order.items.all()
    
#     if request.method == 'POST':
#         action = request.POST.get('action')
        
#         if action == 'update_status':
#             new_status = request.POST.get('order_status')
#             if new_status in dict(Order.STATUS_CHOICES):
#                 old_status = order.order_status
#                 order.order_status = new_status
                
#                 # If delivered, set delivered date
#                 if new_status == 'DEL' and not order.delivered_date:
#                     order.delivered_date = timezone.now()
                
#                 order.save()
                
#                 # Create status history
#                 OrderStatusHistory.objects.create(
#                     order=order,
#                     status=new_status,
#                     note=f"Status changed from {dict(Order.STATUS_CHOICES)[old_status]} to {dict(Order.STATUS_CHOICES)[new_status]}",
#                     changed_by=request.user
#                 )
                
#                 messages.success(request, f'Order #{order.order_number} status updated to {dict(Order.STATUS_CHOICES)[new_status]}')
#                 return redirect('store:admin_order_detail', order_id=order.id)
        
#         elif action == 'cancel_order':
#             if order.order_status in ['PEN', 'PRO']:
#                 order.order_status = 'CAN'
#                 order.save()
                
#                 # Restore stock
#                 for item in order.items.all():
#                     medicine = item.medicine
#                     medicine.quantity += item.quantity
#                     medicine.save()
                
#                 # Create cancellation record
#                 OrderStatusHistory.objects.create(
#                     order=order,
#                     status='CAN',
#                     note=f"Order cancelled by admin: {request.POST.get('cancellation_reason', 'No reason provided')}",
#                     changed_by=request.user
#                 )
                
#                 messages.success(request, f'Order #{order.order_number} has been cancelled successfully.')
#                 return redirect('store:admin_order_management')
        
#         elif action == 'update_payment':
#             payment_status = request.POST.get('payment_status')
#             if payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
#                 order.payment_status = payment_status
#                 order.save()
                
#                 OrderStatusHistory.objects.create(
#                     order=order,
#                     status=order.order_status,
#                     note=f"Payment status updated to {dict(Order.PAYMENT_STATUS_CHOICES)[payment_status]}",
#                     changed_by=request.user
#                 )
                
#                 messages.success(request, f'Payment status updated successfully.')
#                 return redirect('store:admin_order_detail', order_id=order.id)
        
#         elif action == 'add_note':
#             note = request.POST.get('note', '')
#             if note:
#                 OrderStatusHistory.objects.create(
#                     order=order,
#                     status=order.order_status,
#                     note=note,
#                     changed_by=request.user
#                 )
#                 messages.success(request, 'Note added successfully.')
#                 return redirect('store:admin_order_detail', order_id=order.id)
    
#     # Get status history
#     status_history = OrderStatusHistory.objects.filter(order=order).order_by('-created_at')
    
#     context = {
#         'order': order,
#         'items': items,
#         'status_history': status_history,
#         'status_choices': Order.STATUS_CHOICES,
#         'payment_choices': Order.PAYMENT_STATUS_CHOICES,
#     }
#     return render(request, 'store/admin_order_detail.html', context)

@login_required
def admin_bulk_order_action(request):
    """Bulk action for orders"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if request.method == 'POST':
        action = request.POST.get('action')
        order_ids = request.POST.getlist('order_ids[]')
        
        if not order_ids:
            return JsonResponse({'success': False, 'error': 'No orders selected'})
        
        orders = Order.objects.filter(id__in=order_ids)
        
        if action == 'cancel':
            for order in orders:
                if order.order_status in ['PEN', 'PRO']:
                    order.order_status = 'CAN'
                    order.save()
                    
                    # Restore stock
                    for item in order.items.all():
                        medicine = item.medicine
                        medicine.quantity += item.quantity
                        medicine.save()
                    
                    OrderStatusHistory.objects.create(
                        order=order,
                        status='CAN',
                        note=f"Bulk cancellation by admin",
                        changed_by=request.user
                    )
            
            return JsonResponse({'success': True, 'message': f'{orders.count()} orders cancelled'})
        
        elif action == 'delete':
            orders.delete()
            return JsonResponse({'success': True, 'message': f'{orders.count()} orders deleted'})
        
        elif action == 'update_status':
            status = request.POST.get('status')
            if status in dict(Order.STATUS_CHOICES):
                for order in orders:
                    order.order_status = status
                    order.save()
                    
                    OrderStatusHistory.objects.create(
                        order=order,
                        status=status,
                        note=f"Bulk status update to {dict(Order.STATUS_CHOICES)[status]}",
                        changed_by=request.user
                    )
                
                return JsonResponse({'success': True, 'message': f'{orders.count()} orders updated'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def admin_order_invoice(request, order_id):
    """Generate invoice for order"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('store:home')
    
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'store/admin_order_invoice.html', context)

@login_required
def admin_order_export(request):
    """Export orders to CSV"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Order #', 'Customer', 'Email', 'Phone', 'Total Amount', 
        'Status', 'Payment Status', 'Order Date', 'Delivered Date'
    ])
    
    orders = Order.objects.all()
    for order in orders:
        writer.writerow([
            order.order_number,
            order.customer_name,
            order.customer_email,
            order.customer_phone,
            order.grand_total,
            order.get_order_status_display(),
            order.get_payment_status_display(),
            order.order_date.strftime('%Y-%m-%d %H:%M'),
            order.delivered_date.strftime('%Y-%m-%d %H:%M') if order.delivered_date else ''
        ])
    
    return response