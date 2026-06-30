from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.html import strip_tags
import urllib.parse
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
        
        # 發送報名成功信件與 QR Code
        try:
            check_in_url = request.build_absolute_uri(reverse('events:check_in_by_qr', args=[registration.check_in_id]))
            qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={urllib.parse.quote(check_in_url)}"
            
            subject = f"報名成功通知：{event.title}"
            
            # 格式化活動時間，處理 timezone
            from django.utils import timezone
            local_date = timezone.localtime(event.date).strftime('%Y-%m-%d %H:%M')
            
            html_content = f"""
            <h2>您已成功報名 {event.title}</h2>
            <p>親愛的 <strong>{registration.name}</strong> 您好，</p>
            <p>這是一封報名成功通知信。以下為您的報名資訊與活動詳情：</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="margin-top: 0;">報名資訊</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li><strong>活動名稱：</strong>{event.title}</li>
                    <li><strong>報名姓名：</strong>{registration.name}</li>
                    <li><strong>聯絡信箱：</strong>{registration.email}</li>
                    <li><strong>活動時間：</strong>{local_date}</li>
                    <li><strong>活動地點：</strong>{event.location or '未定'}</li>
                </ul>
            </div>
            
            <p>請在活動當天出示下方 QR Code 進行簽到：</p>
            <div style="margin: 20px 0;">
                <img src="{qr_image_url}" alt="簽到 QR Code" width="200" height="200" />
            </div>
            <p>如果圖片無法顯示，請點擊下方連結取得您的簽到 QR Code：</p>
            <p><a href="{check_in_url}">{check_in_url}</a></p>
            <p>感謝您的參與！</p>
            """
            text_content = strip_tags(html_content)
            
            email_msg = EmailMultiAlternatives(
                subject,
                text_content,
                None,
                [registration.email]
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send(fail_silently=True)
        except Exception as e:
            # 若發送失敗不影響報名流程
            pass

        return redirect('events:registration_success', registration_id=registration.id)
        
    return redirect('events:detail', event_id=event.id)

def registration_success(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id)
    event = registration.event
    
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
        'is_full': event.registered_count >= event.capacity,
        'registration_success_modal': registration
    })

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
