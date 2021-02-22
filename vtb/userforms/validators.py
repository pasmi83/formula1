from django.core.exceptions import ValidationError
from datetime import datetime
def number_of_visitors_check(instance):
    if instance.excursion.number_of_visitors>=instance.excursion.max_visitors:
        raise ValidationError(f"Превышение количества участников экскурсии({instance.excursion}11)\n\
            Необходимо выбрать другую.")

def excursion_not_in_the_past(instance):
    print('instance.excursion.start_datetime',instance.excursion.start_datetime,'datetime.now()',datetime.now())
    if instance.excursion.start_datetime<=datetime.now():
        raise ValidationError(f"Данную экскурсию Вы уже пропустили!")