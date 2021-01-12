from django import forms
from django.forms import formset_factory

from phonenumber_field.formfields import PhoneNumberField
from excursions.models import Excursion
from userforms.models import Userform  

class ContactDataForm(forms.Form):
    first_name=forms.CharField(
        label="Имя",
        max_length=50,
        required=True
    )

    last_name = forms.CharField(
        label="Фамилия",
        max_length=50,
        required=True
    )

    phone=PhoneNumberField(
        label='Телефонный номер',
        required=True,
    )
#----------------------------------------
class ExcursionForm(forms.Form):
    excursion = forms.ModelChoiceField(
        queryset = Excursion.objects.filter(is_avaliable = True).order_by('start_datetime'),
        label='Выбор экскурсии'
    )
#---------------------------------------------
class InvitationForm(forms.Form):
    event = forms.ChoiceField(
        label='События',
        choices=(Userform.EVENTS),
    )
    
    email = forms.EmailField(
        label='Адрес электронной почты',
        max_length=254,
    )
#---------------------------------------------
class FinForm(forms.Form):
    pd_agreement = forms.BooleanField(
        label='Согласие на обработку',
    )

