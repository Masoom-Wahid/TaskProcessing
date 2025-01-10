from django.contrib import admin
from users.models import OTP,CustomUser
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

class OTPInline(admin.TabularInline):  
    model = OTP
    extra = 0  
    readonly_fields = ('created_at',)  

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_verified', 'is_staff', 'is_superuser',
                                       )}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'is_verified', 'is_staff', 'is_superuser', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'is_verified')
    search_fields = ('email',)
    ordering = ('email',)
    list_filter = ("email",)
    inlines = [OTPInline] 


admin.site.register(CustomUser, UserAdmin)
admin.site.register(OTP)

