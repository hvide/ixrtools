from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from .modules.rsvpclient import RsvpClient

import os
from dotenv import load_dotenv

from pprint import pprint

from .forms import TextForm

# Create your views here.
load_dotenv()
IXR_APY_KEY = os.getenv('IXR_APY_KEY')
IXR_BASE_URL = os.getenv('IXR_BASE_URL')


class HomePageView(TemplateView):
    template_name = "rsvp/home.html"


class SearchPathPageView(TemplateView):
    template_name = "rsvp/search_path.html"


def get_path(request):

    search_string = request.POST.get('rsvp_path_name')
    rsvp = RsvpClient(IXR_APY_KEY, IXR_BASE_URL, verify=False)
    data = rsvp.get_rsvp_path_info(search_string)

    context = {
        'status': data["status"],
        'data': data,
        # 'search_string': search_string
    }
    # pprint(context)
    return render(request, 'rsvp/search_path.html', context)


def create_path(request):

    rsvp_destination_box = request.POST.get('rsvp_destination')
    rsvp_lsp_name_box = request.POST.get('rsvp_lsp_name')
    rsvp_path_name_box = request.POST.get('rsvp_path_name')
    host_input_box = request.POST.get('host_input_box')
    primary_box = request.POST.get('primary')
    reversed_box = request.POST.get('reversed')
    rsvp = RsvpClient(IXR_APY_KEY, IXR_BASE_URL, verify=False)

    context = dict()

    if host_input_box is not None:
        host_input_box = host_input_box.split("\n")
        hosts = [x.strip() for x in host_input_box]

        if reversed_box:
            hosts.reverse()

        result = []

        if rsvp_lsp_name_box and rsvp_destination_box:
            result = result + rsvp.create_rsvp_lsp(rsvp_lsp_name_box, rsvp_destination_box)

        result = result + rsvp.create_rsvp_path(rsvp_path_name_box, hosts)

        if rsvp_lsp_name_box and rsvp_destination_box:
            result = result + rsvp.attach_path_to_lsp(rsvp_lsp_name_box, rsvp_path_name_box, primary_box)

        context = {
            'reversed': reversed_box,
            'hosts': hosts,
            'result': result
        }

        # pprint(context, width=160)

    return render(request, 'rsvp/create_path.html', context)

