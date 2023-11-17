from celery import shared_task

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

from .utils import generate_random_password
from .models import Scholar, CustomUser, UserIdCounter
from application.models import Applications


@shared_task
def supply_account(application_id):
    subject_email = "Account Provision"

    application = Applications.objects.get(id=application_id)
    Scholar = get_user_model()

    date_joined = timezone.now()

    username = CustomUser.generated_formatted_id(CustomUser(date_joined=date_joined))
    password = generate_random_password()
    
    print(password)

    # Create a scholar instance
    scholar = Scholar.objects.create(
        username = username,
        password = make_password(password),
        email = application.email_address,
        is_active = True
    )

    context = {
        "username": username,
        "password": password,
    }

    html_message = render_to_string("content/supply_account.html", context=context)
    plain_message = strip_tags(html_message)

    message = EmailMultiAlternatives(
        subject = subject_email,
        body = plain_message,
        from_email = None,
        to = [application.email_address,]
    )

    message.attach_alternative(html_message, "text/html")
    message.send()