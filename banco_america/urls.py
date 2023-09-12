from django.urls import path
from . import views



app_name = 'banco_america'

urlpatterns = [
    path('', views.home, name='home'),
    path('client/', views.register_client, name='client'),
    path('download_password/<str:username>/<str:password>/', views.download_password, name='download_password'),
    path('login/', views.login_user, name='login'),
    path('login/<path:file_path>/<path:file_name>/', views.login_user, name='login_with_file'),
    path('profile/', views.profile, name='profile'),
    path('verify_account/<str:account_number>/', views.verify_account, name='verify_account'),
    path('transaction/<int:account_id>/<int:transaction_type_id>/', views.transaction, name='transaction'),
    path('deposit_cash', views.deposit_cash, name='deposit_cash'),
    path('withdraw_cash/', views.withdraw_cash, name='withdraw_cash'),
    path('teller/', views.teller, name='teller'), 
    path('success/', views.success, name='success'), 
    path('success_online/', views.success_online, name='success_online'),
    path('movements/', views.movements, name='movements'),
    path('movements_filter/', views.movements_filter, name='movements_filter'),
    path('transaction/', views.transaction, name='transaction'),
    path('verify_account_online/str<account_number>', views.verify_account_online, name='verify_account_online'),
    path('deposit_online/', views.deposit_online, name='deposit_online'),
    path('send-sms/', views.send_sms, name='send_sms'),

]
