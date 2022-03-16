from django.contrib import admin
from .models import  Waitlist, Message

# Register your models here.
admin.site.register(Waitlist)
admin.site.register(Message)