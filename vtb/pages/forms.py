from django import forms

class LoginForm(forms.Form):
    username=forms.CharField(
        label="Enter your login",
        max_length=50,
        required=True
        )
    password=forms.CharField(
        label="Enter your password",
        max_length=50,
        required=True,
        widget=forms.widgets.PasswordInput
        )
    
class UserslistFilterForm(forms.Form):
    FIELDS_FOR_SEARCH = [
    ('first_name','Имя'),
    ('last_name','Фамилия'),
    ('phone','Телефонный номер'),
    ('email','Адрес электронной почты'),
    ]

    NUMBER_OF_RECORDS = [
        (2,2),
        (4,4),
        (8,8),
        (16,16),
        (32,32),
        (64,64),
        ('all','ВСЁ'),
        ]
    
    
    shown_number = forms.ChoiceField(
        label="Количество отображаемых записей",
        choices=NUMBER_OF_RECORDS,
        initial=NUMBER_OF_RECORDS[1],
        )

    search_by_field = forms.ChoiceField(
        label='Поиск по полю',
        choices=FIELDS_FOR_SEARCH,
        required=False,
        initial=FIELDS_FOR_SEARCH[0],
        )

    looking_for=forms.CharField(
        label='Строка для поиска',
        max_length=50,
        required=False,
        )

    
