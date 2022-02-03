from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    
    bio = models.TextField(default="no bio...")
    foto = models.ImageField(upload_to='fotos', default='no_picture.jpg')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
    
