import re

from django.core import exceptions
from django.db import models

from pg_fts.fields import TSVectorField

comma = re.compile(r'\s*\,\s*')



class State(models.Model):
    abbrev = models.TextField(unique=True, db_index=True)
    name = models.TextField(unique=True, db_index=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_make(cls, abbrev, name):
        abbrev = abbrev.upper()
        name = name.upper()
        found = cls.objects.filter(abbrev=abbrev)
        if found:
            found = found.filter(name=name)
            if not found:
                raise cls.NotFoundError(
                    'abbrev {} does not match name {}'.format(abbrev, name))
            return found.first()
        return cls(abbrev=abbrev, name=name)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        self.abbrev = self.abbrev.upper()
        super(State, self).save(*args, **kwargs)


class County(models.Model):
    us_state = models.ForeignKey(State)
    name = models.TextField(blank=False, db_index=True)

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        super(County, self).save(*args, **kwargs)

    def __str__(self):
        return '{self.name} county, {self.us_state.name}'.format(self=self)
    # TODO need: compound unique state - county constraint

    @classmethod
    def get_or_make(cls, county):
        try:
            county = int(county)
            county = qu.get(pk=county)
            return county
        except ValueError:
            county = county.upper()
            if ',' in county:
                (county, state) = comma.split(county)
                qu = cls.objects.filter(name=county)
                state = (State.objects.filter(abbrev=state) or
                         State.objects.filter(name=state)).first()
                if not state:
                    raise State.NotFoundError(
                        'abbrev {} does not match name {}'.format(abbrev,
                                                                  name))
                qu = qu.filter(us_state=state)
                if not qu:
                    return cls(name=county, us_state=state)
            else:
                qu = cls.objects.filter(name=county)
            if len(qu) > 1:
                raise cls.MultipleObjectsReturned(
                    'county {} not unique'.format(county))
            return qu.first()


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

    # when a user needs to request a new determination
    # official_dol = models.BooleanField(default=True)

    def __str__(self):
        return '{determination}: {occupation}/{rate_name}/{subrate_name} ${dollars_per_hour}'.format(
            determination=self.determination,
            **self.__dict__)

    fts_index = TSVectorField(
        (('occupation', 'A'),
         ('rate_name', 'B'),
         ('subrate_name', 'B'),
         'occupation_qualifier',
         'rate_name_qualifier',
         'subrate_name_qualifier', ),
        dictionary='english')


def delete_all():
    County.objects.all().delete()
    State.objects.all().delete()
    Rate.objects.all().delete()
    WageDetermination.objects.all().delete()
