from django.core.mail import send_mail
from django.conf import settings
import random


def generate_verification_code():
    return ''.join(random.choices('0123456789', k=4))


def send_verification_email(user):
    try:
        # Generate 4-digit code
        verification_code = generate_verification_code()

        # Save code to user
        user.verification_code = verification_code
        user.save()

        # Send email
        subject = 'Edugen Account Verification'
        message = f"""
        Hi {user.first_name},

        Welcome to Edugen! Please use the following code to verify your account:

        {verification_code}

        If you didn't create an account with Edugen, please ignore this email.

        Thank you and Happy Learning!
        """

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return True
    except Exception as e:
        print(f"Error in send_verification_email: {str(e)}")
        return False