from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal
from ..models import Wallet, Transaction
from ..tasks import send_notification_task


class TransferAPIView(APIView):
    """
    API для перевода денег между пользователями.
    """

    @transaction.atomic
    def post(self, request):
        from_user_id = request.data.get('from_user_id')
        to_user_id = request.data.get('to_user_id')
        amount = Decimal(request.data.get('amount'))

        if not all([from_user_id, to_user_id, amount]):
            return Response(
                {"error": "from_user_id, to_user_id, amount обязательны"},
                status=400
            )

        if amount <= 0:
            return Response({"error": "amount должен быть > 0"}, status=400)

        try:
            # Блокируем кошельки на время транзакции
            from_wallet = Wallet.objects.select_for_update().get(user_id=from_user_id)
            to_wallet = Wallet.objects.select_for_update().get(user_id=to_user_id)
            admin_wallet = Wallet.objects.select_for_update().get(user__username='admin')
        except Wallet.DoesNotExist:
            return Response({"error": "Кошелёк не найден"}, status=404)

        # Комиссия 10% только если сумма > 1000
        commission = Decimal('0.00')
        if amount > Decimal('1000.00'):
            commission = amount * Decimal('0.10')
        total_debit = amount + commission

        # Защита от double spending и ухода в минус
        if from_wallet.balance < total_debit:
            return Response({"error": "Недостаточно средств"}, status=400)

        # Списываем, зачисляем, снимаем комиссию
        from_wallet.balance -= total_debit
        to_wallet.balance += amount
        admin_wallet.balance += commission

        from_wallet.save(update_fields=['balance'])
        to_wallet.save(update_fields=['balance'])
        admin_wallet.save(update_fields=['balance'])

        # Записываем транзакцию
        Transaction.objects.create(
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=amount,
            commission=commission
        )

        # Асинхронное уведомление получателю
        send_notification_task.delay(to_user_id, amount)

        return Response({
            "status": "success",
            "transferred": f"{amount:.2f}",
            "commission": f"{commission:.2f}",
            "new_balance": f"{from_wallet.balance:.2f}"
        }, status=201)
