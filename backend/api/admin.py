from django.contrib import admin

from .models import MeUser, MeFollow

class MeUserAdmin(admin.ModelAdmin):
    """ Админ зона для пользователей """
    list_display = ('last_name', 'email', 'first_name')
    search_fields = ('username', 'email')
    list_filter = ('email', 'username')

class MeFollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')




admin.site.register(MeUser) 
admin.site.register(MeFollow) 
