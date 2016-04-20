from factory.django import DjangoModelFactory
import factory
from . import models

class StateFactory(DjangoModelFactory):

    class Meta:
        model = models.State

    name = factory.Faker('state_abbr')

class CountyFactory(DjangoModelFactory):

    class Meta:
        model = models.County

    name = factory.Faker('city')
    us_state = factory.SubFactory(StateFactory)


class WageDeterminationFactory(DjangoModelFactory):

    class Meta:
        model = models.WageDetermination

    code = factory.Faker('text', max_nb_chars=8)
    header = factory.Faker('paragraphs', nb=1)
    footer = factory.Faker('paragraphs', nb=2)
    published_date = factory.Faker('date')
