from django.db import migrations
from decimal import Decimal


def create_test_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Wallet = apps.get_model('transactions', 'Wallet')

    # Технический кошелёк admin
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'is_staff': True, 'is_superuser': False}
    )
    Wallet.objects.get_or_create(
        user=admin_user,
        defaults={'balance': Decimal('0.00')}
    )

    # Тестовые пользователи
    test_users = ['alice', 'bob', 'charlie']
    for username in test_users:
        user, created = User.objects.get_or_create(username=username)
        wallet, _ = Wallet.objects.get_or_create(user=user)

        # Даём Alice 5000 u. только один раз
        if username == 'alice' and wallet.balance == Decimal('0.00'):
            wallet.balance = Decimal('5000.00')
            wallet.save(update_fields=['balance'])


def reverse_test_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username__in=['admin', 'alice', 'bob', 'charlie']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),  # замените на вашу последнюю миграцию моделей
    ]

    operations = [
        migrations.RunPython(create_test_data, reverse_test_data),
    ]
