from django.db import models

from .validators import max_visitorsVSnumber_of_visitors,beginingVSend,patternVSexcursion,timeline_overlay

from django.core.validators import MaxValueValidator,MinValueValidator
from django.core.exceptions import ValidationError



# Create your models here.
class ExcursionPattern(models.Model):

    WEEKDAYS = (
        (1,"Понедельник"),
        (2,"Вторник"),
        (3,"Среда"),
        (4,"Четверг"),
        (5,"Пятница"),
        (6,"Суббота"),
        (7,"Воскресенье"),
        (0,"НЕТ В РАСПИСАНИИ")
        )

    weekday = models.PositiveIntegerField(
        verbose_name = "День недели",
        choices=WEEKDAYS,
        )

    begining = models.TimeField(
        verbose_name='Начало экскурсий',
        help_text='Укажите начало экскурсий',
        auto_now=False,
        auto_now_add=False,
        default=None,
        )
    
    end = models.TimeField(
        verbose_name = 'Конец экскурсий',
        help_text = 'Укажите конец экскурсий',
        auto_now = False,
        auto_now_add = False,
        default = None,
        )
    
    class Meta:
        verbose_name = "Расписание экскурсии"
        verbose_name_plural = "Расписание экскурсий"
        unique_together = (("weekday", "begining"),)
        ordering = ('weekday','begining')

    def clean(self):
        beginingVSend(self.begining, self.end)
        timeline_overlay(self)
        super().clean()

    def save(self,*args,**kwargs):
        self.full_clean()
        super().save(*args,**kwargs)


    def __str__(self):
        try:
            wd = dict(self.WEEKDAYS)[self.weekday]
        except:
            wd = self.weekday

        return f'{wd} с {self.begining.strftime("%H:%M")} до {self.end.strftime("%H:%M")}'


class Excursion(models.Model):

    pattern  = models.ForeignKey(
        ExcursionPattern,
        verbose_name="Паттерн",
        default=21,
        on_delete=models.SET_DEFAULT,
        )

    max_visitors = models.PositiveIntegerField(
        verbose_name = "Максимальное число участников",
        default=15,
        )

    number_of_visitors = models.PositiveIntegerField(
        verbose_name = "Текущее количество участников",
        default=0,
        )

    start_datetime = models.DateTimeField(
        verbose_name = "Дата и время начала",
        auto_now=False,
        auto_now_add=False,
        )

    end_datetime = models.DateTimeField(
        verbose_name = "Дата и время окончания",
        auto_now=False,
        auto_now_add=False
        )
    
    is_avaliable=models.BooleanField(
        verbose_name = "Доступность регистрации",
        default=0,
        )

    is_shown = models.BooleanField(
        verbose_name = "Отображаемость",
        default=0
        )
    
    @property
    def title(self):
        return f'{self.start_datetime.strftime("%d.%m.%y")}| {dict(ExcursionPattern.WEEKDAYS)[self.start_datetime.isoweekday()]} {self.start_datetime.strftime("%H:%M")}-{self.end_datetime.strftime("%H:%M")}'

    def clean(self,*args,**kwargs):
        max_visitorsVSnumber_of_visitors(self)
        beginingVSend(self.start_datetime, self.end_datetime)
        patternVSexcursion(self)
        timeline_overlay(self)
        super().clean(*args,**kwargs)
    
    def save(self,*args,**kwargs):
        self.full_clean()
        if self.number_of_visitors == self.max_visitors:
            self.is_avaliable=False
        super().save(*args,**kwargs)


    class Meta:
        verbose_name = "Экскурсия"
        verbose_name_plural = "Экскурсии"
        unique_together = (("pattern", "start_datetime"),("pattern", "end_datetime"))
        

    def __str__(self):
        return f'{self.title}'

