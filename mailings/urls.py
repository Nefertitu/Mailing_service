from django.urls import path
from django.views.decorators.cache import cache_page

from mailings.apps import MailingsConfig


app_name = MailingsConfig.name

urlpatterns = [

]