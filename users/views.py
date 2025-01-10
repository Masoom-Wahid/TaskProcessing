from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from users.serializers import OtpSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from users.tasks import OtpHandler
from .models import OTP
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import Throttled
from .throttles import OTPRateThrottle

class RegisterApiView(
    GenericViewSet,
    CreateModelMixin
):
    throttle_classes=[OTPRateThrottle],
    
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def throttled(self,request, wait):
        raise Throttled(detail={
            "message": "Sabr is a good thing.",
            "available_in": f"{wait} seconds"
        })
    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(serializer.validated_data["password"])
        user.save()
        
        otp_handler = OtpHandler(
            email=user.email,
        )

        OTP.objects.create( #type:ignore
            user=user,
            otp_code=otp_handler.otp_code
        )
        otp_handler.send_email()


class VerifyApiView(APIView):
    throttle_classes = [OTPRateThrottle]


    def throttled(self,request, wait):
        raise Throttled(detail={
            "message": "Sabr is a good thing.",
            "available_in": f"{wait} seconds"
        })


    @swagger_auto_schema(
        operation_description="Verify user using OTP and return JWT tokens.",
        request_body=OtpSerializer,
        responses={
            200: openapi.Response(
                description="User verified successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    },
                ),
            ),
            400: openapi.Response(
                description="Invalid OTP or other validation errors",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message'),
                    },
                ),
            ),
        },
    )
    def post(self,request):
        serializer = OtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"] #type:ignore
        user.is_verified = True
        user.save()
        refresh_token = RefreshToken.for_user(user)
        return Response(
            {
                "refresh" : str(refresh_token),
                "access" : str(refresh_token.access_token) #type:ignore
            }
        )



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


