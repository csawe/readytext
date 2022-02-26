from django import forms
from .models import Waitlist, Message, Reservation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class WaitlistModelForm(forms.ModelForm):
    class Meta:
        model = Waitlist
        fields = ['wait', 'party_name', 'size','phone','note']
        
class MessageModelForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message_number','delay','message_text']
        
class ReservationModelForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['date', 'party_name', 'size', 'phone']
        
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