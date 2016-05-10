import subprocess

import requests
from django.http import JsonResponse
from django.shortcuts import render
from lxml import etree

URL_TEMPLATE = 'https://www.fpds.gov/ezsearch/FEEDS/ATOM?FEEDNAME=PUBLIC&q=PIID:{piid}'


def get_fpds(request, contract_no):
    data = {'soup': contract_no}
    url = URL_TEMPLATE.format(piid=contract_no)
    rslt = subprocess.check_output(['/usr/bin/curl', '-v', url])
    return JsonResponse(parse_fpds_atom(rslt))


NS_STEM = '{http://www.fpdsng.com/FPDS}'


def parse_fpds_atom(raw):
    tree = etree.fromstring(raw)
    loc = tree.iter('{NS_STEM}principalPlaceOfPerformance'.format(
        NS_STEM=NS_STEM)).__next__()
    us_state = loc.find('{NS_STEM}stateCode'.format(NS_STEM=NS_STEM)).text
    location_code = loc.find('{NS_STEM}locationCode'.format(NS_STEM=
                                                            NS_STEM)).text
    data = {'state': us_state, 'location_code': location_code, }
    return data
