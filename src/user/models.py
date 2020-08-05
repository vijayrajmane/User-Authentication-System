from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class AccountManager(BaseUserManager):
    def create_user(self, phoneNumber, password=None):
        if not phoneNumber:
            raise ValueError("User must have Phone Number")
        if not email:
            raise ValueError("User must have email")

        user = self.model(
            email=self.normalize_email(email),
            phoneNumber=phoneNumber
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phoneNumber,email, password=None):
        user = self.create_user(
            phoneNumber,
            email=self.normalize_email(email),
            password=password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using = self._db)
        return user

'''Overwritting User model provided by Django'''

class Account(AbstractBaseUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(verbose_name="email", max_length=100)
    phoneNumber = PhoneNumberField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'phoneNumber'  # field use for login 
    REQUIRED_FIELDS = ['email'] # field required to create account

    objects = AccountManager()

    def __str__(self):
        return self.name + " " + str(self.phoneNumber) 

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

