from lxml import etree
import sys
from datetime import datetime
from pprint import pprint
from wage_determinations import models
from django.core.management.base import BaseCommand, CommandError
from django.core import exceptions

DEFAULT_FILENAME = '../../clement/wdol_dbra_wd_2016-01-14_02.00.07.xml'

def sibling_element(element, name):
    parent = element.getparent()
    sibling_name = parent.tag + name.capitalize()
    return parent.find(sibling_name)

def sibling_text(element, name):
    sibling = sibling_element(element, name)
    if sibling is not None:
        return sibling.text

def text(element):
    return ((element is not None) and element.text) or None

def dt(element):
    return datetime.strptime(element.text, '%Y-%m-%d').date()

def counties(det):
    abbrev = det.find('wageDeterminationCode').text[:2].upper()
    for county in det.xpath('location/state/countyIncludedList/countyName'):
        yield {'county': county.text,
               'state': county.iterancestors('state').__next__().find('stateName').text,
               'abbrev': abbrev,
              }

def construction_type_qualifier(el):
    type_list = el.iterancestors('constructionTypeList').__next__()
    qual = type_list.find('surveyConstructionTypeQualifier')
    return qual and qual.text

def construction_types(group):
    det = group.iterancestors('wageDetermination').__next__()
    any_subtypes = False
    for subtype in det.iter('subconstructionType'):
        construction_type = subtype.iterancestors('constructionType').__next__()
        yield {'subtype': subtype.text,
               'type': construction_type.find('constructionTypeName').text,
               'qualifier': text(group.find('constructionTypeQualifier')),
               'surveyQualifier': construction_type_qualifier(subtype)}
        any_subtypes = True
    if not any_subtypes:
        for contype in det.iter('constructionTypeName'):
            yield {'subtype': None, 'type': contype.text,
               'qualifier': text(group.find('constructionTypeQualifier')),
               'surveyQualifier': construction_type_qualifier(subtype)}


def extract_rates(filename=DEFAULT_FILENAME):
    tree = etree.parse(filename)
    for raw_det in tree.iter('wageDetermination'):
        det = {'code': raw_det.find('wageDeterminationCode').text,
              'published_date': dt(raw_det.find('publishedDate')),
              'header': text(raw_det.find('wageDeterminationHeader')),
              'footer': text(raw_det.find('wageDeterminationFooter')),
              'rates': [],
              }
        for rate_type in ('occupation', 'rate', 'subrate'):
            for rate in raw_det.iter(rate_type + 'Rate'):
                group = rate.iterancestors('wageGroup').__next__()
                for construction_type in construction_types(group):
                    result = {
                              'location_qualifier': group.find('locationQualifier').text,
                              # TODO: Use loc qualifier to further filter the county list
                              'survey_location_qualifier': raw_det.find('surveyLocationQualifier').text,
                              'counties': list(counties(raw_det)),
                              'effective_date': dt(group.find('effectiveDate')),
                              'rate': rate.text,
                              'fringe': sibling_text(rate, 'fringe'),
                              'occupation': {rate_type: {
                                             'title': sibling_text(rate, 'title'),
                                             'qualifier': sibling_text(rate, 'qualifier'),
                                            },},
                              'construction_type': construction_type,
                              'groupQualifier': sibling_text(group, 'groupQualifier'),
                    }
                    for parent_rate_type in ('occupation', 'rate'):
                        if rate_type != parent_rate_type:
                            try:
                                parent = rate.iterancestors(parent_rate_type).__next__()
                                result['occupation'][parent_rate_type] = {
                                    'title': text(parent.find(parent_rate_type + 'Title')),
                                    'qualifier': text(parent.find(parent_rate_type + 'Qualifier')),
                                    'groupQualifier': text(parent.find(parent_rate_type + 'GroupQualifier')),
                                     }
                            except StopIteration:
                                # That level "up" does not exist, so skip
                                pass
                    det['rates'].append(result)
        yield det


# because of wagegroup, locations attach downward to rates
# construction types -> wageDeterminationCode

# locationQualifiers attach to wageGroups - so must locs
# and constructionTypeQualifiers
# and effective dates

# basically, no information can be pushed up to the
# wage determination itself


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = DEFAULT_FILENAME
    for rate in extract_rates(filename):
        pprint(rate)

class Command(BaseCommand):

    """
    def add_arguments(self, parser):
        parser.add_argument('filenames', nargs='+', type=str)
    """

    def handle(self, *args, **options):
        models.delete_all()
        if not args:
            args = [DEFAULT_FILENAME, ]
        for filename in args:
            for det in extract_rates(filename):
                try:
                    determination = models.WageDetermination.objects.get(code=det['code'])
                except exceptions.ObjectDoesNotExist:
                    determination = models.WageDetermination(
                        code=det['code'],
                        published_date=det['published_date'],
                        header=det['header'] or '',
                        footer=det['footer'] or '',)
                    determination.save()
                print(determination)
                for rate in det['rates']:
                    rate_instance = models.Rate(
                        determination=determination,
                        dollars_per_hour=rate['rate'],
                        fringe=rate['fringe'] or '',
                        group_qualifier=rate['groupQualifier'] or '',
                        construction_type=rate['construction_type']['type'] or '',
                        construction_subtype=rate['construction_type']['subtype'] or '',
                        construction_qualifier=rate['construction_type']['qualifier'] or '',
                        construction_survey_qualifier=rate['construction_type']['surveyQualifier'] or '',
                        occupation=rate['occupation']['occupation']['title'] or '',
                        occupation_qualifier=rate['occupation']['occupation']['qualifier'] or '',
                        location_qualifier=rate['location_qualifier'] or '',
                        survey_location_qualifier=rate['survey_location_qualifier'] or '',
                        )
                    rate_instance.save()
                    if 'rate' in rate['occupation']:
                        rate_instance.rate_name=rate['occupation']['rate']['title'] or ''
                        rate_instance.rate_name_qualifier=rate['occupation']['rate']['qualifier'] or ''
                        if 'subrate' in rate['occupation']:
                            rate_instance.subrate_name=rate['occupation']['subrate']['title'] or ''
                            rate_instance.subrate_name_qualifier=rate['occupation']['subrate']['qualifier'] or ''
                    for raw_county in rate['counties']:
                        county = models.County.get_or_make(raw_county['abbrev'], raw_county['state'], raw_county['county'])
                        rate_instance.counties.add(county)
                        print(county)
                    rate_instance.save()
                    print (rate_instance)
