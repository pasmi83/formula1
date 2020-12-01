from django.contrib import admin
from .models import ExcursionPattern,Excursion
from .utils import generate_excursion
# Register your models here.
class Admin_of_ExcursionPattern(admin.ModelAdmin):
    list_display = ('__str__','id',)
    generate_excursion.short_description = 'Запланировать экскурсию на неделю вперёд'
    actions = [generate_excursion]

class Admin_of_Excursion(admin.ModelAdmin):
    #fields = ('max_visitors','pattern',)
    list_display = ('title','date','is_avaliable','is_shown')
    ordering = ('start_datetime','pattern__weekday',)

    def date(self,obj):
        return obj.start_datetime.strftime('%d.%m.%Y')
    date.short_description = "Дата экскурсии"

admin.site.register(ExcursionPattern,Admin_of_ExcursionPattern)
admin.site.register(Excursion,Admin_of_Excursion)
