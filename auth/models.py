from django.db import models
from django.contrib.auth.models import User

class OauthToken(models.Model):
  username = models.CharField(max_length=30, primary_key=True)
  #request_token = models.CharField(max_length=200)
  oauth_token = models.CharField(max_length=200) #oauth_token
  oauth_token_secret = models.CharField(max_length=200)
  oauth_verifier = models.CharField(max_length=10) # oauth_verifier
  authorized = models.BooleanField(default=False)
  
  def access_token(self):
    """ Returns the access token """
    return self.access_token
    
  def is_authorized(self):
    return self.authorized
    
  def unauthorize(self):
    self.authorized = False
    self.save()
    return self.authorized