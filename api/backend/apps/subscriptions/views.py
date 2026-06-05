from datetime import timedelta

from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response

from apps.subscriptions.models import Subscription


class SubscriptionDetailView(APIView):

    def get(self, request, tenant_id):

        subscription = Subscription.objects.get(
            client_id=tenant_id
        )

        return Response({
            "plan": subscription.plan_tier,
            "status": subscription.status,
            "modules": subscription.enabled_modules,
            "billing_cycle": subscription.billing_cycle,
            "period_end": subscription.current_period_end,
        })


class SubscriptionUpdateView(APIView):

    def patch(self, request, tenant_id):

        subscription = Subscription.objects.get(
            client_id=tenant_id
        )

        plan_tier = request.data.get("plan_tier")

        subscription.plan_tier = plan_tier
        subscription.save()

        return Response({
            "message": "Subscription updated",
        })


class SubscriptionCancelView(APIView):

    def post(self, request, tenant_id):

        subscription = Subscription.objects.get(
            client_id=tenant_id
        )

        subscription.status = "CANCELLED"
        subscription.save()

        return Response({
            "message": "Subscription cancelled",
        })


class SubscriptionRenewView(APIView):

    def post(self, request, tenant_id):

        subscription = Subscription.objects.get(
            client_id=tenant_id
        )

        subscription.current_period_end = (
            timezone.now().date() + timedelta(days=30)
        )

        subscription.status = "ACTIVE"

        subscription.save()

        return Response({
            "message": "Subscription renewed",
        })  