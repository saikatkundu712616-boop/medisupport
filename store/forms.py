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