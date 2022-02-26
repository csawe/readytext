from django.db import models
from phone_field import PhoneField

# Create your models here.

class Waitlist(models.Model):
    wait = models.IntegerField()
    party_name = models.CharField(max_length=20)
    size = models.IntegerField()
    phone = PhoneField() #E164_only=False if numbers are from US only.
    note = models.CharField(max_length=20)
    state = models.BooleanField(default=False)
    checked_in = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    time_message_sent = models.DateTimeField(null=True)

    def __str__(self):
        return self.party_name 

class Reservation(models.Model):
    date = models.DateTimeField()
    party_name = models.CharField(max_length=20)
    size = models.IntegerField()
    phone = PhoneField()
    state = models.BooleanField(default=False)
    checked_in = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    
    
class Message(models.Model):
    message_number = models.IntegerField()
    delay =  models.IntegerField()
    message_text = models.CharField(max_length=200)
    
    