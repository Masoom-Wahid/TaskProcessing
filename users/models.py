from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import BaseUserManager,PermissionsMixin





class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_verified',True)
        return self.create_user(email, password, **extra_fields)



class CustomUser(AbstractBaseUser,PermissionsMixin,BaseUserManager):
    email = models.EmailField(blank=False, null=False, unique=True)
    is_verified = models.BooleanField(default=False) #type:ignore
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False) #type:ignore
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()

    class Meta: #type:ignore
        swappable = "AUTH_USER_MODEL"
        verbose_name = "user"
        verbose_name_plural = "users"


    USERNAME_FIELD = "email"


class OTP(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def __str__(self) -> str:
        return str(self.otp_code)
