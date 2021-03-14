from .models import Client
from django import forms
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    fullname = forms.CharField(max_length=200,help_text= 'Required.', label='Full Name')
    email = forms.EmailField(max_length=254, help_text='Required.',label='Email Address')
    #university = forms.CharField(max_length=30, help_text='Required.')
    phone = forms.CharField(max_length=30, help_text='Required.',label='Mobile Number')
    
