from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone


# Create your models here.

class Client(models.Model):
    user  = models.OneToOneField(User ,  on_delete=models.CASCADE)
    fullname = models.CharField(max_length=200)
    email = models.EmailField()
    age = models.IntegerField(default=0)
    personal_contact = models.IntegerField()
    relative_contact = models.IntegerField()
    address = models.TextField(max_length=1000)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics/')
    blood_group = models.CharField(max_length=50)


    def __str__(self):
        return self.user.username


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Medical_Record(models.Model):
    date = models.DateField(default = timezone.now)
    amount = models.IntegerField(default = 0)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    hospital = models.CharField(max_length = 200)
    image = models.ImageField(default='default.jpg', upload_to='reports_pic/')
    client = models.ForeignKey(Client , on_delete = models.CASCADE)

    def __str__(self):
        return self.client.user.username









