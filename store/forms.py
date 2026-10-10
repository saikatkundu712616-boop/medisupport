from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Category,  Medicine, Customer, 
    Sale, SaleItem
)
from decimal import Decimal

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'category',  'medicine_type', 'generic_name',
            'manufacturer', 'composition',  'selling_price',
            'mrp', 'discount_percentage', 'quantity', 'reorder_level',
            'batch_number', 'expiry_date', 'description', 'image',
            'prescription_required', 'is_active'
        ]
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'date_of_birth']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'total_amount', 'paid_amount', 'discount', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class SaleItemForm(forms.Form):
    medicine = forms.ModelChoiceField(queryset=Medicine.objects.filter(is_active=True, quantity__gt=0))
    quantity = forms.IntegerField(min_value=1)
    selling_price = forms.DecimalField(max_digits=10, decimal_places=2)
    discount = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=0)

class StockSearchForm(forms.Form):
    medicine = forms.ModelChoiceField(queryset=Medicine.objects.all(), required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    expiry_before = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    expiry_after = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    low_stock = forms.BooleanField(required=False)
    from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Category, Medicine, Customer, CustomerOrder

# class UserRegistrationForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)
#     phone = forms.CharField(max_length=15, required=False)

#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'name', 'category', 'generic_name', 'manufacturer',
            'purchase_price', 'selling_price', 'mrp', 'quantity', 'reorder_level',
            'batch_number', 'expiry_date', 'description', 'image', 'is_active'
        ]
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = CustomerOrder
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'shipping_address', 'billing_address', 'notes'
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 4}),
            'billing_address': forms.Textarea(attrs={'rows': 4}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
from django import forms
from .models import UserAddress

class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            'address_type', 'address_label', 'name', 'phone',
            'alternate_phone', 'email', 'address_line1', 'address_line2',
            'landmark', 'city', 'state', 'pincode', 'country',
            'is_default', 'is_billing'
        ]
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-select'}),
            'address_label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Home, Office'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'address_line1': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'House/Flat, Building, Street'}),
            'address_line2': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Locality, Area (Optional)'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nearby landmark'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6-digit pincode'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode and (len(pincode) != 6 or not pincode.isdigit()):
            raise forms.ValidationError("Pincode must be 6 digits.")
        return pincode

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and (len(phone) != 10 or not phone.isdigit()):
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phone