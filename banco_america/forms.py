from django import forms
from banco_america.models import Client, Address, Account_type, Transaction, Transaction_type, Account
from phonenumber_field.formfields import PhoneNumberField

class CreateClientForm(forms.ModelForm):
    phone = PhoneNumberField(initial='+593', required=True)
    class Meta:
        model = Client
        fields = ('identification', 'first_name', 'last_name', 'email', 'phone')

        
class CreateAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('province', 'city', 'street_name', 'house_number', 'postal_code')

class Create_Account_typeForm(forms.ModelForm):        
        class Meta:
            model = Account_type
            fields = ['account_type']
            
class CreateTransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']
        
class CreateAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['account_number']
        
class Create_transaction_type_Form(forms.ModelForm):        
        class Meta:
            model = Transaction_type
            fields = ['transaction_name']
            
class DateFilterForm(forms.Form):
    search_date = forms.DateField(label="Search by Date", widget=forms.DateInput(attrs={'type': 'date'}))

