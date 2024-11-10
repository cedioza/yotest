# tickets/urls.py

from django.urls import path
from . import views


urlpatterns = [
    path('', views.bot_response, name='tickets_index'),  
    path('emails/', views.get_emails, name='get_emails'),
    path('emails/<str:email_id>/', views.get_email_detail, name='get_email_detail'),
    path('emails_attachments/', views.get_emails_with_attachments, name='get_email_detail'),
    path('cron-email/', views.gmail_notification, name='get_email_detail'),

]
