from django.contrib.auth.models import AbstractUser, BaseUserManager  # A new class is imported. ##
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=65, blank=False, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    # def get_profile(self):
    #     try:
    #         profile = Profile.objects.get(user=self)
    #         return profile
    #     except ObjectDoesNotExist:
    #         return None

class EmergencyContact(models.Model):
    user = models.ForeignKey(User, related_name='emergency_contacts', on_delete=models.CASCADE)
    name = models.CharField(max_length=65, blank=False, null=True)
    number = models.CharField(max_length=10, blank=False, null=True)

    def __str__(self):
        return self.number

#How to retrieve phone number from user object?
#user = User.objects.get(email='')
#emergency_contacts = user.emergency_contacts.all()
#for phone in emergency_contacts:
#   print(phone.number)