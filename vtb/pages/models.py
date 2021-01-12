from django.db import models
from django.contrib.auth.models import Group
# Create your models here.
class CustomQuerySet(models.QuerySet):
        def get_queryset(self):
            return self.order_by('position')
        #def by_group(self,request):
        #    return get_queryset(self).filter(available_for = request.user.groups.)

class CustomManager(models.Manager):
        def get_queryset(self):
            return CustomQuerySet(self)


class IndexButton(models.Model):

    objects = CustomManager
    
    name = models.CharField(
        max_length=20,
        verbose_name="Надпись на кнопке",
        blank=False,
        unique=True,
        )

    position = models.SmallIntegerField(
        verbose_name="Позиция кнопки",
        blank=True,
        unique=True,
        )
    
    href = models.CharField(
        max_length=200,
        verbose_name="Ссылка или действие",
        blank=False,
        unique=True,
        )
    
    class_of = models.CharField(
        max_length=50,
        verbose_name="Класс",
        blank=True,
        )

    available_for = models.ManyToManyField(
        Group,
        verbose_name="Группа пользователей",
        blank=False,
        )





    class Meta:
        verbose_name = "IndexButton"
        verbose_name_plural = "IndexButtons"
        ordering = ['position']

    def __str__(self):
        return self.name
