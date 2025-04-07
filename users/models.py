from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    # Ensure email is unique and used for authentication
    email = models.EmailField(unique=True)

    # Make sure username is not unique
    username = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.email  # Use email as the string representation
