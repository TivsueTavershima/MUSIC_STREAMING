# from django.utils import timezone
# from .models import UserSubscription


# def user_has_premium(user):
#     subscription = (
#         UserSubscription.objects
#         .filter(user=user)
#         .order_by("-expiry_date")
#         .first()
#     )

#     if subscription and subscription.expiry_date > timezone.now():
#         return subscription.plan.name == "PREMIUM"

#     return False