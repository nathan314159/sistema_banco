from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.

class Address(models.Model):
    province = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    street_name = models.CharField(max_length=50)
    house_number = models.CharField(max_length=20)
    postal_code = models.CharField(max_length=20)
  
  
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
    identification = models.CharField(max_length=15)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.EmailField()
    phone = PhoneNumberField()


    def create_user(self):
        username = f"{self.first_name[0]}{self.last_name.lower()}"
        return username
        
    def __str__(self):
        return f"Name: {self.first_name} {self.last_name} / Identification: {self.identification}"

class Account_type(models.Model):
    ACCOUNT_CHOICES = (
        ('checking', 'checking account'),
        ('savings', 'savings account'),
    )
    account_type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES)
    
    def __str__(self):
        return self.account_type

class Account(models.Model):
    
    account_type = models.ForeignKey(Account_type, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    
    def number_account(self):
        print(self.account_number)

    def __str__(self):
        return f'account_number: {self.account_number} client: {self.client}'

        
    @classmethod
    def generate_account_number(cls, user_id, account_type_name):
        # Get the account type instance based on the account_type_name
        try:
            account_type_instance = Account_type.objects.latest('id')
        except Account_type.DoesNotExist:
            raise ValueError(f"Account type '{account_type_name}' does not exist.")

        num_accounts_of_type = Account.objects.filter(account_type=account_type_instance).count()

        # Get the account type abbreviation (e.g., "checking" -> "CHK")
        account_type_abbreviation = account_type_instance.account_type[:3].upper()

        # Format the account number with leading zeros based on the number of digits in num_accounts_of_type
        numLen = len(str(num_accounts_of_type))
        a = "00000"[5 - numLen:] + str(num_accounts_of_type)

        # Include the user ID in the formatted account number
        user_id_str = str(user_id).zfill(3)  # Assuming user ID is numeric and should have 3 digits

        account_number = f"{account_type_abbreviation}{a}{user_id_str}"

        # Return the formatted account number
        return account_number
       
class Transaction_type(models.Model):
    TRANSACTION_CHOICES = (
        ('credit', 'credit'),
        ('debit', 'debit'),
    )
    transaction_name = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    
    def __str__(self):
        return f'{self.transaction_name}'

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.ForeignKey(Transaction_type, on_delete=models.CASCADE)
    transaction_number = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.amount}'
    
    def process_transaction(self):
        if self.transaction_type.name == 'Deposit':
            self.account.balance += self.amount
            self.account.save()
        elif self.transaction_type.name == 'Withdrawal':
            if self.account.balance >= self.amount:
                self.account.balance -= self.amount
                self.account.save()
            else:
                raise ValueError("Insufficient balance for withdrawal.")