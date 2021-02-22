from django.urls import path

from . import views

app_name = "pages"
urlpatterns = [
    path('',views.index,name='index'),
    path('login',views.log_in,name='login'),
    path('logout',views.log_out,name='logout'),
    path('userform',views.userform,name='userform'),
    path('userslist',views.userslist,name='userslist'),
    path('csv_out',views.csv_out,name="csv_out"),
    path('mail_filter',views.mail_filter,name="mail_filter"),
    path('for_mail_sending',views.for_mail_sending, name="for_mail_sending"),
    path('send_mail_to',views.send_mail_to, name="send_mail_to"),
]
