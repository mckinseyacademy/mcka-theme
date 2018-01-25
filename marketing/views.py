''' rendering templates from requests related to marketing '''
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import ugettext as _
from lib.authorization import permission_group_required
from api_client.group_api import PERMISSION_GROUPS
from .forms import TechSupportForm, SubscribeForm, EdxOfferForm


def infer_default_navigation(request, page_name):
    page = "marketing/{0}.haml".format(page_name.lower())
    try:
        template = get_template(page)
        if page_name == "programs" or page_name == "about" or page_name == "experience" or page_name == "edxoffer" or page_name == "fblf":
            return redirect('/')
        else:
            return render(request, page)

    except TemplateDoesNotExist:
        raise Http404


def contact(request, tech_support_form=TechSupportForm, subscribe_form=SubscribeForm):
    # data = {
    #     "support_form": tech_support_form(),
    #     "subscribe_form": subscribe_form(),
    # }

    # return render(request, 'marketing/contact.haml', data)
    return redirect('/')


@require_POST
def support(request, tech_support_form=TechSupportForm):
    form = tech_support_form(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, _('Thank you. We will get back to you as soon as possible.'))
    return redirect('/contact/')


@require_POST
def subscribe(request, subscribe_form=SubscribeForm):
    form = subscribe_form(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, _('Thank you for your interest in McKinsey Academy. We will keep you updated.'))
    return redirect('/contact/')


def styleguide(request):
    return render(request, 'marketing/styleguide.haml')
    # return redirect('/')


def edxoffer(request, offer_form=EdxOfferForm):
    # data = {
    #     "edx_offer_form": offer_form(),
    # }

    # return render(request, 'marketing/edxoffer.haml', data)
    return redirect('/')


def fblf(request):
    # return redirect('http://www.fblf.info')
    return redirect('/')
