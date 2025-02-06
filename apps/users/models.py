import uuid

from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db import models


class User(AbstractUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('company', 'Client Company'),
        ('client', 'Client'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    # Password is already handled by AbstractBaseUser
    profile_pic = models.ImageField(upload_to="profile_img", blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Admin(User):
    created_at = models.DateTimeField(auto_now_add=True)
    last_admin_login = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.role = 'admin'
        self.is_staff = True
        self.is_superuser = True  # Grants all permissions
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Admin: {self.first_name} {self.last_name}"


class Member(User):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("disabled", "Disabled"),
        ("pending", "Pending"),
        ("banned", "Banned"),
    ]

    registration_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    address = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Member: {self.first_name} {self.last_name}"


class Driver(Member):
    driving_license = models.ImageField(upload_to="driver_licence_img", blank=True, null=True)
    experience = models.IntegerField(default=0, help_text="Years of experience")

    def __str__(self):
        return f"Driver: {self.first_name} {self.last_name}"


class ClientCompany(Member):
    company_name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)

    def __str__(self):
        return f"Company: {self.company_name}"


class IndividualClient(Member):
    pass

    def __str__(self):
        return f"Client: {self.first_name} {self.last_name}"
