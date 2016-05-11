import subprocess

import requests
from django.core import exceptions
from django.http import Http404, JsonResponse
from django.shortcuts import render
from lxml import etree

# Create your views here.

URL_TEMPLATE = 'https://api.data.gov/sam/v4/registrations/{duns}?api_key={api_key}'
API_KEY = 'kzDzoh62yMF47LxUM3RedIQe5h4RObsDoeQia1gK'


def get_sam(request, duns):
    url = URL_TEMPLATE.format(duns=duns, api_key=API_KEY)
    response = requests.get(url)
    if response.ok:
        sam = response.json()['sam_data']['registration']
        data = {'duns': duns,
                'address': sam['samAddress'],
                'name': sam['legalBusinessName'], }
    else:
        raise Http404(response.text)
        # should respect other status_codes like 406, though
    return JsonResponse(data)
