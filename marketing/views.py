''' rendering templates from requests related to marketing '''
from django.shortcuts import render

# Create your views here.

def infer_default_navigation(request, page_name):
  page = "marketing/{0}.html.haml".format(page_name)
  return render(request, page)
