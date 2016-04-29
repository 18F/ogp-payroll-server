from django.contrib import auth

import random
import factory
from . import models
from wage_determinations.factories import StateFactory, CountyFactory

class UserFactory(factory.DjangoModelFactory):

    class Meta:

        model = auth.get_user_model()
        exclude = ('raw_password',)

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    username = factory.Faker('user_name')
    raw_password = factory.Faker('password')
    password = factory.PostGenerationMethodCall('set_password', raw_password)
    is_active = True


class SuperUserFactory(UserFactory):

    is_superuser = True


class LocationFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Location

    street = factory.Faker('street_address')
    city = factory.Faker('city')
    # state = factory.SubFactory(StateFactory)
    # state = factory.LazyAttribute(lambda a: a.county.us_state)
    zip_code = factory.Faker('zipcode')
    county = factory.SubFactory(CountyFactory)


class ContractorFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Contractor

    cage = factory.Faker('credit_card_number')
    name = factory.Faker('company')
    address = factory.SubFactory(LocationFactory)
    created = factory.Faker('date')
    modified = factory.Faker('date')
    submitter = factory.SubFactory(UserFactory)


class ProjectFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Project

    project_number = factory.Faker('credit_card_number')
    name = factory.Faker('text', max_nb_chars=30)
    location = factory.SubFactory(LocationFactory)
    created = factory.Faker('date')
    modified = factory.Faker('date')


class PayrollFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Payroll

    payroll_number = factory.Faker('pyint')
    project = factory.SubFactory(ProjectFactory)
    contractor = factory.SubFactory(ContractorFactory)
    parent_contractor = factory.SubFactory(ContractorFactory)
    parent_payroll = None
    period_end = factory.Faker('date')
    date_submitted_to_parent = factory.Faker('date')
    date_submitted_to_gov = factory.Faker('date')
    signer_name = factory.Faker('name')
    submitter = factory.SubFactory(UserFactory)
    response = factory.Faker('sentence')


class WorkerFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Worker

    payroll = factory.SubFactory(PayrollFactory)
    name = factory.Faker('name')
    number_withholding_exceptions = factory.Faker('pyint')
    special = factory.Faker('word')


class PayrollLineFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.PayrollLine

    worker = factory.SubFactory(WorkerFactory)
    dol_rate = None
    dollars_per_hour = factory.Faker('pydecimal', left_digits=2, right_digits=2)
    response = factory.Faker('sentence')
    time_type = 'REG'


class DayFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Day

    payroll_line = factory.SubFactory(PayrollLineFactory)
    work_classification = factory.Faker('word')
    date = factory.Faker('date')
    hours = random.randint(2,8)


class DeductionFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Deduction

    payroll_line = factory.SubFactory(PayrollLineFactory)
    name = factory.Faker('word')
    dollars = factory.Faker('pydecimal', left_digits=2, right_digits=2)
