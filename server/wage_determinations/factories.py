import factory

from . import models


class StateFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.State

    abbrev = factory.Faker('state_abbr')
    name = factory.Faker('state')


class CountyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.County

    name = factory.Faker('city')
    # us_state = factory.SubFactory(StateFactory)
    us_state = factory.Iterator(models.State.objects.all())


class WageDeterminationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.WageDetermination

    name = 'ABC001'
    date = factory.Faker('date')
    county = factory.SubFactory(CountyFactory)
