from django.core.exceptions import ValidationError

def number_of_visitors_check(instance):
    print("@@@@@@@",instance.excursion.number_of_visitors)
    if instance.excursion.number_of_visitors>=instance.excursion.max_visitors:
        raise ValidationError(f"Превышение количества участников экскурсии({instance.excursion}11)\n\
            Необходимо выбрать другую.")