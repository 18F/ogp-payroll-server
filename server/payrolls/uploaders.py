"""
Uploader classes for generation of payroll data from CSV uploads.

Because each program generating CSVs may arrange its data differently,
``Uploader`` should be subclassed for each structure to be supported.
"""
import csv
import datetime
import re
from decimal import Decimal

import dateutil.parser
import usaddress
from django.db import transaction
from rest_framework import exceptions

from . import models


class Uploader(object):
    def __init__(self, request):
        self.request = request
        self.uploading_user = request.user

    _number_range = re.compile('^\s*(\d+)\s*\-\s*(\d+)\s*$')

    def _column_numbers(self, raw):
        try:
            result = int(raw)
            return (result, )
        except (TypeError, ValueError):
            range_match = self._number_range.search(raw)
            return range(*map(int, range_match.groups()))

    def extract(self, node, line):
        """Applies self.sources to extract data from line.

        Assumes that `self.sources` containts, for each `node`, >= 1 of:

            - column number or range to extract data from
            - function to call with column data
            - any additional arguments
        """
        result = {}
        for (name, source) in self.sources[node].items():
            if isinstance(source, tuple):
                (col_no, func, *args) = source
                result[name] = [func(line[c], *args)
                                for c in self._column_numbers(col_no)]
            else:
                result[name] = [line[c] for c in self._column_numbers(source)]
            if len(result[name]) == 1:
                result[name] = result[name][0]
        return result

    @transaction.atomic
    def upload(self, raw, data):
        for requirement in ('project_id', 'cage'):
            if requirement not in data:
                raise exceptions.ValidationError('{} missing'.format(
                    requirement))
        contractor = None
        for line in csv.reader(raw.decode('utf8').splitlines()):
            if not contractor:
                address_data = self.extract('Address', line)
                address = models.Location(**address_data)
                address.save()

                contractor_data = self.extract('Contractor', line)
                contractor = models.Contractor.objects.filter(
                    name=contractor_data['name']).filter(
                        address=address).filter(cage=data['cage']).first()
                if not contractor:
                    contractor = models.Contractor(
                        name=contractor_data['name'],
                        cage=data['cage'],
                        address=address,
                        submitter=self.uploading_user)
                    contractor.save()

                payroll_data = self.extract('Payroll', line)
                payroll = models.Payroll(contractor=contractor,
                                         submitter=self.uploading_user,
                                         **payroll_data)
                payroll.project_id = data['project_id']
                payroll.save()
                payroll.mark_others_noncurrent()

            worker_data = self.extract('Worker', line)
            if worker_data['identifier']:
                match_field = 'identifier'
            else:
                match_field = 'name'
            worker = models.Worker.objects.filter(
                contractor=contractor).filter(
                    name=worker_data[match_field]).first()
            if not worker:
                worker = models.Worker(contractor=contractor, **worker_data)
                worker.save()

            workweek = models.Workweek(payroll=payroll, worker=worker)
            workweek.save()
            payroll.workweek_set.add(workweek)

            payroll_line_data = self.extract('PayrollLine', line)
            payroll_line = models.PayrollLine(workweek=workweek,
                                              **payroll_line_data)
            payroll_line.save()

            day_data = self.extract('Day', line)
            for (days_back, hours) in enumerate(reversed(day_data['hours'])):
                day = models.Day(payroll_line=payroll_line,
                                 date=payroll.period_end - datetime.timedelta(
                                     days=days_back),
                                 hours=float(hours or 0))
                day.save()
        return payroll


_name_from_address_splitter = re.compile(r'(.+?)(\d.*)')


def extract_name_and_address(txt):
    match = _name_from_address_splitter.search(txt)
    result = {'street': '', 'name': match.group(1)}
    parsed = usaddress.parse(match.group(2))
    """usaddress parses to many pieces, most of which should be
       reassembled into `street`."""
    for (word, word_type) in parsed:
        if word_type == 'PlaceName':
            result['city'] = word
        elif word_type == 'StateName':
            result['state'] = word
        elif word_type == 'ZipCode':
            result['zip_code'] = word
        else:
            result['street'] += word + ' '
    return {r: result[r].strip().strip(',') for r in result}


def from_address_line(txt, desired):
    full_address = extract_name_and_address(txt)
    return full_address[desired]


def word_number(txt, idx, data_type=str):
    word = txt.split()[idx]
    if data_type == datetime.date:
        return dateutil.parser.parse(word)
    return data_type(word)


def until_pattern(txt, pattern):
    return re.split(pattern, txt)[0]


def extract_pattern(txt, pattern):
    return re.search(pattern, txt).group(0)


def decimal_or_zero(txt):
    return Decimal(txt or 0)


class AmgUploader(Uploader):
    """
    Uploader for the format represented by the
    sample data at sample_data/amg_payroll.csv

    Note: the CSVs from AMG omit all tax and deduction info!"""

    name = 'AMG'

    sources = {'Payroll':
               {'date_submitted_to_gov': (1, dateutil.parser.parse),
                'payroll_number': (6, word_number, -1, str),
                'period_end': (8, word_number, -1, datetime.date), },
               'Contractor': {
                   'name': (2, from_address_line, 'name'),
               },
               'Address': {
                   'street': (2, from_address_line, 'street'),
                   'city': (2, from_address_line, 'city'),
                   'state': (2, from_address_line, 'state'),
                   'zip_code': (2, from_address_line, 'zip_code'),
               },
               'Worker': {
                   'name': (28, until_pattern, r'\d'),
                   'identifier': (28, extract_pattern, r'\d+'),
               },
               'Day': {
                   'hours': ('31-38',
                             decimal_or_zero, ),
               },
               'PayrollLine': {
                   'job_name': 30,
                   'time_type': 40,
                   'dollars_per_hour': (41,
                                        decimal_or_zero, ),
               }, }


def upload(request, raw_data):
    """
    Generate payroll data from a web request with a .csv upload.

    At present, simply tries each available Uploader class, accepting the
    first one which passes without data validation errors.  As ``Uploader``
    subclasses are added, a more sophisticated format recognizer should be
    added.
    """
    upload_exceptions = {}
    for uploader in (AmgUploader, ):
        try:
            payroll = uploader(request).upload(raw_data, request.data)
            return payroll
        except Exception as e:
            upload_exceptions[uploader.name] = str(e)
    raise exceptions.ValidationError(upload_exceptions)
