from django.urls import include, path
from . import views

urlpatterns = [
    path('event/hook/', views.event_hook, name='event_hook'),
    path('message_action/', views.message_action, name='message_action'),
]
