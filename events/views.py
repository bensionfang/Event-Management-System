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
    for reg in event.registrations.all():
        name = reg.name
        if len(name) >= 3:
            anon_name = name[0] + 'O' + name[2:]
        elif len(name) == 2:
            anon_name = name[0] + 'O'
        else:
            anon_name = name + 'O'
        attendees.append(anon_name)
        
    return render(request, 'events/event_detail.html', {
        'event': event,
        'attendees': attendees,
        'is_full': event.registered_count >= event.capacity
    })

@transaction.atomic
def register_event(request, event_id):
    event = get_object_or_404(Event.active_objects, id=event_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        
        if not name or not email:
            messages.error(request, "請填寫姓名與聯絡信箱。")
            return redirect('events:detail', event_id=event.id)
            
        # Select for update to lock the row
        event_locked = Event.active_objects.select_for_update().get(id=event_id)
        
        if Registration.objects.filter(event=event_locked, email=email).exists():
            messages.warning(request, "此信箱已經報名過此活動。")
            return redirect('events:detail', event_id=event.id)
            
        if event_locked.registered_count >= event_locked.capacity:
            messages.error(request, "抱歉，本活動名額已滿。")
            return redirect('events:detail', event_id=event.id)
            
        # Create registration
        registration = Registration.objects.create(event=event_locked, name=name, email=email)
        
        # Update count atomically
        event_locked.registered_count = F('registered_count') + 1
        event_locked.save()
        
        messages.success(request, "報名成功！")
        # 未來可以重導向到成功頁面顯示 QR Code，目前先導回詳情頁
        return redirect('events:registration_success', registration_id=registration.id)
        
    return redirect('events:detail', event_id=event.id)

def registration_success(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    return render(request, 'events/registration_success.html', {'registration': registration})

@login_required
@transaction.atomic
def cancel_registration(request, event_id):
    if request.method == 'POST':
        event = Event.active_objects.select_for_update().get(id=event_id)
        registration = Registration.objects.filter(event=event, user=request.user).first()
        
        if registration:
            registration.delete()
            event.registered_count = F('registered_count') - 1
            event.save()
            messages.success(request, "取消報名成功！")
        else:
            messages.warning(request, "您尚未報名此活動。")
            
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('events:detail', event_id=event.id)
        
    return redirect('events:list')

@login_required
def check_in_by_qr(request, check_in_id):
    # 確保是具備管理權限的人員（至少是 staff）才能進行簽到動作
    if not request.user.is_staff:
        messages.error(request, "您沒有權限執行簽到作業。")
        return redirect('events:list')
        
    registration = get_object_or_404(Registration, check_in_id=check_in_id)
    
    if registration.attended:
        status = 'already_checked_in'
        message = f"【{registration.name}】已經簽到過了！"
    else:
        registration.attended = True
        registration.save()
        status = 'success'
        message = f"簽到成功！歡迎【{registration.name}】參加 {registration.event.title}。"
        
    return render(request, 'events/check_in_result.html', {
        'registration': registration,
        'status': status,
        'message': message
    })

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
