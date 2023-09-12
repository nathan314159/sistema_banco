from decimal import Decimal
from django.shortcuts import redirect, render
from django.urls import reverse
from banco_america.forms import *
from django.db import IntegrityError
from banco_america.models import Account, Client, Account_type, Account, Transaction_type, Transaction

from account.views import login
from django.http import HttpResponse, HttpResponseRedirect
import random 
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from urllib.parse import unquote
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from twilio.rest import Client as TwilioClient
from django.contrib.auth.models import User



# Create your views here.


def home(request):
    context = {}
    return render(request, 'registration/home.html', context)

def code_generator():
    x = random.randrange(10000000, 99999999)
    return str(x)

def send_code(username, password):
    file_path = os.path.join(settings.MEDIA_ROOT, f'{username}_password.pdf')
    print(f"File path: {file_path}")

    c = canvas.Canvas(file_path)
    c.setFont("Helvetica", 12)
    c.drawString(100, 700, f"The {username} randomly generated password: {password}")
    c.save()

def register_client(request):
    if request.method == "POST":
        form_client = CreateClientForm(request.POST)
        form_address = CreateAddressForm(request.POST)
        type_account_form = Create_Account_typeForm(request.POST)
        if form_client.is_valid() and form_address.is_valid() and type_account_form.is_valid:
            # Save the address instance
            address_instance = form_address.save()
            type_account_instance = type_account_form.save()

            try:
                # Create a User instance
                username = form_client.cleaned_data['first_name'][0].lower() + form_client.cleaned_data['last_name'].lower()
                password = code_generator()
                user_instance = User.objects.create_user(username=username, password=password)
                print('------ password',password)
                print('------ user_instance',user_instance)
                
                # Save the client instance
                client_instance = form_client.save(commit=False)
                client_instance.address = address_instance
                client_instance.user = user_instance
                client_instance.save()
                
                # Generate the account number
                print('------type_account_instance:',type_account_instance)
                user_id = user_instance.id
                account_number = Account().generate_account_number(user_id, type_account_instance.account_type)

                # Create the associated Account instance and link it to the Client
                account_instance = Account.objects.create(
                    account_type=type_account_instance,
                    client=client_instance,
                    account_number=account_number,
                )
                
                print('------account_instance:',account_instance)
                
                # Assign the account_instance to the account attribute of the Client
                client_instance.account = account_instance
                client_instance.save()

                # Generate password document
                file_path, file_name = download_password(request, client_instance, password)
                print('++++> file_path: ', file_path)
                print('++++> file_name: ', file_name)


                return HttpResponseRedirect(file_name )

            except IntegrityError:
                return HttpResponse("Username already exists. Please choose a different username.")
        
        else:
            print(form_client.errors)

    else:
        form_client = CreateClientForm()
        form_address = CreateAddressForm()
        type_account_form = Create_Account_typeForm()

    context = {
        'form_client': form_client,
        'form_address': form_address,
        'type_account_form' : type_account_form,
    }

    return render(request, 'registration/register_client.html', context)

def download_password(request, client_instance, password):
    username = client_instance.user.username
    file_name = f"{username}_password.pdf"
    print('-----file_name: ', file_name)    

    save_directory = r'C:\django_projects\bank_management_system_arboleda\centralBank\media'  # Replace with the actual path
    file_path = os.path.join(save_directory, file_name)
    print('OJO-----file_path: ', file_path, file_name)
    
    # Create the directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)
    
    pdf = canvas.Canvas(file_path)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 700, f"Your username is: {username} and your randomly generated password is: {password}")
    pdf.save()
    
    
    print('OJO-----file_path: ', file_path, ' ..', file_name)
    file_name = reverse('banco_america:login_with_file', kwargs={'file_path': file_path, 'file_name': file_name})
    print('OJO-----file_path: ', file_path, ' ..', file_name)
    return file_path, file_name

