from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from auth.models import OauthToken
import oauth2 as oauth
import urlparse
import urllib
import socks
from django.utils import simplejson
from httplib2 import ProxyInfo

IS24_CONSUMER_KEY = "Home SearchKey"
IS24_COSUMER_SECRET = "rH1335WD26eXKK8t"
IS24_REQUEST_TOKEN_URL = "http://rest.immobilienscout24.de/restapi/security/oauth/request_token"
IS24_CONFIRM_TOKEN_URL = "http://rest.immobilienscout24.de/restapi/security/oauth/confirm_access"
IS24_ACCESS_TOKEN_URL = "http://rest.immobilienscout24.de/restapi/security/oauth/access_token"
HS24_OAUTH_CALLBACK = "http://zi0n.no-ip.org:8000/oauth_callback"


@login_required(login_url='login/')
def authorize(request):
  if not isAuthorized(request.user):
    consumer = oauth.Consumer(IS24_CONSUMER_KEY, IS24_COSUMER_SECRET)
    client = oauth.Client(consumer)
    
    resp, content = client.request(IS24_REQUEST_TOKEN_URL, 'POST',
      body = 'oauth_callback=%s' % HS24_OAUTH_CALLBACK
    )
    
    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])
    
    request_token = dict(urlparse.parse_qsl(content))

    t = OauthToken(username=request.user.username, 
                  oauth_token=request_token['oauth_token'],
                  oauth_token_secret=request_token['oauth_token_secret'])
    t.save()
    
    redirect_url = "%s?oauth_token=%s" % (IS24_CONFIRM_TOKEN_URL, request_token['oauth_token'])
    
    return HttpResponseRedirect(redirect_url)
  else:
    return HttpResponse("User %s is already authorized" % request.user.username)

def oauth_callback(request):
  t = OauthToken.objects.get(username=request.user.username)
  t.oauth_verifier = request.GET['oauth_verifier']
  t.save()
  
  token = oauth.Token(t.oauth_token, t.oauth_token_secret)
  token.set_verifier(t.oauth_verifier)
  consumer = oauth.Consumer(IS24_CONSUMER_KEY, IS24_COSUMER_SECRET)
  client = oauth.Client(consumer, token)
  
  resp, content = client.request(IS24_ACCESS_TOKEN_URL, "POST")
  
  if resp['status'] != '200':
      raise Exception("Invalid response %s." % resp['status'])

  t.oauth_token = dict(urlparse.parse_qsl(content))['oauth_token']
  t.oauth_token_secret = dict(urlparse.parse_qsl(content))['oauth_token_secret']
  t.authorized = True
  t.save()
  
  return HttpResponseRedirect('/')


def testIS24(request):
  t = OauthToken.objects.get(username=request.user.username)
  consumer = oauth.Consumer(IS24_CONSUMER_KEY, IS24_COSUMER_SECRET)
  token = oauth.Token(t.oauth_token, t.oauth_token_secret)
  p = ProxyInfo(socks.PROXY_TYPE_HTTP, "nokes.nokia.com", 8080)
  headers = {'Accept' :'application/json'}
  query_params = {
    'q': "berlin",
    'realEstateType': 'APARTMENT_BUY'
  }
  request_url = "http://rest.immobilienscout24.de/restapi/api/search/v1.0/region?%s" % urllib.urlencode(query_params)
  #client = oauth.Client(consumer, token=token, proxy_info=p)
  client = oauth.Client(consumer, token=token)
  resp, content = client.request(request_url, "GET", headers=headers)
  
  if resp['status'] != '200':
      raise Exception("Invalid response %s." % resp['status'])
  
  return HttpResponse(content, 'application/javascript')
  

def testSearch(request):
  t = OauthToken.objects.get(username=request.user.username)
  consumer = oauth.Consumer(IS24_CONSUMER_KEY, IS24_COSUMER_SECRET)
  token = oauth.Token(t.oauth_token, t.oauth_token_secret)
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
  }
  query_params = {
    #'q': "berlin",
    "realEstateType": "apartmentbuy",
    "geocodes": "1276003001046",
    "price": "-200000.00",
    "rented": False,
    "pagesize": 200,
  }
  request_url = "http://rest.immobilienscout24.de/restapi/api/search/v1.0/search/region?%s" % urllib.urlencode(query_params)
  client = oauth.Client(consumer, token=token)
  resp, content = client.request(request_url, "GET", headers=headers)
  
  if resp['status'] != '200':
      raise Exception("Invalid response %s." % resp['status'])
  
  return HttpResponse(content)

def testExpose(request):
  t = OauthToken.objects.get(username=request.user.username)
  consumer = oauth.Consumer(IS24_CONSUMER_KEY, IS24_COSUMER_SECRET)
  token = oauth.Token(t.oauth_token, t.oauth_token_secret)
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
  }
  request_url = "http://rest.immobilienscout24.de/restapi/api/search/v1.0/expose/67453896"
  client = oauth.Client(consumer, token=token)
  resp, content = client.request(request_url, "GET", headers=headers)
  
  if resp['status'] != '200':
      raise Exception("Invalid response %s." % resp['status'])
  
  return HttpResponse(content)
  
def isAuthorized(user):
  try:
    t = OauthToken.objects.get(username=user)
    return t.authorized
  except ObjectDoesNotExist:
    return False
    
def unauthorize(request):
  t = OauthToken.objects.get(username=request.user.username)
  t.unauthorize()
  return HttpResponseRedirect('/')


