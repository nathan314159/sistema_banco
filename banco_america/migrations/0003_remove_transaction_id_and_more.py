# Generated by Django 4.1.3 on 2023-08-01 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banco_america', '0002_alter_account_account_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='id',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_number',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
