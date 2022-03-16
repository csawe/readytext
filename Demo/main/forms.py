from django import forms
from .models import Waitlist, Message
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class WaitlistModelForm(forms.ModelForm):
    class Meta:
        model = Waitlist
        fields = ['wait', 'party_name', 'size', 'date', 'phone', 'note']
        widgets = {
            'date': forms.DateInput(attrs={"type":"date"})
        }

class MessageModelForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message_number','delay','message_text', 'message_context']

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user