import datetime

from django.db import models
from django.utils.dateparse import parse_date

from wage_determinations.models import County, Rate, State


class Location(models.Model):
    street = models.TextField()
    city = models.TextField()
    state = models.TextField()
    zip_code = models.TextField()
    county = models.ForeignKey(County, null=True)

    @classmethod
    def make(cls, data):
        county = County.get_or_make(data['county'])
        location = cls(street=data['street'],
                       city=data['city'],
                       zip_code=data['zip_code'],
                       county=county)
        return location


class Contractor(models.Model):
    cage = models.TextField(db_index=True)  # uniqueness?  Versions...
    name = models.TextField(db_index=True)
    address = models.ForeignKey(Location)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    submitter = models.ForeignKey('auth.User', related_name='contractors')

    @classmethod
    def make(cls, data):
        location = Location.make(data['location'])

        county = County.get_or_make(data['county'])
        location = cls(street=data['street'],
                       city=data['city'],
                       zip_code=data['zip_code'],
                       county=county)
        return location


class Project(models.Model):
    project_number = models.TextField()
    contract_number = models.TextField()
    name = models.TextField()
    location = models.ForeignKey(Location)
    start = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    dol_rates = models.ManyToManyField(Rate)


class ProjectContractor(models.Model):
    project = models.ForeignKey(Project, null=False)
    contractor = models.ForeignKey(Contractor, null=False)
    subcontracting_from = models.ForeignKey(Contractor,
                                            related_name='subcontractor',
                                            null=True)


class Worker(models.Model):
    contractor = models.ForeignKey(Contractor)
    identifier = models.TextField(
        db_index=True)  # contractor-assigned ID number
    name = models.TextField()
    number_withholding_exceptions = models.IntegerField(default=0)
    special = models.TextField(blank=True)  # for owner, salaried, etc.


class Payroll(models.Model):
    payroll_number = models.TextField()
    uploaded_at = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=True)
    status = models.TextField(null=True)
    project = models.ForeignKey(Project)
    contractor = models.ForeignKey(Contractor)
    parent_contractor = models.ForeignKey(Contractor,
                                          blank=True,
                                          null=True,
                                          related_name='parent_contractor')
    parent_payroll = models.ForeignKey('Payroll',
                                       blank=True,
                                       null=True,
                                       related_name='child_payroll')
    period_end = models.DateField()
    date_submitted_to_parent = models.DateField(blank=True, null=True)
    date_submitted_to_gov = models.DateField(blank=True, null=True)
    signer_name = models.TextField()
    """`fringe_benefit_programs` and `fringe_benefit_cash`
    are for recording an employer's answers to assertion 4(c)
    in WH-347 Certified Payroll Exercise."""
    fringe_benefit_programs = models.BooleanField(default=False)
    fringe_benefit_cash = models.BooleanField(default=False)
    submitter = models.ForeignKey('auth.User', related_name='payrolls')
    response = models.TextField(blank=True)
    workers = models.ManyToManyField(to=Worker, through='Workweek')

    def mark_others_noncurrent(self):
        for existing in Payroll.objects.filter(project=self.project,
                                               contractor=self.contractor,
                                               period_end=self.period_end):
            if existing.id != self.id:
                existing.is_current = False
                existing.save()

    def clone(self, payroll_number, period_end):
        old = self.workweek_set.all()
        self.pk = None
        self.payroll_number = payroll_number
        if not isinstance(period_end, datetime.date):
            period_end = parse_date(period_end)
        self.period_end = period_end
        self.save()
        for workweek in old:
            self.workweek_set.add(workweek.clone())
        self.save()
        return self


class Workweek(models.Model):
    """All data on one payroll for each worker."""
    payroll = models.ForeignKey(Payroll)
    worker = models.ForeignKey(Worker)
    number_withholding_exceptions = models.IntegerField(default=0)
    special = models.TextField(blank=True)  # for owner, salaried, etc.

    def clone(self):
        old = self.payrollline_set.all()
        self.pk = None
        self.save()
        for payrollline in old:
            self.payrollline_set.add(payrollline.clone())
        self.save()
        return self


class PayrollUpload(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey('auth.User', to_field='id')
    payroll = models.ForeignKey(Payroll, blank=True)
    datafile = models.FileField()


class FringeException(models.Model):
    """List of exceptions and explanations from the
    assertions in `Payroll.fringe_benefit_programs`
    and `Payroll.fringe_benefit_cash`.
    """
    exception = models.TextField()
    explanation = models.TextField(blank=True)
    payroll = models.ForeignKey(Payroll)


class Withholding(models.Model):
    purpose = models.TextField(blank=False)  # Tax, FICA, etc.
    dollars = models.DecimalField(blank=True, max_digits=6, decimal_places=2)
    workweek = models.ForeignKey(Workweek)


class PayrollLine(models.Model):
    REGULAR = 'REG'
    OVERTIME = 'OT'
    # TIME_TYPE_CHOICES = ((REGULAR, 'Regular'), (OVERTIME, 'Overtime'), )

    workweek = models.ForeignKey(Workweek)
    job_name = models.TextField()
    work_classification = models.TextField(blank=True, )  # tie to WDOL!
    dol_rate = models.ForeignKey(Rate, null=True, blank=True)
    dollars_per_hour = models.DecimalField(blank=True,
                                           max_digits=6,
                                           decimal_places=2)
    response = models.TextField(blank=True)
    # time_type = models.CharField(max_length=3, choices=((REGULAR, 'Regular'), (OVERTIME, 'Overtime'), ))
    time_type = models.TextField(default='REG')

    def clone(self):
        days = self.day_set.all()
        linequantities = self.linequantity_set.all()
        self.pk = None
        self.save()
        for (days_back, day) in enumerate(reversed(days)):
            new_day = day.clone()
            new_day.date = self.workweek.payroll.period_end - datetime.timedelta(
                days_back)
            new_day.save()
            self.day_set.add(new_day)
        for linequantity in linequantities:
            self.linequantity_set.add(linequantity.clone())
        self.save()
        return self


class Day(models.Model):
    payroll_line = models.ForeignKey(PayrollLine)
    date = models.DateField()
    hours = models.FloatField()

    class Meta:
        ordering = ('date', )

    def clone(self):
        self.pk = None
        self.save()
        return self


class LineQuantity(models.Model):
    payroll_line = models.ForeignKey(PayrollLine)
    type = models.TextField()  # 'Deduction' or 'Fringe'
    name = models.TextField()
    dollars = models.DecimalField(max_digits=6, decimal_places=2)

    def clone(self):
        self.pk = None
        self.save()
        return self
