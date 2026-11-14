from django.shortcuts import render
from core.models import CompanySettings

def contacts(request):
    company = CompanySettings.objects.first()

    return render(request, 'public/contacts.html',{'company': company})

def about(request):
    company = CompanySettings.objects.first()

    return render(request, 'public/about.html', {'company': company})