def login_user(request, *args, **kwargs):
    file_path = kwargs.get('file_path')
    file_url = kwargs.get('file_name')
    if file_path is not None and file_url is not None:
        file_url = settings.MEDIA_URL + file_url
        print('OJO ---> file_url:', file_url)

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                
                if file_path and file_url:
                    decoded_file_path = unquote(file_path)
                    decoded_file_url = unquote(file_url)
                    print("File path:", decoded_file_path)
                    print("File URL:", decoded_file_url)
                    
            
                if username == 'teller1':
                    return redirect('banco_america:teller')
                else:
                    return redirect('banco_america:profile')

            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    context = {'form': form, 'file_path': file_path, 'file_url': file_url}
    return render(request, 'registration/login.html', context)

@login_required
def profile(request):
    transactionForm = CreateTransactionForm()
    accountForm = CreateAccountForm()

    
    current_user = request.user
    client1 = Client.objects.get(user=current_user)
    account = Account.objects.get(client=client1)

    print('==== user: ', current_user)
    print('==== client: ', client1)
    print('==== account: ', account)
    
    context = {
        'current_user': current_user,
        'client': client1,
        'account': account,
        'transactionForm': transactionForm,
        'accountForm': accountForm,

    }
    
    return render(request, 'bankAccount/profile.html', context)

def transaction(request, account_id, transaction_type_id):
    print("=----> account_id: ", account_id)
    print("=----> transaction_type_id: ", transaction_type_id)
    
    if request.method == 'POST':
        transaction_type_name = request.POST.get('transaction_name')
        amount = request.POST.get('amount')
        description = request.POST.get('description')

        # Assuming you have the account object based on the provided account_id
        account = Account.objects.get(id=account_id)

        # Create a new transaction record with the provided information
        Transaction.objects.create(
            account=account,
            transaction_type=transaction_type_name,
            amount=amount,
            description=description
        )

        # Redirect to a success page or some other appropriate view
        return redirect('success_page')

    # If the form is not submitted, render the transaction template
    context = {
        'account_id': account_id,
        'transaction_type_id': transaction_type_id,
    }
    return render(request, 'bankAccount/transaction.html', context)

def movement(request):
    context = {}
    return render(request, 'bankAccount/movement.html', context)

def verify_account(request, account_number):
    account_exists = False
    amount = None

    print('=== verify_account POST ===')
    print('=%=%=%= account_number sent:', account_number)
    print('=%=%=%= account_number: ', account_number)
    
    try:
        account = Account.objects.get(account_number=account_number)
        print('=-=-=-- account: ', account)
        account_exists = True  

        request.session['verified_account_number'] = account_number
  
        request.session.save()
    except Account.DoesNotExist:
        pass  
    
    context = {
        'account_exists': account_exists,
        'account_number':account_number,
        # 'account_number_form': account_number_form,
    }
    return render(request, 'bankAccount/teller.html', context)


@login_required    
def teller(request):
    print("----> Inside teller view <----")
    account_number = None  

    
    if request.method == 'POST':
        account_form = CreateAccountForm(request.POST)
        if account_form.is_valid():
            account_number = account_form.cleaned_data['account_number']
            return verify_account(request, account_number)
    else:
        account_form = CreateAccountForm()
    
    context = {
        'account_form': account_form,
        'account_number': account_number,  

    }

    return render(request, 'bankAccount/teller.html', context)


# deposit cash
def create_transaction_credit(account, amount, credit_transaction_type):
    print('=== create_transaction_credit POST ===')
    transaction_type = Transaction_type.objects.get(transaction_name='credit')
    print('=== verify_account POST ===', transaction_type)
    transaction = Transaction.objects.create(
        account=account,
        transaction_type=transaction_type,
        amount=amount,
    )

    account.balance += amount
    account.save()

