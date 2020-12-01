from datetime import datetime,date,timedelta
from django.contrib import messages

from .models import Excursion

def get_next_weekday_datetime(excursion_pattern,current_date=date.today()):
    """Функция возвращающая два значения даты и времени: 
    1 - дата и время начала экскурсии (ближайший день недели от текущей даты)
    2 - дата и время окончания экскурсии.
    Принимает объект класcа ExcursionPattern и текущую дату(datetime.date).
    """
    current_weekday  = current_date.isoweekday()
    print('!!!!!0!!',current_date)
    print('!!!!!!!',current_weekday)
    if current_weekday < excursion_pattern.weekday:
        next_weekday_date = current_date + timedelta(
            excursion_pattern.weekday-current_weekday
            )
        print ('!!!!1---',next_weekday_date)
    elif current_weekday > excursion_pattern.weekday:
        next_weekday_date = current_date + timedelta(
            (7-current_weekday)+excursion_pattern.weekday
            )
        print ('!!!!2---',(7-current_weekday)+excursion_pattern.weekday)
    else:
        next_weekday_date = current_date
        if excursion_pattern.begining < datetime.now().time():
            print ('!!!!3---',next_weekday_date)
            next_weekday_date = current_date + timedelta(7
            
            ) 
    next_weekday_datetime_start = datetime.combine(
        next_weekday_date,
        excursion_pattern.begining
        )
    next_weekday_datetime_end = datetime.combine(
        next_weekday_date,
        excursion_pattern.end
        )
    return (next_weekday_datetime_start, next_weekday_datetime_end)

def generate_excursion(modeladmin, request, queryset):
    """Создаётся объект класса Excursion с ближайшей датой"""
    for pattern in queryset:
        start_datetime,end_datetime = get_next_weekday_datetime(
            pattern,current_date=date.today()
            )
        excursion = Excursion(
            pattern = pattern,
            start_datetime = start_datetime,
            end_datetime = end_datetime,
            is_avaliable=True,
            is_shown=True,
            )
        try:
            excursion.save()
        except Exception as e:
            messages.error(request, e)
        else:
            messages.success(request, f'Запланирована экскурсия {excursion}')
            
            

