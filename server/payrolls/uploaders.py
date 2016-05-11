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
        if 'project_id' not in data:
            raise exceptions.ValidationError('project_id missing')
        contractor = None
        for line in csv.reader(raw.decode('utf8').splitlines()):
            if not contractor:
                address_data = self.extract('Address', line)
                address = models.Location(**address_data)
                address.save()

                contractor_data = self.extract('Contractor', line)
                contractor = models.Contractor.objects.filter(
                    name=contractor_data['name']).filter(
                        address=address).first()
                if not contractor:
                    contractor = models.Contractor(
                        name=contractor_data['name'],
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
            worker = models.Worker.objects.filter(payroll=payroll).filter(
                name=worker_data['name']).first()
            if not worker:
                worker = models.Worker(payroll=payroll, **worker_data)
                worker.save()

            payroll_line_data = self.extract('PayrollLine', line)
            payroll_line = models.PayrollLine(worker=worker,
                                              **payroll_line_data)
            payroll_line.save()

            day_data = self.extract('Day', line)
            for (days_back, hours) in enumerate(reversed(day_data['hours'])):
                day = models.Day(payroll_line=payroll_line,
                                 job_name=day_data['job_name'],
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


def until_digits(txt):
    return re.split('\d', txt)[0]


def decimal_or_zero(txt):
    return Decimal(txt or 0)


class AmgUploader(Uploader):

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
                   'name': (28, until_digits),
               },
               'Day': {
                   'job_name': 30,
                   'hours': ('31-38',
                             decimal_or_zero, ),
               },
               'PayrollLine': {
                   'time_type': 40,
                   'dollars_per_hour': (41,
                                        decimal_or_zero, ),
               }, }


def upload(request, raw_data):
    upload_exceptions = {}
    for uploader in (AmgUploader, ):
        try:
            payroll = uploader(request).upload(raw_data, request.data)
            return payroll
        except Exception as e:
            upload_exceptions[uploader.name] = str(e)
    raise exceptions.ValidationError(upload_exceptions)
