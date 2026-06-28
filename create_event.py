import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_system.settings')
django.setup()
from events.models import Event
from django.utils import timezone
event = Event.active_objects.first()
if not event:
    event = Event.objects.create(
        title="Test Event",
        description="Test",
        date=timezone.now(),
        capacity=10
    )
print('Event ID:', event.id)
