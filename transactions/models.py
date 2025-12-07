from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Wallet(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    def __str__(self):
        return f"Wallet {self.user.username} – {self.balance}"

    class Meta:
        db_table = 'wallets'


class Transaction(models.Model):
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
    )

    from_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='outgoing_transactions'
    )
    to_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='incoming_transactions'
    )
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2
    )
    commission = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='success'
    )

    class Meta:
        db_table = 'transactions'
        indexes = [models.Index(fields=['timestamp'])]
