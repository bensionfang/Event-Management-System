from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='list'),
    path('<int:event_id>/', views.event_detail, name='detail'),
    path('<int:event_id>/register/', views.register_event, name='register'),
    path('api/event-info/<int:event_id>/', views.get_event_info, name='api_event_info'),
]
