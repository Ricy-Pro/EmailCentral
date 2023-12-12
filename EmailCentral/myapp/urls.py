# urls.py in your app
from django.urls import path
from .views import home, Emails, email_detail, download_attachment

urlpatterns = [
    path('', home, name='home'),
    path('emails/', Emails, name='emails'),
    path('emails/<int:pk>/', email_detail, name='email_detail'),
    path('attachments/<path:filename>/', download_attachment, name='download_attachment'),

]