def deposit_cash(request):
    account_number_form = CreateAccountForm()
    verified_account_number = request.session.get('verified_account_number')
    amount_form = CreateTransactionForm(request.POST)  # Define it here

    if verified_account_number:
        account_number_form = CreateAccountForm(initial={'account_number': verified_account_number})

    if request.method == 'POST':
        account_number = request.POST.get('account_number')
        amount_form = CreateTransactionForm(request.POST)  

        if verify_account(request, account_number):  # FUNCTION verify_account
            amount = get_valid_amount(amount_form)

            if amount is not None:
                credit_transaction_type = get_credit_transaction_type() # FUNCTION credit_transaction_type

                if credit_transaction_type is not None:
                    account = get_account(request)   # FUNCTION get_account
                    print(f"###---> Account: {account}")

                    if account is not None:
                        create_transaction_credit(account, amount, credit_transaction_type)
                        return redirect('banco_america:success')
                    else:
                        print("###---> Account not found.")
                        return HttpResponse("Account not found.")
                else:
                    return HttpResponse("Credit transaction type not available.")
            else:
                return HttpResponse("Invalid amount.")
        else:
            return HttpResponse("Account verification failed.")

    context = {
        'account_number_form': account_number_form,
        'amount_form': amount_form,
    }

    return render(request, 'bankAccount/deposit.html', context)

def get_valid_amount(amount_form):
    print("==== Inside get_valid_amount ====")
    if amount_form.is_valid():
        amount = amount_form.cleaned_data['amount']
        print("====>> Amount: ", amount)
        return amount
    print("====>> Form errors: ", amount_form.errors)
    return None


def get_credit_transaction_type():
    try:
        return Transaction_type.objects.get(transaction_name='credit')
    except Transaction_type.DoesNotExist:
        return Transaction_type.objects.create(transaction_name='credit')

def get_account(request):
    try:
        verified_account_number = request.session.get('verified_account_number')
        return Account.objects.get(account_number=verified_account_number)
    except Account.DoesNotExist:
        return None


# withdraw cash
def create_transaction_debit(account, amount, credit_transaction_type):
    print('=== create_transaction_debit POST ===')
    transaction_type = Transaction_type.objects.get(transaction_name='debit')
    print('=== verify_account POST ===', transaction_type)
    transaction = Transaction.objects.create(
        account=account,
        transaction_type=transaction_type,
        amount=amount,
    )

    account.balance -= amount
    account.save()

def withdraw_cash(request):
    account_number_form, verified_account_number, amount_form = prepare_forms(request)

    print(f"Request Method: {request.method}")

    if request.method == 'POST':
        account_number = request.POST.get('account_number')
        amount_form = CreateTransactionForm(request.POST)

        if amount_form.is_valid():  # Validate the form first
            print(f"POST request - Account Number: {account_number}")
            print(f"POST request - Amount Form: {amount_form.cleaned_data['amount']}")

            if verify_account(request, account_number):
                amount = get_valid_amount(amount_form)
                account = get_account(request)

                print(f"Verified Account: {account}")
                print(f"Withdrawal Amount: {amount}")

                validation_message = validate_withdrawal(account.account_type, amount, account.balance)
                if validation_message == "Validation passed":
                    perform_withdrawal(account, amount)
                    print("Withdrawal successful")
                    
                    # Send an SMS to notify the user <---------
                    send_sms(request) 
                    return redirect('banco_america:success')
                else:
                    print(f"Withdrawal validation failed. Reason: {validation_message}")
                    return HttpResponse(f"Withdrawal validation failed. Reason: {validation_message}")
            else:
                print("Account verification failed.")
        else:
            print("Amount form is not valid.")
    else:
        print("Method is not POST.")

    context = {
        'account_number_form': account_number_form,
        'amount_form': amount_form,
    }

    return render(request, 'bankAccount/withdraw.html', context)

def prepare_forms(request):
    
    account_number_form = CreateAccountForm()
    verified_account_number = request.session.get('verified_account_number')
    amount_form = CreateTransactionForm()

    if verified_account_number:
        account_number_form = CreateAccountForm(initial={'account_number': verified_account_number})

    return account_number_form, verified_account_number, amount_form

