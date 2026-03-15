from django import forms
from .models import Tweet
import re

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class TweetForm(forms.ModelForm):
    class Meta:
        model=Tweet
        fields=['text','photo']


class UserRegrestrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-input'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-input'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-input'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-input'}))

    class Meta:
        model = User
        fields = ('username','email','password1','password2')
# What this does
# model = User
# This tells Django that this form is associated with the User model (built-in django.contrib.auth.models.User).
# When the form is saved, it will create a new User instance in the database.

# Here:
# model = Tweet → The form is linked to your Tweet model.
# fields = ['text', 'photo'] → Only these two fields will show in the form (not user or updated_at, since those are handled automatically).




from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profession', 'email', 'bio', 'profile_photo']






from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm): #Automatically maps model fields → form fields
    class Meta:
        model = UserProfile
                                # UserProfile.bio          → form.bio
                                # UserProfile.profession   → form.profession
                                # UserProfile.email        → form.email
                                # UserProfile.profile_photo → form.profile_photo

        fields = ['profile_photo', 'profession', 'email', 'bio']  # Saare fields include hain
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Enter your bio...'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your profession...'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your.email@example.com'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Fields ko required ya optional banane ke liye
        self.fields['bio'].required = False
        self.fields['profession'].required = False
        self.fields['email'].required = False
        self.fields['profile_photo'].required = False


from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class CombinedProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150)

    class Meta:
        model = UserProfile
        fields = ['profile_photo', 'profession', 'email', 'bio']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')   # logged-in user
        super().__init__(*args, **kwargs)

        # Pre-fill username
        self.fields['username'].initial = user.username

        # Make fields optional
        self.fields['bio'].required = False
        self.fields['profession'].required = False
        self.fields['email'].required = False
        self.fields['profile_photo'].required = False

    def clean_username(self):
        username = self.cleaned_data['username']
        user_qs = User.objects.filter(username=username)

        # if username exists but it's not current user
        if user_qs.exists() and user_qs.first().id != self.instance.user.id:
            raise forms.ValidationError("This username is already taken.")
        
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user

        # update username
        user.username = self.cleaned_data['username']
        user.save()

        if commit:
            profile.save()

        return profile



from django import forms
from django.contrib.auth.models import User

class UsernameUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

    def clean_username(self):
        username = self.cleaned_data['username']
        qs = User.objects.filter(username=username)
        if qs.exists() and qs.first().id != self.instance.id:
            raise forms.ValidationError("This username is already taken.")
        return username

from django.contrib.auth.forms import PasswordChangeForm



from django import forms
from django.contrib.auth.models import User

class SetPasswordWithoutOldForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="New password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm new password"
    )

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")

        if p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def save(self, user):
        user.set_password(self.cleaned_data["new_password1"])
        user.save()
        return user
