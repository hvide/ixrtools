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
    pprint(context)
    return render(request, 'rsvp/results.html', context)
#
# def search_path(request):
#     form = TextForm(request.GET)
#     print(form.__dict__)
#     context = {'form': form}
#     return render(request, 'rsvp/results.html', context)
