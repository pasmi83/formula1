import csv
import math
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import F, Q, Value
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from excursions.models import Excursion, ExcursionPattern
from userforms.forms import *
from userforms.models import Userform

from .forms import LoginForm, MailFilter, UserslistFilterForm
from .models import IndexButton


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        current_users_groups = request.user.groups.values('name')
        first_button_set = IndexButton.objects.filter(available_for__in = request.user.groups.all())
        
        context={
            "users_groups":current_users_groups,
            "buttons":first_button_set,
            }
        return render(request,'pages/index.html',context=context)
    else:
        return redirect('pages:login')

def log_in(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request,'pages/login.html',{'form':form})

    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username,password=password)
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return HttpResponseRedirect(reverse('pages:index'))
                else:
                    return HttpResponseRedirect(reverse('pages:login'))
            else:
                return HttpResponseRedirect(reverse('pages:login'))

def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse('pages:login'))

def userform(request):
    userformset = [ContactDataForm(),ExcursionForm(),InvitationForm(),FinForm()]
    if request.method =="GET":
        return render(request,'pages/userform.html',{'userformset':userformset})
    if request.method=="POST":
        universal_d={}
        for form in userformset:
            
            current_f = form.__class__(request.POST)
            if current_f.is_valid():
                
                universal_d = {**universal_d,**current_f.cleaned_data}
            
        userform = Userform(**universal_d)
        userform.staff_id=request.user
        

        try:
            userform.save()
        except Exception as errors:
            for topic,texts in errors:
                extra_tags=topic
                for text in texts:
                    messages.error(request,message=text,extra_tags=extra_tags)
        return render(request,'pages/userform.html',{'userformset':userformset})

def get_current_range(current_page,lower_limit=2,hight_limit=2):
    """
    Принимает текущую страницу из пагинатора и границы диапазона относительно текущего номера страницы. Применена рекурсия.
    Формирует диапазон выводимых на экран номеров страниц, который включает текущую страницу.
     
    """
    if sum([lower_limit,hight_limit])>=len(current_page.paginator.page_range):
        return current_page.paginator.page_range
    if current_page.number-lower_limit not in current_page.paginator.page_range:
        lower_limit-=1
        return get_current_range(current_page, lower_limit=lower_limit)
    if current_page.number+hight_limit not in current_page.paginator.page_range:
        hight_limit-=1
        return get_current_range(current_page, hight_limit=hight_limit)
    return range(current_page.number-lower_limit, current_page.number+hight_limit+1)
    
def get_limit_page_indicator(current_page,first_delta=4,last_delta=4):
    """
    Принимается текущая страница из пагинатора,
    нижняя и верхняя граница отображения границ пагинатора.
    Возвращает индикаторы отображения ссылки на первую и последнюю страницы пагинатора,
    в зависимости номера текущей страницы. 
    """
    first_indicator=False
    last_indicator=False
    if current_page.paginator.page_range[0]+first_delta<=current_page.number:
        first_indicator=True
    if current_page.paginator.page_range[-1]-last_delta>=current_page.number:
        last_indicator=True
    return {
        'first':first_indicator,
        'last':last_indicator
        }

def get_shown_number(request):
    """
    Принимается запрос и Queryset класса Userform
    Возвращает количество отображаемых страниц в для пагинатора 
    """
    shown_number=4
    if request.method=="GET":
        if request.GET.get('shown_number',False):
            shown_number=request.GET['shown_number']   
    elif request.method=="POST":
        form = UserslistFilterForm(request.POST)
        if form.is_valid:
            shown_number = request.POST['shown_number']
    try:
        return int(shown_number)
    except:
        return 1000

def looking_for_something(request):
    """
    Принимается запрос.
    Возвращает словарь: search_by_field - поиск по полю, looking_for - строка поиска,q - аргумент фильтра
    """
    if request.method == "GET":
        if request.GET.get('search_by_field',False) and request.GET.get('looking_for',False):
            search_by_field = request.GET['search_by_field']
            looking_for = request.GET['looking_for']
        else:    
            search_by_field = ''
            looking_for = ''
    elif request.method=="POST":
        form = UserslistFilterForm(request.POST)
        if form.is_valid:
            search_by_field = request.POST['search_by_field']
            looking_for = request.POST['looking_for']
    q=Q(**{search_by_field+"__icontains":looking_for})
    return {
        'search_by_field':search_by_field,
        'looking_for':looking_for,
        'q':q,
        }

