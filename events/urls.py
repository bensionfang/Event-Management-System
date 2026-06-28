from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('<int:event_id>/', views.event_detail, name='detail'),
    path('<int:event_id>/register/', views.register_event, name='register'),
    path('registration/<int:registration_id>/success/', views.registration_success, name='registration_success'),
    path('check-in/<uuid:check_in_id>/', views.check_in_by_qr, name='check_in_by_qr'),
    path('<int:event_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('api/event-info/<int:event_id>/', views.get_event_info, name='api_event_info'),
]
