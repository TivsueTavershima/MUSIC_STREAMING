# from django.conf import settings
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.db import models
# from django.utils import timezone
# from billing.models import Subscription
# from users.managers import UserManager



# class User(AbstractBaseUser, PermissionsMixin):
#     ROLE_CHOICES = (
#         ("USER", "User"),
#         ("ADMIN", "Admin"),
#         ("ARTIST", "Artist"),
#     )

#     email             = models.EmailField(unique=True)
#     first_name        = models.CharField(max_length=50)
#     last_name         = models.CharField(max_length=50)
#     phone_number      = models.CharField(max_length=20, blank=True, null=True)
#     role              = models.CharField(max_length=20, choices=ROLE_CHOICES, default="USER")
#     is_premium        = models.BooleanField(default=False)
#     subscription_expiry = models.DateTimeField(null=True, blank=True)
#     is_active         = models.BooleanField(default=True)
#     is_staff          = models.BooleanField(default=False)
#     created_at        = models.DateField(auto_now_add=True)

#     objects = UserManager()

#     USERNAME_FIELD  = "email"   # ✅ use email to login
#     REQUIRED_FIELDS = []        # ✅ no extra required fields

#     def __str__(self):
#         return self.email

#     def has_active_subscription(self):
#         if self.is_premium and self.subscription_expiry:
#             return self.subscription_expiry > timezone.now()
#         return False


# class UserSubscription(models.Model):
#     user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     plan       = models.ForeignKey(Subscription, on_delete=models.CASCADE)
#     start_date = models.DateTimeField(auto_now_add=True)
#     expiry_date = models.DateTimeField()

#     def is_active(self):
#         return self.expiry_date > timezone.now()

#     def __str__(self):
#         return f"{self.user.email} - {self.plan.name}"  # ✅ changed .username to .email









from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        FREE = "free", "Free"
        PREMIUM = "premium", "Premium"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.FREE)
    is_premium = models.BooleanField(default=False)
    subscription_expiry = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN

    @property
    def subscription_is_active(self):
        if not self.is_premium:
            return False
        if self.subscription_expiry and self.subscription_expiry < timezone.now():
            return False
        return True