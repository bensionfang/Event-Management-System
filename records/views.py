from django.shortcuts import render, get_object_or_404
from .models import Record

def record_list(request):
    # Fetch all active and public records and order by year/semester descending
    records = Record.active_objects.filter(is_public=True).select_related('event').order_by('-school_year', '-semester')
    
    # Get all available distinct years for the filter dropdown (only for public records)
    available_years = Record.active_objects.filter(is_public=True).values_list('school_year', flat=True).distinct().order_by('-school_year')
    
    # Filter by selected year if provided
    selected_year = request.GET.get('year')
    if selected_year and selected_year.isdigit():
        records = records.filter(school_year=int(selected_year))
    
    # Group by school_year
    grouped_records = {}
    for record in records:
        year_key = f"{record.school_year} 學年度"
        if year_key not in grouped_records:
            grouped_records[year_key] = []
        grouped_records[year_key].append(record)
        
    return render(request, 'records/record_list.html', {
        'grouped_records': grouped_records,
        'available_years': available_years,
        'selected_year': selected_year
    })
