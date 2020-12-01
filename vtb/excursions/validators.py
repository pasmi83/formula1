from django.core.exceptions import ValidationError
from datetimerange import DateTimeRange
import datetime

def max_visitorsVSnumber_of_visitors(instance):
    """Проверка на превышение количества посетителей"""
    if instance.max_visitors<instance.number_of_visitors:
        raise ValidationError(
    f'Все места заполнены. Максимальное число посетителей - {instance.max_visitors}'
    )

def beginingVSend(begining,end):
    """Конец и начало периода должны быть на своём месте"""
    if begining >= end:
        raise ValidationError(
    f'Конец интервала раньше начала или равенему.'
    )

def patternVSexcursion(instance):
    """Проверка экскурсии на соответствие паттерну и календарю"""
    if instance.pattern.begining!=instance.start_datetime.time():
        e = "Начало экскурсии не совпадает с расписанием"
    elif instance.pattern.end!=instance.end_datetime.time():
        e = "Конец экскурсии не совпадает с расписанием"
    elif instance.pattern.weekday!=instance.start_datetime.isoweekday():
        e = "День недели не соответствует дате"
    else:
        return
    if e:
        raise ValidationError(f'{instance}: {e}')

def timeline_overlay(instance):
    """Проверка на пересечение временного интервала с уже существующими записями"""
    
    def get_datetime_range(start,stop):
        """Принимает начало и конец периода в формате datetime или time и возвращает диапазон времени DateTimeRange"""
        if type(start).__name__=='time' and type(stop).__name__=='time':
            datetime_range = DateTimeRange(
                f"2015-03-22T{start}+0300",
                f"2015-03-22T{stop}+0300")
        elif type(start).__name__=='datetime' and type(stop).__name__=='datetime':
            datetime_range = DateTimeRange(
                f"{start.date()}T{start.time()}+0300",
                f"{stop.date()}T{stop.time()}+0300")
        else:
            raise ValueError('Не тот тип переменных!')
        return datetime_range

    
    if type(instance).__name__ == "ExcursionPattern":
        day_query = type(instance).objects.filter(weekday= instance.weekday)
        r1 = get_datetime_range(instance.begining,instance.end)
        for q in day_query:
            if q.id!=instance.id:
                r2 = get_datetime_range(q.begining,q.end)
                if r2.is_intersection(r1)==True:
                    raise ValidationError(f'Время уже занято! {q}')
    elif type(instance).__name__ == "Excursion":
        day_query = type(instance).objects.filter(pattern__weekday= instance.pattern.weekday)
        r1 = get_datetime_range(instance.start_datetime,instance.end_datetime)
        for q in day_query:
            if q.id!=instance.id:
                r2 = get_datetime_range(q.start_datetime,q.end_datetime)
                if r2.is_intersection(r1)==True:
                    raise ValidationError(f'Время уже занято! {q}')


