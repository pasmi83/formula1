from django.shortcuts import render

# Create your views here.
def index(request):
    context={
        "index":"index"
        }
    return render(request,'pages/index.html',context=context)