def validate_withdrawal(account_type, amount, balance):
    print("---validate_withdrawal function---")
    print(f"Account Type: {account_type.account_type}, Amount: {amount}, Balance: {balance}")

    if account_type.account_type == 'savings':
        if amount > 100:
            return "Withdrawal amount exceeds limit for Savings account"
        elif balance < amount:
            return "Insufficient account balance for withdrawal."
    
    elif account_type.account_type == 'checking':
        if amount > 500:
            return "Withdrawal amount exceeds limit for Checking account"
        elif balance - amount < 0:
            return "Insufficient account balance for withdrawal."

    return "Validation passed"

def get_debit_transaction_type():
    # Implement the logic to retrieve or create a debit transaction type
    # For example:
    transaction_type, created = Transaction_type.objects.get_or_create(transaction_name='debit')
    return transaction_type

def perform_withdrawal(account, amount):
    debit_transaction_type = get_debit_transaction_type()  # Get the debit transaction type
    create_transaction_debit(account, amount, debit_transaction_type)
    print("###---> Withdraw Transaction created and account updated.")


# render personal info in success page
def get_user_info(account_number):
    try:
        # Retrieve the account based on the provided account number
        account = Account.objects.get(account_number=account_number)
        
        # Get the associated client information
        client = account.client
        user = client.user
        
        
        # Retrieve user information
        name = client.first_name
        last_name = client.last_name
        email = user.email
        account_number = account.account_number
        account_balance = account.balance
        
        return name, email, account_balance, last_name, account_number
    except Account.DoesNotExist:
        return None, None, None

def success(request):
    account_number = request.session.get('verified_account_number')
    
    amount = request.session.get('amount')

    name, email, account_balance, last_name, account_number = get_user_info(account_number)
    
    
    
    context = {
        'name': name,
        'email': email,
        'account_balance': account_balance,
        'last_name': last_name,
        'account_number':account_number,
        'amount':amount
    }
    return render(request, 'messages/success.html', context)

def success_online(request):
    account_number = request.session.get('verified_account_number')
    
    name, email, account_balance, last_name, account_number = get_user_info(account_number)
    
    context = {
        'name': name,
        'email': email,
        'account_balance': account_balance,
        'last_name': last_name,
        'account_number':account_number
    }
    return render(request, 'messages/success_online.html', context)

# movements
def movements(request):
    
    context = movements_filter(request)
    
    return render(request, 'movements/movements.html', context)

def movements_filter(request):
    user = request.user
    account = Account.objects.get(client=user.client)
    
    search_form = DateFilterForm(request.GET)
    transactions = Transaction.objects.filter(account=account)  # Initial queryset
    
    if search_form.is_valid():
        search_date = search_form.cleaned_data['search_date']
        transactions = transactions.filter(date__date=search_date)
    
    context = {
        'user': user,
        'account': account,
        'transactions': transactions,
        'search_form': search_form,
    }

    return context


# transaction
   
def transaction(request):
    print("----> Inside transaction <----")
    account_number = None  

    if request.method == 'POST':
        account_form = CreateAccountForm(request.POST)
        if account_form.is_valid():
            account_number = account_form.cleaned_data['account_number']
            print('----..>> account_number: ', account_number)
            return verify_account_online(request, account_number)
    else:
        account_form = CreateAccountForm()
    
    context = {
        'account_form': account_form,
        'account_number': account_number,  
    }

    return render(request, 'transaction/transaction.html', context)

def verify_account_online(request, account_number):
    account_exists = False


    print('=== verify_account POST ===')
    print('=%=%=%= account_number sent:', account_number)
    print('=%=%=%= account_number: ', account_number)
    try:
        account = Account.objects.get(account_number=account_number)
        print('=-=-=-- account: ', account)
        account_exists = True  
        request.session['verified_account_number'] = account_number
        request.session.save()
    except Account.DoesNotExist:
        pass  
    
    context = {
        'account_exists': account_exists,
        'account_number':account_number,
        # 'account_number_form': account_number_form,
    }
    return render(request, 'transaction/transaction.html', context)

