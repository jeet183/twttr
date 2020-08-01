from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class UserRegisterForm(forms.Form):
    CHOICES = (('Cricket','Cricket'),
               ('FootBall','FootBall'),
               ('Sports','Sports'),
               ('Bollywood','Bollywood'),
               ('Politics','Politics'),
               ('General Knowledge' , 'General Knowledge'),
               ('Hollywood' , 'Hollywood'))

    username = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    interest = forms.MultipleChoiceField(choices=CHOICES, widget=forms.CheckboxSelectMultiple())
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)


    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password != password2:
            raise forms.ValidationError("Password must match")
        return password2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__icontains=username).exists():
            raise forms.ValidationError("This username is taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__icontains=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']

