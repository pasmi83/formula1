from django.db import models
from django.contrib.auth.models import User

from phonenumber_field.modelfields import PhoneNumberField

from .validators import number_of_visitors_check, excursion_not_in_the_past
from excursions.models import Excursion
# Create your models here.

class Userform(models.Model):

    EVENTS = (
        ("фм","Футбольный матч"),
        ("хм","Хоккейный матч"),
        ("кз","Концерт звезды"),
        ("др","'Другое"),
    )

    __original_excursion = None #сюда при инициализации попадёт первоначальное значение excursion

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=50,
        )
    
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=50,
        )

    phone = PhoneNumberField(
        verbose_name='Телефонный номер',
        unique=True,
        )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        )

    pd_agreement = models.BooleanField(
        verbose_name='Согласие на обработку',
        default=False,
        )

    email_send = models.BooleanField(
        verbose_name='Статус отправки письма',
        default=False,
        )

    email_status = models.BooleanField(
        verbose_name='Статус доставки письма',
        default=False,
        )

    staff_id = models.ForeignKey(
        User,
        verbose_name='id Персонала',
        on_delete=models.DO_NOTHING,
        )

    @property
    def staff_fullname(self):
        if self.staff_id.get_full_name():
            return self.staff_id.get_full_name
        else:
            return self.staff_id.username

    staff_fullname.fget.short_description = 'Полное имя вносившего данные'

    registered_at = models.DateTimeField(
        verbose_name='Дата и время регистрации',
        auto_now=False,
        auto_now_add=True,
        )
    
    updated_at = models.DateTimeField(
        verbose_name='Дата и время изменения записи',
        auto_now=True,
        auto_now_add=False,
        )

    excursion = models.ForeignKey(
        Excursion,
        verbose_name="Экскурсия",
        on_delete=models.DO_NOTHING,
        null=True,
        )
    
    event = models.CharField(
        verbose_name="Событие",
        max_length=2,
        choices=EVENTS,
        )
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.__original_excursion = self.excursion
        print('init!!!!', self.__original_excursion)

    def clean(self,*args,**kwargs):
        number_of_visitors_check(self)
        excursion_not_in_the_past(self)
        super().clean(*args,**kwargs)


    def save(self,*args,**kwargs):
        
        def visitor_plus(instance = self):
            excursion = Excursion.objects.get(id = instance.excursion.id)
            excursion.number_of_visitors += 1
            excursion.save()
        
        
        if self.__original_excursion != None and self.__original_excursion != self.excursion:
            previous_excursion = Excursion.objects.get(id = self.__original_excursion.id)
            print('B previous_number',previous_excursion.number_of_visitors)
            previous_excursion.number_of_visitors -= 1
            print('AFT previous_number',previous_excursion.number_of_visitors)
            previous_excursion.save()
            print('11111self.__original_excursion!!!!',self.__original_excursion,'self.excursion!!!!!',self.excursion)
            visitor_plus()
        elif self.__original_excursion == None:
            print('22222self.__original_excursion!!!!',self.__original_excursion,'self.excursion!!!!!',self.excursion)
            visitor_plus()
        elif self.__original_excursion == self.excursion:
            pass
        elif self.__original_excursion != None and self.__original_excursion == self.excursion:
            super().save(*args,**kwargs)
        
        self.full_clean()
        super().save(*args,**kwargs)

    class Meta:
        verbose_name = "Анкета участников"
        verbose_name_plural = "Анкеты участников"
        unique_together = (('first_name','last_name'),)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    #def get_absolute_url(self):
    #    return reverse("Userform_detail", kwargs={"pk": self.pk})
