from urllib.error import HTTPError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import UpdateView
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm

from django.conf import settings
from django.contrib.auth.decorators import login_required

from main.models import Waitlist, Message, Reservation
from main.forms import WaitlistModelForm, MessageModelForm, NewUserForm, ReservationModelForm

from twilio.rest import Client
from datetime import datetime

# Create your views here.

#Part One one of views
#Handles non-data-rendered pages
def home_view(request):
    return render(request, 'main/home.html', {})

#Part two of views
#Handles views that deals with waitlist

def waitlist_create(request):
    form = WaitlistModelForm(request.POST or None)
    if form.is_valid():
        form.save()
        #Toast a message=, include JS
        waitlist = form.cleaned_data.get('party_name')
        form = WaitlistModelForm()
        messages.success(request, f"New reservation created for {waitlist}")
        return redirect('../waitlist')
    else:
        for msg in form.errors:
            messages.error(request, f'{msg}: {form.errors[msg]}')
        form = WaitlistModelForm()

    context={
        'form' : form,
    }
    return render(request, 'main/waitlist_create.html', context)

def send_message(num, text, request):
    # Your Account SID from twilio.com/console
    account_sid = settings.TWILIO_ACCOUNT_SID
    # Your Auth Token from twilio.com/console
    auth_token = settings.TWILIO_AUTH_TOKEN
    acc_num = settings.TWILIO_NUMBER
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            to=num,
            from_=acc_num,
            body=text
        )
        messages.success(request, 'Message sent')
        print(message.sid)
        return True
    except Exception as e:
        try:
            validation_request = client.validation_requests.create(
                friendly_name='A new Customer',
                phone_number=num
            )
            num = validation_request.phone_number
            message = client.messages.create(
                to=num,
                from_=acc_num,
                body=text
            )
            messages.success(request, 'Message sent')
            print(message.sid)
            return True
        except Exception as ex:
            if HTTPError:
                messages.error(request, "Cannot send text at this moment. Kindly wait...")
                print("Chhange twilio sid and auth")
            else:
                messages.error(request, 'An error occured')
                print(ex)
            return redirect('../')



@login_required
def waitlist_view(request):
    waitlist = Waitlist.objects.all()
    if request.method=='POST':
        id_num = request.POST.get('message-id', None)
        id_num2 = request.POST.get('message-id2', None)
        id_del = request.POST.get('delete-id', None)
        id_upd = request.POST.get('update-id', None)
        id_seated = request.POST.get('seated-id', None)
        id_canncelled = request.POST.get('cancel-id', None)
        if id_num:
            obj = Waitlist.objects.get(id=id_num)
            if obj.state == False:
                num = str(obj.phone)
                txt = Message.objects.get(message_number=1)
                print(txt.message_number)
                body = txt.message_text
                state = send_message(num, body, request)
                if state == True:
                    obj.state = True
                    obj.save()
                obj.time_message_sent = datetime.now()
            else:
                messages.error(request,'First message has already been sent')
        elif id_num2:
            obj = Waitlist.objects.get(id=id_num)
            if obj.state==True:
                num = str(obj.phone)
                txt = Message.objects.get(message_number=2)
                print(txt.message_number)
                body = txt.message_text
                send_message(num, body, request)
                obj.time_message_sent = datetime.now()
        elif id_del:
            obj = Waitlist.objects.get(id=id_del)
            print(f'Deleting {obj.party_name}')
            obj.delete()
            messages.info(request, 'Waitlist deleted')
        elif id_upd:
            obj = Waitlist.objects.get(id=id_upd)
            return redirect(f'../waitlist_update/{obj.id}')
        elif id_seated:
            obj = Waitlist.objects.get(id=id_seated)
            obj.checked_in = True
            obj.save()
            obj.delete()
            messages.success(request, 'Customer has been attended to.')
            return redirect('../waitlist')
        elif id_canncelled:
            obj = Waitlist.objects.get(id=id_canncelled)
            obj.cancelled = True
            obj.save()
            obj.delete()
            messages.success(request, "Customer has cancelled reservation successfully.")
            return redirect('../waitlist')

    for waitlist_obj in waitlist:
        now = datetime.now()
        try:
            ts = (waitlist_obj.time_message_sent).minute or None
            diff = (now.minute) - ts
            if diff > 5:
                text = Message.objects.get(message_number=2)
                body = text.message_text
                send_message(str(waitlist.phone), body)
        except AttributeError:
            continue
    context = {
        'object':waitlist,
    }
    while True:
        return render(request, 'main/waitlist_list.html', context)

class WaitlistUpdateView(UpdateView):
    form_class = WaitlistModelForm
    template_name = 'main/waitlist_update.html'

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(Waitlist, id=id)

    def form_valid(self,form):
        print(form.cleaned_data)
        form.save()
        messages.success(self.request, 'Waitlist updated')
        return redirect('../waitlist')

#Part three of views
#Handles views that deals with messages