def userslist(request):
    if request.method == "GET":
        form=UserslistFilterForm()    
    else:
        form=UserslistFilterForm(request.POST)
    try:
        userslist=Userform.objects.filter(looking_for_something(request)['q']).order_by('-updated_at')
    except:
        userslist = Userform.objects.all().order_by('-updated_at')
    
    form['shown_number'].initial=get_shown_number(request)
    form['search_by_field'].initial = looking_for_something(request)['search_by_field']
    form['looking_for'].initial = looking_for_something(request)['looking_for']

    fields = Userform._meta.get_fields()
    paginator=Paginator(userslist,get_shown_number(request))
    
    if userslist.count()<=int(get_shown_number(request)):
        pagination_indicator = False
    else:
        pagination_indicator = True
    
    current_page_number = request.GET.get('page',1)

    try:
        current_page=paginator.page(current_page_number)
    except PageNotAnInteger:
        current_page=paginator.page(paginator.num_pages)
    except EmptyPage:
        current_page=paginator.page(paginator.num_pages)

    context =  {

        'form':form,
        'shown_number':get_shown_number(request),
        'search_by_field':looking_for_something(request)['search_by_field'],
        'looking_for':looking_for_something(request)['looking_for'],
        'fields':fields,
        'pagination_indicator':pagination_indicator,
        'current_page':current_page,
        'current_page_range':get_current_range(current_page),
        'first_page_in_current_page_range':paginator.page(get_current_range(current_page)[0]),
        'last_page_in_current_page_range':paginator.page(get_current_range(current_page)[-1]),
        'limit_page_indicator':get_limit_page_indicator(current_page),
        }
    return render(request,'pages/userformlist.html',context=context)

def csv_out(request):
    try:
        userslist=Userform.objects.filter(looking_for_something(request)['q']).order_by('-updated_at')
    except:
        userslist = Userform.objects.all().order_by('-updated_at')

    response=HttpResponse(content_type="text/csv")
    response["Content-Disposition"]='attachment;filename="csv_from_query.csv"'
    writer = csv.writer(response)
    model = userslist.model
    field_names_set=[field.name for field in model._meta.fields]
    writer.writerow(field_names_set)
    for userform in userslist:
        values_set=[getattr(userform,name_of_field) for name_of_field in field_names_set]
        writer.writerow(values_set)
    return response

def send_mail_to(request):
    print ('mail-send',request.GET['userform'])
    current_userform=Userform.objects.get(id = request.GET['userform'])
    print('DTT#',type(current_userform.excursion.start_datetime))
    status_of_mail=send_mail(
        subject='Напоминание о записи на экскурсию '+str(current_userform.excursion),
        message='Приглашаем Вас посетить экскурсию в нашем музее, которая состоится '+ str(current_userform.excursion.start_datetime.strftime("%d.%m.%y"))+' в '+ str(current_userform.excursion.start_datetime.strftime("%H:%M")),
        recipient_list = [current_userform.email,],
        from_email='python-mail-test@yandex.ru',
        )
    if status_of_mail==1:
        current_userform.email_send=True
        current_userform.save()
    return redirect(reverse('pages:for_mail_sending')+'?shown_number='+str(get_shown_number(request)))
    
def mail_filter(request):
    if request.method=="GET":
        form = MailFilter()
        print('choices',[i[0] for i in form.fields['for_sending'].choices])
        form.fields['for_sending'].initial = [i[0] for i in form.fields['for_sending'].choices]
    if request.method=="POST":
        form=MailFilter(request.POST)
        if form.is_valid:
            list_of_excursions=form.data.getlist('for_sending',default=None)
            q_list_of_excursions = Q(id__in=list_of_excursions)


    context = {
        'form':form,
    }

    return render(request,'pages/mail_filter.html',context=context)

def for_mail_sending(request):
    if request.method == "GET":
        form=UserslistFilterForm()    
    else:
        form=UserslistFilterForm(request.POST)
    try:
        userslist=Userform.objects.filter(looking_for_something(request)['q']).order_by('-updated_at')
    except:
        userslist = Userform.objects.all().order_by('-updated_at')

    form['shown_number'].initial=get_shown_number(request)
    form['search_by_field'].initial = looking_for_something(request)['search_by_field']
    form['looking_for'].initial = looking_for_something(request)['looking_for']
    
    fields = list(i for i in Userform._meta.get_fields() if i.name not in ('pd_agreement','staff_id','event'))#pd_agreement,

    print ('fields',type(fields))
    for userform in userslist:
        for f in fields:
            print ('attr',getattr(userform,f.name))

    #paginator=Paginator(userslist,per_page=userslist.count())#get_shown_number(request)
    paginator=Paginator(userslist,per_page=get_shown_number(request))
    
    
    if userslist.count()<=paginator.per_page:
        pagination_indicator = False
    else:
        pagination_indicator = True
    
    current_page_number = request.GET.get('page',1)

    try:
        current_page=paginator.page(current_page_number)
    except PageNotAnInteger:
        current_page=paginator.page(paginator.num_pages)
    except EmptyPage:
        current_page=paginator.page(paginator.num_pages)

    context = {
        'form':form,
        'shown_number':get_shown_number(request),
        'search_by_field':looking_for_something(request)['search_by_field'],
        'looking_for':looking_for_something(request)['looking_for'],
        'fields':fields,
        'pagination_indicator':pagination_indicator,
        'current_page':current_page,
        'current_page_range':get_current_range(current_page),
        'first_page_in_current_page_range':paginator.page(get_current_range(current_page)[0]),
        'last_page_in_current_page_range':paginator.page(get_current_range(current_page)[-1]),
        'limit_page_indicator':get_limit_page_indicator(current_page),
        }
    return render(request,'pages/for_mail_sending.html',context=context)
