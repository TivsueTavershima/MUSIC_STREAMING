
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