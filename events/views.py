from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db import transaction
from .models import Event, Registration

def event_list(request):
    events = Event.active_objects.order_by('-date')
    return render(request, 'events/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(Event.active_objects, id=event_id)
    
    # Anonymize attendees (e.g., 王大明 -> 王O明)
    attendees = []
    for reg in event.registrations.select_related('user'):
        name = reg.user.last_name + reg.user.first_name if reg.user.last_name or reg.user.first_name else reg.user.username
        if len(name) >= 3:
            anon_name = name[0] + 'O' + name[2:]
        elif len(name) == 2:
            anon_name = name[0] + 'O'
        else:
            anon_name = name + 'O'
        attendees.append(anon_name)
        
    is_registered = False
    if request.user.is_authenticated:
        is_registered = Registration.objects.filter(event=event, user=request.user).exists()
        
    return render(request, 'events/event_detail.html', {
        'event': event,
        'attendees': attendees,
        'is_registered': is_registered,
        'is_full': event.registered_count >= event.capacity
    })

@login_required
@transaction.atomic
def register_event(request, event_id):
    if request.method == 'POST':
        # Select for update to lock the row
        event = Event.active_objects.select_for_update().get(id=event_id)
        
        if Registration.objects.filter(event=event, user=request.user).exists():
            messages.warning(request, "您已經報名過此活動。")
            return redirect('events:detail', event_id=event.id)
            
        if event.registered_count >= event.capacity:
            messages.error(request, "抱歉，本活動名額已滿。")
            return redirect('events:detail', event_id=event.id)
            
        # Create registration
        Registration.objects.create(event=event, user=request.user)
        
        # Update count atomically using F() expression as backup or select_for_update is sufficient
        event.registered_count = F('registered_count') + 1
        event.save()
        
        messages.success(request, "報名成功！")
        return redirect('events:detail', event_id=event.id)
        
    return redirect('events:list')

from django.http import JsonResponse

def get_event_info(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
        return JsonResponse({
            'success': True,
            'school_year': event.school_year,
            'year': event.year,
            'semester': event.semester,
        })
    except Event.DoesNotExist:
        return JsonResponse({'success': False})
