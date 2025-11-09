import secrets

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import PermissionsMixin

from tabibi_core.constants import USER_TYPE_CHOICES, Const


class CommonInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        abstract = True


class TabibiUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('User mast have email address')

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, CommonInfo, PermissionsMixin):
    USERNAME_FIELD = 'email'
    user_type      = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default=Const.USER_TYPE_PATIENT)
    email          = models.EmailField(unique=True)
    email_verified = models.BooleanField(default=False)
    first_name     = models.CharField('firstname', max_length=150, blank=True)
    last_name      = models.CharField('lastname', max_length=150, blank=True)
    is_active      = models.BooleanField('Active', default=False)
    id_number      = models.CharField(max_length=100, blank=True, null=True)
    id_scan        = models.FileField(upload_to='id_scans/', blank=True, null=True)

    objects = TabibiUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    @property
    def full_name(self):
        if self.first_name and self.last_name: return f'{self.first_name} {self.last_name}'
        if self.first_name                   : return self.first_name
        if self.last_name                    : return self.last_name
        return self.email

    @property
    def group_name(self):
        if self.is_superuser:
            return 'Administrator (Superuser)'

        if self.groups.count() > 1:
            return ', '.join([obj.split(" ", 1)[1] for obj in self.groups.values_list('name', flat=True)])

        return ''.join([obj.split(" ", 1)[1] for obj in self.groups.values_list('name', flat=True)])

    @property
    def is_staff(self):
        return self.is_superuser

    def get_full_name(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.email: self.email = self.email.lower()
        if self.user_type == Const.USER_TYPE_SUPERUSER: self.is_superuser = True
        if self.is_superuser: self.user_type = Const.USER_TYPE_SUPERUSER
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name()


class Token(CommonInfo):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    token      = models.CharField(max_length=120, unique=True)
    is_refresh = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f'Token for {self.user.email} (expires at {self.expires_at})'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_hex(50)
        return super().save(*args, **kwargs)
