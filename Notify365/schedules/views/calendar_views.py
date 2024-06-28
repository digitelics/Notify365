from django.shortcuts import render

def calendar(request):
    return render(request, 'schedules/calendar_template.html', {})

def day_calendar(request):
    return render(request, 'schedules/day_calendar_template.html', {})