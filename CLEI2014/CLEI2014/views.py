from django.http import HttpResponse, HttpResponseRedirect
import datetime
import urllib
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render

#View que despliega la pagina de inicio del sistema
def home(request):
  now= datetime.datetime.now()
  return render (request,'index.html',{'now':now})