def deposit_online(request):
    account_number_form = CreateAccountForm()
    verified_account_number = request.session.get('verified_account_number')
    amount_form = CreateTransactionForm(request.POST)

    user = request.user
    client = Client.objects.get(user=user)
    account_user = Account.objects.get(client=client)

    if verified_account_number:
        account_number_form = CreateAccountForm(initial={'account_number': verified_account_number})

    if request.method == 'POST':
        account_number = request.POST.get('account_number')
        amount_form = CreateTransactionForm(request.POST)

        if verify_account_online(request, account_number):
            amount = get_valid_amount(amount_form)

            if amount is not None:
                credit_transaction_type = get_credit_transaction_type()
                validation_message = validate_user_money(account_user.account_type.account_type, amount, account_user.balance)
                
                if validation_message == "Validation passed":
                    account = get_account(request)

                    if account is not None:
                        create_transaction_credit(account, amount, credit_transaction_type)
                        debit_account(account_user, amount)
                        return redirect('banco_america:success_online')
                    else:
                        print("###---> Account not found.")
                        return HttpResponse("Account not found.")
                else:
                    return HttpResponse(validation_message)
            else:
                return HttpResponse("Invalid amount.")
        else:
            return HttpResponse("Account verification failed.")

    context = {
        'account_number_form': account_number_form,
        'amount_form': amount_form,
    }

    return render(request, 'transaction/deposit_online.html', context)



def debit_account(account_user, amount):
    debit_transaction_type = get_debit_transaction_type()
    if debit_transaction_type is not None:
        create_transaction_debit(account_user, amount, debit_transaction_type)
        return True
    else:
        return False

def validate_user_money(account_type, withdrawal_amount, balance):
    print("---validate_withdrawal_user_provided function---")
    print(f"Account Type: {account_type}, Withdrawal Amount: {withdrawal_amount}, Balance: {balance}")

    if account_type == 'savings':
        if withdrawal_amount > 100:
            return "Withdrawal amount exceeds limit for Savings account"
        elif balance < withdrawal_amount:
            return "Insufficient account balance for withdrawal."
    
    elif account_type == 'checking':
        if withdrawal_amount > 500:
            return "Withdrawal amount exceeds limit for Checking account"
        elif balance - withdrawal_amount < 0:
            return "Insufficient account balance for withdrawal."

    return "Validation passed"


# sms

def send_sms(request):
    # Get the account number from the session or some other source
    verified_account_number = request.session.get('verified_account_number')
    
    # Check if the account number is valid, you can use get_object_or_404 for this
    account = get_object_or_404(Account, account_number=verified_account_number)
    
    # Retrieve client information associated with the account
    client_user = account.client
    
    # Get necessary information from the client and account
    first_name = client_user.first_name
    print("##@@!!--> first_name: ", first_name)
    phone_number = client_user.phone
    print("##@@!!--> phone_number: ", phone_number)
    withdrawal_balance = account.balance
    print("##@@!!--> withdrawal_balance: ", withdrawal_balance)

    withdrawal_amount = withdrawal_balance  # Replace with the actual withdrawal amount
    recipient_phone_number = str(phone_number)  # "+593998098630"
    print("##@@!!--> recipient_phone_number: ", recipient_phone_number)
    message_body = f"Hello! ${first_name} You've withdrawn ${withdrawal_amount} from your account."
    
    # Initialize the Twilio client
    client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Send an SMS
    message = client.messages.create(
        body=message_body,
        from_=settings.TWILIO_PHONE_NUMBER,  # Your Twilio phone number
        to=recipient_phone_number
    )

    # Handle the response, log, or return a success message as needed

    return HttpResponse("SMS sent!")





