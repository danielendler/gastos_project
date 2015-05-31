from django.db import models
from datetime import datetime
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=128)
    author = models.ForeignKey(User)

    def clean(self):
        self.name = self.name.capitalize()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ("name", "author")

class Month(models.Model):
    MONTHS_CHOICES=(
        (1,"Jan"),
        (2,"Fev"),
        (3,"Mar"),
        (4,"Apr"),
        (5,"May"),
        (6,"Jun"),
        (7,"Jul"),
        (8,"Aug"),
        (9,"Sep"),
        (10,"Oct"),
        (11,"Nov"),
        (12,"Dec"),
    )
    average = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    days_passed = models.IntegerField(default=0)
    now = datetime.now()
    now_month = int(now.month)
    year = int(now.year)
    month_date = models.IntegerField(choices=MONTHS_CHOICES,default=now_month)
    year_date = models.IntegerField(default=year)

    class Meta:
        unique_together = ("month_date", "year_date")

    def __unicode__(self):
        name = str(self.month_date)+"/"+str(self.year_date)
        return name

# (?P<year>[0-9]{1,4})\/(?P<month>[0]?[1-9]|[1][0-2])$

class Expenditure(models.Model):

    now = datetime.now()
    now_month = int(now.month)
    now_year = int(now.year)

    name = str(now_month)+"/"+str(now_year)

    gastos_name = models.CharField(max_length=128,blank=True)
    gastos_created_date = models.DateField(auto_now_add=True)
    gastos_expense_date = models.DateField(default=datetime.now)
    gastos_category = models.ForeignKey("Category",help_text="Category",blank=True, null=True)
    # gastos_mes = models.ForeignKey(Month,default=name,blank=True, null=True,editable=False)
    gastos_value = models.DecimalField(decimal_places=2,max_digits=100)
    gastos_author = models.ForeignKey(User)

    def __unicode__(self):
        return self.gastos_name

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username

class RecurringEvent(models.Model):

    CHOICES=(
        (1,"Monthly"),
        (2,"Weekly"),
        (3,"Daily")
    )

    TYPE=(
        (1,"Expense"),
        (2,"Income"),
        (3,"Budget")
    )
    category = models.ForeignKey("Category",help_text="Category",blank=True, null=True)
    value = models.DecimalField(decimal_places=2,max_digits=100)
    recurrence = models.IntegerField(choices=CHOICES,default=1)
    in_or_outcome = models.IntegerField(choices=TYPE,default=2)
    date_from = models.DateField(default=datetime.now)
    date_to = models.DateField(blank=True,null=True)
    annotation = models.TextField(blank=True)
    author = models.ForeignKey(User)

    def __unicode__(self):
        name = str(self.category)+" "+str(self.in_or_outcome)
        return name