from django.contrib import admin
from .models import Userform
# Register your models here.


class Admin_of_userform(admin.ModelAdmin):
    list_display = ('__str__','registered_at','staff_fullname')
    #staff_fullname.short_description = "Полное имя вносившего данные"
    #ordering = ('start_datetime','pattern__weekday',)

admin.site.register(Userform,Admin_of_userform)