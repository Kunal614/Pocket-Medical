from django.contrib import admin
from .models import Client , Medical_Record 
# Register your models here.

admin.site.register(Client)
admin.site.register(Medical_Record)