from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from uuid import uuid4

def send_activation_email(user, request):
    # Generate a raw token
    raw_token = str(uuid4())

    # Hash the token
    hashed_token = make_password(raw_token)

    # Store the activation token for the given user
    user.activation_token = hashed_token
    user.save()

    # Send the raw token in the email link
    activation_link = f"{request.scheme}://{request.get_host()}/api/users/activate/{raw_token}"
    subject = 'Edugen Account Activation'
    message = f"Hi {user.first_name}, Welcome to Edugen \n\nPlease click the link below to activate your account:\n{activation_link}\n\nThank you and Happy Learning!"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])