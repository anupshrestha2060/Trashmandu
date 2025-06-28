from django import forms
from django.contrib.auth.models import User
from .models import CollectorProfile

class CollectorUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class CollectorProfileForm(forms.ModelForm):
    class Meta:
        model = CollectorProfile
        fields = ['phone', 'address']  # whatever fields your CollectorProfile has
