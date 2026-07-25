
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import * 
from .forms import (
    UserRegistrationForm, CategoryForm,
    MedicineForm, CustomerForm,
    SaleForm, SaleItemForm, StockSearchForm
)
def index(request):
    return render(request, 'store/home.html')
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

@login_required
def home(request):

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

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful")
            return redirect("/home")
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, "store/login.html")

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('/')

# Category Views
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'store/category_list.html', {'categories': categories})

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

# Medicine Views
@login_required
def medicine_list(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    
    medicines = Medicine.objects.select_related('category', 'supplier')
    
    if search_query:
        medicines = medicines.filter(
            Q(name__icontains=search_query) |
            Q(generic_name__icontains=search_query) |
            Q(batch_number__icontains=search_query)
        )
    
    if category_id:
        medicines = medicines.filter(category_id=category_id)
    
    categories = Category.objects.all()
    
    return render(request, 'store/medicine_list.html', {
        'medicines': medicines,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id
    })

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

@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    stock_movements = medicine.stock_movements.order_by('-created_at')[:20]
    return render(request, 'store/medicine_detail.html', {
        'medicine': medicine,
        'stock_movements': stock_movements
    })

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

@login_required
def inventory_medicine_search(request):
    form = StockSearchForm(request.GET)
    medicines = Medicine.objects.select_related('category', 'supplier')
    
    if form.is_valid():
        if form.cleaned_data.get('medicine'):
            medicines = medicines.filter(id=form.cleaned_data['medicine'].id)
        if form.cleaned_data.get('category'):
            medicines = medicines.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('expiry_before'):
            medicines = medicines.filter(expiry_date__lte=form.cleaned_data['expiry_before'])
        if form.cleaned_data.get('expiry_after'):
            medicines = medicines.filter(expiry_date__gte=form.cleaned_data['expiry_after'])
        if form.cleaned_data.get('low_stock'):
            medicines = medicines.filter(quantity__lte=10)
    
    return render(request, 'store/inventory_search.html', {
        'form': form,
        'medicines': medicines
    })

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

@login_required
def admin_order_detail(request, order_id):
    """Admin view for order details with management options"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('store:home')
    
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('order_status')
            if new_status in dict(Order.STATUS_CHOICES):
                old_status = order.order_status
                order.order_status = new_status
                
                # If delivered, set delivered date
                if new_status == 'DEL' and not order.delivered_date:
                    order.delivered_date = timezone.now()
                
                order.save()
                
                # Create status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status=new_status,
                    note=f"Status changed from {dict(Order.STATUS_CHOICES)[old_status]} to {dict(Order.STATUS_CHOICES)[new_status]}",
                    changed_by=request.user
                )
                
                messages.success(request, f'Order #{order.order_number} status updated to {dict(Order.STATUS_CHOICES)[new_status]}')
                return redirect('store:admin_order_detail', order_id=order.id)
        
        elif action == 'cancel_order':
            if order.order_status in ['PEN', 'PRO']:
                order.order_status = 'CAN'
                order.save()
                
                # Restore stock
                for item in order.items.all():
                    medicine = item.medicine
                    medicine.quantity += item.quantity
                    medicine.save()
                
                # Create cancellation record
                OrderStatusHistory.objects.create(
                    order=order,
                    status='CAN',
                    note=f"Order cancelled by admin: {request.POST.get('cancellation_reason', 'No reason provided')}",
                    changed_by=request.user
                )
                
                messages.success(request, f'Order #{order.order_number} has been cancelled successfully.')
                return redirect('store:admin_order_management')
        
        elif action == 'update_payment':
            payment_status = request.POST.get('payment_status')
            if payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
                order.payment_status = payment_status
                order.save()
                
                OrderStatusHistory.objects.create(
                    order=order,
                    status=order.order_status,
                    note=f"Payment status updated to {dict(Order.PAYMENT_STATUS_CHOICES)[payment_status]}",
                    changed_by=request.user
                )
                
                messages.success(request, f'Payment status updated successfully.')
                return redirect('store:admin_order_detail', order_id=order.id)
        
        elif action == 'add_note':
            note = request.POST.get('note', '')
            if note:
                OrderStatusHistory.objects.create(
                    order=order,
                    status=order.order_status,
                    note=note,
                    changed_by=request.user
                )
                messages.success(request, 'Note added successfully.')
                return redirect('store:admin_order_detail', order_id=order.id)
    
    # Get status history
    status_history = OrderStatusHistory.objects.filter(order=order).order_by('-created_at')
    
    context = {
        'order': order,
        'items': items,
        'status_history': status_history,
        'status_choices': Order.STATUS_CHOICES,
        'payment_choices': Order.PAYMENT_STATUS_CHOICES,
    }
    return render(request, 'store/admin_order_detail.html', context)

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