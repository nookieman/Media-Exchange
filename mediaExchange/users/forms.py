from django import forms
from django.contrib.auth.models import User
 
class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    email = forms.EmailField(label='E-Mail')
    password1 = forms.CharField(label='Password', max_length=255, widget=forms.PasswordInput())
    password2 = forms.CharField(label='Retype password', max_length=255, widget=forms.PasswordInput())

    def arePasswordsEqual(self):
        return self.cleaned_data['password1'] == self.cleaned_data['password2']

    def isValidUsername(self):
        result = False
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            result = True
        return result

    def save(self):
        u = User.objects.create_user(username = self.cleaned_data['username'],
                                     email = self.cleaned_data['email'],
                                     password = self.cleaned_data['password1'])
        u.is_active = False
        u.save()
        return u

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255, widget=forms.PasswordInput())
