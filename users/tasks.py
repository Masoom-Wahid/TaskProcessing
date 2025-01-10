from celery import shared_task
import secrets
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings



@shared_task
def send_otp_email_task(*,email, subject, otp_code, html_path):
    try:
        html_message = render_to_string(html_path, {
            'username': email,
            'otp': otp_code
        })
        plain_message = strip_tags(html_message)
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        
        send_mail(
            subject,
            plain_message,
            from_email,
            to_email,
            html_message=html_message
        )
    except Exception as e:
        print(f"Failed to send email: {e}")



class OtpHandler:
    def __init__(self,
                 *,
                 email:str,
                 subject : str="Your OTP Code",
                 k : int=6,
                 html_path : str = "otp.html"
                 ):
        """
        :param username: the user username
        :param email : the user email
        :param subject : the user's email subject (defaults to 'Your OTP Code')
        :param k: number of digits of ur otp (defaults to 6)
        :param html_path, the file of ur otp (defaults to otp.html)
        """
        self.email : str = email
        self.subject : str = subject
        self.k : int = k
        self.html_path = html_path
        self.otp_code  : str = self.generate_otp()



    def send_email(self):
        send_otp_email_task.delay(
            email=self.email,
            subject=self.subject,
            otp_code=self.otp_code,
            html_path=self.html_path
        )

    def generate_otp(
        self
    ) -> str:
        """
        :param k: the lenght of the otp (defaults to 6)
        :return : string of otp
        """

        digits = '0123456789'
        otp = ''.join(secrets.choice(digits) for _ in range(self.k)) 
        return otp



