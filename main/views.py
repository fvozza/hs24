from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ObjectDoesNotExist
from auth.models import OauthToken
import oauth2 as oauth
import urllib
import ipdb

@login_required(login_url='login/')
def index(request):
  
  try:
    t = OauthToken.objects.get(username=request.user.username)
    c = {
      'isAuthorized': t.is_authorized()
    }
  except ObjectDoesNotExist:
    c = {
      'isAuthorized': False
    }
  return render_to_response('index.html', c, context_instance=RequestContext(request))

@csrf_protect
@never_cache
def login_user(request, redirect_field_name=REDIRECT_FIELD_NAME):
  redirect_to = request.REQUEST.get(redirect_field_name, '')
  username = request.POST['username']
  password = request.POST['password']
  user = authenticate(username=username, password=password)
  if user is not None:
    if user.is_active:
      login(request, user)
      return HttpResponseRedirect(redirect_to)
    else:
    	return HttpResponse("Already logged in")
  else:
    return render_to_response('login.html', {'login_error': True, }, context_instance=RequestContext(request))

