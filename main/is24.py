from django.utils import simplejson as json
from django.http import HttpResponse, HttpResponseRedirect
from auth.models import OauthToken
from auth.views import IS24_CONSUMER_KEY, IS24_COSUMER_SECRET
import oauth2 as oauth
from httplib2 import ProxyInfo
import urllib, socks
import ipdb;

IS24_RADIUS_SEARCH_URL = "http://rest.immobilienscout24.de/restapi/api/search/v1.0/search/radius?%s"

class IS24(object):
  """Retrieves IS24 objects via RESt API and returns the JSON object"""
  
  def __init__(self, request):
    self.key = IS24_CONSUMER_KEY
    self.secret = IS24_COSUMER_SECRET

    p = ProxyInfo(socks.PROXY_TYPE_HTTP, "nokes.nokia.com", 8080)
    
    t = OauthToken.objects.get(username=request.user.username)
    self.consumer = oauth.Consumer(self.key, self.secret)
    self.token = oauth.Token(t.oauth_token, t.oauth_token_secret)

    self.headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json'
    }

    if request.session.get('is24') == None:
      self.init_is24_settings(request)

    self.common_query_params = {
      "realEstateType": request.session['is24']['type'],
      "price": request.session['is24']['price_min'] + "-" + request.session['is24']['price_max'],
      "livingspace": request.session['is24']['space_min'] + "-" + request.session['is24']['space_max'],
      "numberofrooms": request.session['is24']['rooms_min'] + "-" + request.session['is24']['rooms_max'],
      "constructionyear": request.session['is24']['year_min'] + "-" + request.session['is24']['year_max'],
      "pagesize": 200,
    }

    if self.common_query_params['realEstateType'] == 'apartmentbuy':
      self.common_query_params['rented'] = request.session['is24']['rented']

    #self.client = oauth.Client(consumer=self.consumer, token=self.token, proxy_info=p)
    self.client = oauth.Client(consumer=self.consumer, token=self.token)

  def make_request(self, url, query_params):
    query_params.update(self.common_query_params)
    url = url % urllib.urlencode(query_params)
    resp, content = self.client.request(url, "GET", headers=self.headers)

    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    return content 

  def make_next_request(self, url):
    resp, content = self.client.request(url, "GET", headers=self.headers)

    if resp['status'] != '200':
        raise Exception("Invalid response %s." % resp['status'])

    return content 

  def init_is24_settings(request):
    request.session['is24'] = {}
    request.session['is24']['type'] = 'apartmentbuy'
    request.session['is24']['rented'] = False
    request.session['is24']['price_min'] = '0'
    request.session['is24']['price_max'] = '100000'
    request.session['is24']['year_min'] = '1900'
    request.session['is24']['year_max'] = '2012'
    request.session['is24']['space_min'] = '30'
    request.session['is24']['space_max'] = '80'
    request.session['is24']['rooms_min'] = '1'
    request.session['is24']['rooms_max'] = '3'
    request.session['is24']['radius'] = 1
    return


def change_is24_settings(request):

  if request.session.get('is24') == None:
    self.init_is24_settings(request)

  request.session['is24']['type'] = request.POST.get('type')
  if request.session['is24']['type'] == 'apartmentbuy':
    request.session['is24']['rented'] = True if request.POST.get('rented') else False
  else:
    request.session['is24']['rented'] = False
  request.session['is24']['price_min'] = request.POST.get('price_min')
  request.session['is24']['price_max'] = request.POST.get('price_max')
  request.session['is24']['year_min'] = request.POST.get('year_min')
  request.session['is24']['year_max'] = request.POST.get('year_max')
  request.session['is24']['space_min'] = request.POST.get('space_min')
  request.session['is24']['space_max'] = request.POST.get('space_max')
  request.session['is24']['rooms_min'] = request.POST.get('rooms_min')
  request.session['is24']['rooms_max'] = request.POST.get('rooms_max')
  request.session['is24']['radius'] = request.POST.get('radius')
  
  return HttpResponseRedirect('/')
  

    
def is24_radius_search(request):

  is24 = IS24(request)
  entries = []
  
  lat = request.GET['lat']
  lng = request.GET['lng']
  #radius = request.GET['radius']
  radius = request.session['is24']['radius']
  
  extra_query_params = {
    'geocoordinates': lat + ';' + lng + ';' + radius
  }

  content = is24.make_request(IS24_RADIUS_SEARCH_URL, extra_query_params)
  
    
  while True:

    c = json.loads(content)
    pageNumber = c["resultlist.resultlist"]["paging"]["pageNumber"]
    numberOfPages = c["resultlist.resultlist"]["paging"]["numberOfPages"]
    entries += c["resultlist.resultlist"]['resultlistEntries'][0]['resultlistEntry']
        
    if (pageNumber == numberOfPages):
      break
    else:
      next_url = c["resultlist.resultlist"]["paging"]["next"]["@xlink.href"]
      content = is24.make_next_request(next_url)
  
  json_response = json.dumps(entries)
  #ipdb.set_trace()
  return HttpResponse(json_response, 'application/javascript')
  

