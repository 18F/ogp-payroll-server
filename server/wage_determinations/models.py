from django.db import models
from django.core import exceptions


class State(models.Model):
    name = models.TextField(unique=True)

    def __str__(self):
        return self.name

class County(models.Model):
    us_state = models.ForeignKey(State)
    name = models.TextField()

    def __str__(self):
        return '{self.name} county, {self.us_state.name}'.format(self=self)
    # need: compound unique state - county constraint

    @classmethod
    def get_or_make(cls, state_name, county_name):
        try:
            state = State.objects.get(name=state_name)
        except exceptions.ObjectDoesNotExist:
            state = State(name=state_name)
            state.save()
        try:
            county = cls.objects.get(name=county_name)
        except exceptions.ObjectDoesNotExist:
            county = cls(name=county_name)
            county.us_state = state
            county.save()
        return county



class WageDetermination(models.Model):
    code = models.TextField()
    header = models.TextField(blank=True)
    footer = models.TextField(blank=True)
    published_date = models.DateField()

    def __str__(self):
        return self.code


class Rate(models.Model):
    determination = models.ForeignKey(WageDetermination)
    dollars_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    fringe = models.TextField()
    group_qualifier = models.TextField(blank=True)

    construction_type = models.TextField()
    construction_subtype = models.TextField(blank=True)
    construction_qualifier = models.TextField(blank=True)
    construction_survey_qualifier = models.TextField(blank=True)

    occupation = models.TextField()
    occupation_qualifier = models.TextField(blank=True)
    rate_name = models.TextField(blank=True)
    rate_name_qualifier = models.TextField(blank=True)
    subrate_name = models.TextField(blank=True)
    subrate_name_qualifier = models.TextField(blank=True)

    counties = models.ManyToManyField(County)
    location_qualifier = models.TextField(blank=True)
    survey_location_qualifier = models.TextField(blank=True)

    def __str__(self):
        return '{determination}: {occupation}/{rate_name}/{subrate_name} ${dollars_per_hour}'.format(determination=self.determination, **self.__dict__)

def delete_all():
    County.objects.all().delete()
    State.objects.all().delete()
    Rate.objects.all().delete()
    WageDetermination.objects.all().delete()
