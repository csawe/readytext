from django.contrib import admin
from .models import  Waitlist, Message, Reservation

# Register your models here.
admin.site.register(Waitlist)
admin.site.register(Message)
admin.site.register(Reservation)
