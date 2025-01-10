from rest_framework import serializers 
from django.contrib.auth import get_user_model
from users.tasks import OtpHandler
from users.models import OTP, CustomUser
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.settings import api_settings
from datetime import timedelta

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified: #type:ignore
            raise serializers.ValidationError(
                {'detail': 'User account is not verified.'}
            )

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True,write_only=True)
    class Meta:
        model = CustomUser
        fields = ["email","password"]

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True,write_only=True)
    class Meta:
        model = CustomUser 
        fields = ["email", "password"]

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value 

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        otp_handler = OtpHandler(
            username=email,
            email=email,
        )

        user = CustomUser.objects.create_user(email=email,password=password)
        OTP.objects.create( #type:ignore
            user=user,
            otp_code=otp_handler.otp_code
        )
        otp_handler.send_email()

        return user


class OtpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6,min_length=6,required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        otp_code = attrs.get('otp')
        try:
            user = get_user_model().objects.get(email=email)
        except CustomUser.DoesNotExist: #type:ignore
            raise serializers.ValidationError({"err":"No user found with this email address."})

        if user.is_verified:
            raise serializers.ValidationError({"err":"User is already verified"})

        
        TEN_MINUTES = timezone.now() - timedelta(minutes=10)
        

        otp = OTP.objects.filter( #type:ignore
            user=user,
            is_valid=True,
            otp_code=otp_code,
            created_at__gte=TEN_MINUTES
        ).first()
       
        if not otp:
            raise serializers.ValidationError(
                {"detail": "Invalid or expired OTP. Please request a new one."}
            )
        otp.is_valid = False
        otp.save()


        return {"user" : user}



