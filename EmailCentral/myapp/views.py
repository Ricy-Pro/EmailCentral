from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Email

# Create your views here.
def home(request):
    return render(request, 'home.html')

# views.py in your app
from django.shortcuts import render
from .models import Email

def Emails(request):
    items = Email.objects.all()
    return render(request, 'Emails.html', {'emails': items})


def email_detail(request, pk):
    email = get_object_or_404(Email, pk=pk)
    return render(request, 'email_detail.html', {'email': email})
def download_attachment(request, filename):
  
    email = get_object_or_404(Email, attachments__icontains=filename)
    
    # Assuming you have a 'attachments' field in your Email model
    attachment_path = email.attachments.path
    
    # You may want to set appropriate response headers for downloading the file
    response = HttpResponse(content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Read the attachment file and write it to the response
    with open(attachment_path, 'rb') as attachment_file:
        response.write(attachment_file.read())

    return response