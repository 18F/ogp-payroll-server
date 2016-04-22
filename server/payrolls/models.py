from django.db import models
from wage_determinations.models import State, County, Rate


class Location(models.Model):
    street = models.TextField()
    city = models.TextField()
    state = models.ForeignKey(State)
    zip_code = models.TextField()
    county = models.ForeignKey(County)


class Contractor(models.Model):
    cage = models.TextField()
    name = models.TextField()
    address = models.ForeignKey(Location)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    submitter = models.ForeignKey('auth.User', related_name='contractors')


class Project(models.Model):
    project_number = models.TextField()
    name = models.TextField()
    location = models.ForeignKey(Location)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)


class Payroll(models.Model):
    payroll_number = models.TextField()
    project = models.ForeignKey(Project)
    contractor = models.ForeignKey(Contractor)
    parent_contractor = models.ForeignKey(Contractor, blank=True, null=True, related_name='parent_contractor')
    parent_payroll = models.ForeignKey('Payroll', blank=True, null=True)
    period_end = models.DateField()
    date_submitted_to_parent = models.DateField(blank=True, null=True)
    date_submitted_to_gov = models.DateField(blank=True, null=True)
    signer_name = models.TextField()
    fringe_benefit_programs = models.BooleanField(default=False)
    fringe_benefit_cash = models.BooleanField(default=False)
    submitter = models.ForeignKey('auth.User', related_name='payrolls')
    response = models.TextField(blank=True)


class FringeException(models.Model):
    exception = models.TextField()
    explanation = models.TextField(blank=True)
    payroll = models.ForeignKey(Payroll)


class Worker(models.Model):
    payroll = models.ForeignKey(Payroll)
    name = models.TextField()
    number_withholding_exceptions = models.IntegerField(default=0)
    special = models.TextField(blank=True)  # for owner, salaried, etc.


class PayrollLine(models.Model):
    TIME_TYPE_CHOICES = [('REG', 'Regular'), ('OT', 'Overtime'), ]
    worker = models.ForeignKey(Worker)
    dol_rate = models.ForeignKey(Rate, blank=True)
    dollars_per_hour = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    response = models.TextField(blank=True)
    time_type = models.TextField(choices=TIME_TYPE_CHOICES)


class Day(models.Model):
    payroll_line = models.ForeignKey(PayrollLine)
    work_classification = models.TextField() # tie to WDOL!
    date = models.DateField()
    hours = models.FloatField()


class Deduction(models.Model):
    payroll_line = models.ForeignKey(PayrollLine)
    name = models.TextField()
    dollars = models.DecimalField(max_digits=6, decimal_places=2)
