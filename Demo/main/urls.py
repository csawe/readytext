from django.urls import path
from .views import home_view, reservation_view, waitlist_view, waitlist_create, reservation_create, message_view, message_create, WaitlistUpdateView, ReservationUpdateView, MessageUpdateView, user_register_view, user_login_view, user_logout_view
app_name = 'main'

urlpatterns = [
    path('', home_view, name='home-view'),
    
    path('login/', user_login_view, name="login-page"),
    path('register/',user_register_view ,name="register-page"),
    path('logout/', user_logout_view, name='logout-page'),
    
    path('waitlist/', waitlist_view, name='waitlist-list'),
    path('waitlist_create/', waitlist_create, name='waitlist-create'),
    path('waitlist_update/<int:id>', WaitlistUpdateView.as_view(), name='waitlist-update' ),
       
    path('reservation/', reservation_view, name='reservation-list'),
    path('reservation_create/', reservation_create, name='reservation-create'),
    path('reservation_update/<int:id>', ReservationUpdateView.as_view(), name='reservation-update' ), 
        
    path('message/', message_view, name='message-view'),
    path('message_create/', message_create, name='message-create'),
    path('message_update/<int:id>', MessageUpdateView.as_view(), name='message-update' ),
]

