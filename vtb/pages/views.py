from django.shortcuts import render,redirect
from .models import IndexButton
from .forms import LoginForm,UserslistFilterForm
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from userforms.forms import *
from excursions.models import Excursion, ExcursionPattern
from userforms.models import Userform
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.models import User
import math
import csv
from django.db.models import Q,F,Value
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

def userslist(request):
    if request.method == "GET":
        userslist = Userform.objects.all()
        form=UserslistFilterForm()
        if request.GET.get('shown_number',False):
            shown_number=request.GET['shown_number']   
        else:
            shown_number=4
        form['shown_number'].initial=shown_number

        if request.GET.get('search_by_field',False) and request.GET.get('looking_for',False):
            search_by_field = request.GET['search_by_field']
            looking_for = request.GET['looking_for']

            form['search_by_field'].initial = search_by_field
            form['looking_for'].initial = looking_for
            q=Q(**{search_by_field+"__icontains":looking_for})
        else:
            search_by_field = ''
            looking_for = ''

    if request.method=="POST":
        form = UserslistFilterForm(request.POST)
        if form.is_valid:
            shown_number = request.POST['shown_number']
            search_by_field = request.POST['search_by_field']
            looking_for = request.POST['looking_for']

            if search_by_field and looking_for:
                q=Q(**{search_by_field+"__icontains":looking_for})

    if 'q' in locals():
        userslist=Userform.objects.filter(q).order_by('-updated_at')
    else:
        userslist = Userform.objects.all().order_by('-updated_at')

    if shown_number=='all':
                shown_number=userslist.count()
    fields = Userform._meta.get_fields()
    paginator=Paginator(userslist,shown_number)
    if userslist.count()<=int(shown_number):
        pagination_indicator = False
    else:
        pagination_indicator = True
    current_page_number = request.GET.get('page')

    try:
        current_page=paginator.page(current_page_number)
    except PageNotAnInteger:
        current_page=paginator.page(1)
    except EmptyPage:
        current_page=paginator.page(paginator.num_pages)

    def get_current_range(current_page = current_page,lower_limit=2,hight_limit=2):
        """
        Формирует диапазон выводимых на экран номеров страниц, который включает текущую страницу.
        Принимает текущую страницу из пагинатора и границы диапазона относительно текущего номера страницы. Применена рекурсия. 
        """
        if sum([lower_limit,hight_limit])>=len(current_page.paginator.page_range):
            return current_page.paginator.page_range
        if current_page.number-lower_limit not in current_page.paginator.page_range:
            lower_limit-=1
            return get_current_range(lower_limit=lower_limit)
        if current_page.number+hight_limit not in current_page.paginator.page_range:
            hight_limit-=1
            return get_current_range(hight_limit=hight_limit)
        return range(current_page.number-lower_limit, current_page.number+hight_limit+1)
    
    def get_limit_page_indicator(current_page=current_page,first_delta=4,last_delta=4):
        """
        Возвращает индикаторы отображения ссылки на первую и последнюю страницы пагинатора,
        в зависимости номера текущей страницы. Принимается текущая страница из пагинатора,
        нижняя и верхняя граница отображения границ пагинатора.
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

    context =  {

        'form':form,
        'search_by_field':search_by_field,
        'looking_for':looking_for,
        'shown_number':shown_number,
        'fields':fields,
        'pagination_indicator':pagination_indicator,
        'current_page':current_page,
        'current_page_range':get_current_range(),
        'first_page_in_current_page_range':paginator.page(get_current_range()[0]),
        'last_page_in_current_page_range':paginator.page(get_current_range()[-1]),
        'limit_page_indicator':get_limit_page_indicator(),
        }
    return render(request,'pages/userformlist.html',context=context)

def csv_out(request):
    if request.GET.get('search_by_field',False) and request.GET.get('looking_for',False):
        search_by_field = request.GET['search_by_field']
        looking_for = request.GET['looking_for']
        q=Q(**{search_by_field+"__icontains":looking_for})
    else:
        search_by_field = ''
        looking_for = ''
    
    if 'q' in locals():
        userslist=Userform.objects.filter(q).order_by('-updated_at')
    else:
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
    