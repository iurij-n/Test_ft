from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'user_id')
    list_filter = ('user__date_joined',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-balance',)
    list_editable = ('balance',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'amount', 'commission', 'total', 'timestamp', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('from_wallet__user__username', 'to_wallet__user__username')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)

    def from_user(self, obj):
        return obj.from_wallet.user.username
    from_user.short_description = 'От кого'

    def to_user(self, obj):
        return obj.to_wallet.user.username
    to_user.short_description = 'Кому'

    def total(self, obj):
        return obj.amount + obj.commission
    total.short_description = 'Итого списано'
