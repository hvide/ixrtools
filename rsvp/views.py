from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from .modules.rsvpclient import RsvpClient

from pprint import pprint

from .forms import TextForm

# Create your views here.
IXR_APY_KEY = ""
IXR_BASE_URL = ""


class HomePageView(TemplateView):
    template_name = "rsvp/home.html"


class SearchPathPageView(TemplateView):
    template_name = "rsvp/search_path.html"


def get_path(request):

    search_string = request.POST.get('rsvp_path_name')
    rsvp = RsvpClient(IXR_APY_KEY, IXR_BASE_URL, verify=False)
    result = rsvp.get_rsvp_path_info(search_string)

    context = {
        'result': result,
        'search_string': search_string
    }

    return render(request, 'rsvp/search_path.html', context)


def create_path(request):

    rsvp_path_name_box = request.POST.get('rsvp_path_name')
    host_input_box = request.POST.get('host_input_box')
    reversed_box = request.POST.get('reversed')
    rsvp = RsvpClient(IXR_APY_KEY, IXR_BASE_URL, verify=False)

    context = dict()

    if host_input_box is not None:
        host_input_box = host_input_box.split("\n")
        hosts = [x.strip() for x in host_input_box]

        if reversed_box:
            hosts.reverse()

        result = rsvp.create_rsvp_path(rsvp_path_name_box, hosts)

        context = {
            'reversed': reversed_box,
            'hosts': hosts,
            'result': result
        }
        # pprint(context)

    return render(request, 'rsvp/create_path.html', context)

