from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.conf import settings
from dashboards.views import DashboardApiView
from jobs.views import JobViewSet
from django.conf.urls.static import static
from users.views import (
    RegisterApiView,
    VerifyApiView,
    CustomTokenObtainPairView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from rest_framework import permissions

router = DefaultRouter()
router.register(r'jobs',JobViewSet,basename="jobs")



schema_view = get_schema_view(
   openapi.Info(
      title="Task Processing API",
      default_version='v1',
      description="The API for Task Processing",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/register/",RegisterApiView.as_view({'post':'create'})),
    path("api/verify-email/",VerifyApiView.as_view()),
    path("api/login/",CustomTokenObtainPairView.as_view()),
    path("api/dashboard",DashboardApiView.as_view({'get':'list'})),
    path('api/',include(router.urls))
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns.append(path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),)