def message_create(request):
    form = MessageModelForm(request.POST or None)
    message_tally = Message.objects.all()
    message_tally = message_tally.count()
    print(message_tally)
    if message_tally < 2:
        if form.is_valid():
            form.save()
            form = MessageModelForm()
            return redirect('../message')
        else:
            for msg in form.errors:
                messages.error(request, f'{msg} : {form.errors[msg]}')
            form = MessageModelForm()
        context = {
            'form':form
        }
        return render(request, 'main/message_create.html', context)
    else:
        messages.error(request, 'Message temlates are full.')
    return redirect('../message/')

@login_required
def message_view(request):
    texts = Message.objects.all()

    if request.method =='POST':
        del_num = request.POST.get('delete_id', None)
        upd_num = request.POST.get('update_id', None)
        if del_num:
            obj = Message.objects.get(id=del_num)
            print(obj.message_text)
            print(f'Deleting message {obj.message_text}')
            obj.delete()
        elif upd_num:
            obj = Message.objects.get(id=upd_num)
            return redirect(f'../message_update/{obj.id}')
        else:
            print(request.POST)

    context = {
        'texts': texts,
    }
    return render(request, 'main/message_list.html', context)

class MessageUpdateView(UpdateView):
    template_name = 'main/message_update.html'
    form_class = MessageModelForm

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(Message, id=id)

    def form_valid(self,form):
        print(form.cleaned_data)
        form.save()
        return redirect('../message')

#Part Four
#Handles user logins

def user_register_view(request):
    form = NewUserForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.SUCCESS(request, "Registration Successful")
        return redirect('../')
    context = {
        'form':form,
    }
    return render(request, 'main/register.html', context)

def user_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            uname = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password')
            user = authenticate(username=uname, password=pwd)
            if user is not None:
                login(request, user)
                messages.info(request,'Successfully logged in')
                return redirect('../')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid login credentials")    
    form = AuthenticationForm()
    context = {
        'form':form,
    }
    return render(request, 'main/login.html', context)

def user_logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out')
    return redirect('../')

#Part five
#Handles views that deal with reservations

def reservation_create(request):
    form = ReservationModelForm(request.POST or None)
    if form.is_valid():
        form.save()
        reserve = form.cleaned_data.get('party_name')
        form = ReservationModelForm()
        messages.success(request, f"New reservation created for {reserve}")
        return redirect('../reservation')

    else:
        messages.error(request, 'Invalid details. Make sure date is in format %d%m%Y')
        #for msg in form.errors:
        #    messages.error(request, f'{msg}: {form.errors[msg]}')
        form = ReservationModelForm()

    context={
        'form' : form,
    }
    return render(request, 'main/reservation_create.html', context)

@login_required
def reservation_view(request):
    reservation = Reservation.objects.all()
    if request.method=='POST':
        id_num = request.POST.get('message-id', None)
        id_num2 = request.POST.get('message-id2', None)
        id_del = request.POST.get('delete-id', None)
        id_upd = request.POST.get('update-id', None)
        id_seated = request.POST.get('seated-id', None)
        id_canncelled = request.POST.get('cancel-id', None)
        if id_num:
            obj = Reservation.objects.get(id=id_num)
            if obj.state == False:
                num = str(obj.phone)
                txt = Message.objects.get(message_number=1)
                print(txt.message_number)
                body = txt.message_text
                state = send_message(num, body, request)
                if state == False:
                    obj.state = True
                    obj.save()
                obj.time_message_sent = datetime.now()
            else:
                messages.error(request,'First message has already been sent')
        elif id_num2:
            obj = Waitlist.objects.get(id=id_num)
            if obj.state == True:
                num = str(obj.phone)
                txt = Message.objects.get(message_number=2)
                print(txt.message_number)
                body = txt.message_text
                send_message(num, body)
                messages.success(request, 'Message sent')
                obj.time_message_sent = datetime.now()
        elif id_del:
            obj = Reservation.objects.get(id=id_del)
            print(f'Deleting {obj.party_name}')
            obj.delete()
        elif id_upd:
            obj = Reservation.objects.get(id=id_upd)
            return redirect(f'../waitlist_update/{obj.id}')
        elif id_seated:
            obj = Reservation.objects.get(id=id_seated)
            obj.checked_in = True
            obj.save()
            messages.success(request, 'Customer has been attended to.')
            obj.delete()
            return redirect('../waitlist')
        elif id_canncelled:
            obj = Reservation.objects.get(id=id_canncelled)
            obj.cancelled = True
            obj.save()
            messages.success(request, "Customer has cancelled reservation successfully.")
            obj.delete()
            return redirect('../waitlist')
    for reservation_obj in reservation:
        now = datetime.now()
        try:
            ts = (reservation_obj.time_message_sent).minute or None
            diff = (now.minute) - ts
            if diff > 5:
                text = Message.objects.get(message_number=2)
                body = text.message_text
                send_message(str(reservation_obj.phone), body)
        except AttributeError:
            continue
    context = {
        'object':reservation,
    }

    while True:
        return render(request, 'main/reservation_list.html', context)

class ReservationUpdateView(UpdateView):
    form_class = ReservationModelForm
    template_name = 'main/reservation_update.html'

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(Reservation, id=id)

    def form_valid(self,form):
        print(form.cleaned_data)
        form.save()
        messages.success(self.request, "Reservation has successfully updated.")
        return redirect('../reservation')