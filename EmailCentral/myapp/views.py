from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Email, Attachment

# Create your views here.
def home(request):
    return render(request, 'home.html')

# views.py in your app
from django.shortcuts import render
from .models import Email
from django.core.management import call_command

def Emails(request):
    call_command('fetch_emails')
    items = Email.objects.all()
    return render(request, 'Emails.html', {'emails': items})


def email_detail(request, pk):
    email = get_object_or_404(Email, pk=pk)
    return render(request, 'email_detail.html', {'email': email})
def download_attachment(request, pk):
    email = get_object_or_404(Email, pk=pk)
    
    # Assuming you have a 'attachments' ManyToManyField in your Email model
    attachments = email.attachments.all()
    
    if not attachments:
        # Handle the case when there are no attachments
        return HttpResponse("No attachments found.")

    # For simplicity, assuming you're downloading the first attachment
    attachment = attachments[0]
    
    # You may want to set appropriate response headers for downloading the file
    response = HttpResponse(content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{attachment.name}"'

    # Write the attachment content to the response
    response.write(attachment.content)

    return response
