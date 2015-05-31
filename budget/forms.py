from django import forms
from django.db import models
from budget.models import Category, Month, Expenditure, UserProfile, RecurringEvent
from datetime import date
from django.contrib.auth.models import User
from datetimewidget.widgets import DateWidget
from registration.forms import RegistrationForm
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login

from registration import signals
from registration.users import UserModel



class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Name")
    author = forms.Select()


    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Category
        exclude = ['author']


class ExpenditureForm(forms.ModelForm):
    dateTimeOptions = {
        # 'format': 'dd/mm/yyyy',
        'autoclose': True,
        'todayHighlight': True,
        'clearBtn': True,
    }

    gastos_name = forms.CharField(max_length=128, help_text="Name", required=False)
    gastos_created_date = forms.DateField(widget=forms.HiddenInput, initial=date.today())
    gastos_expense_date = forms.DateField(initial=date.today(), help_text="Date",
                                          widget=DateWidget(options=dateTimeOptions, bootstrap_version=2, usel10n=True))
    gastos_category = forms.Select()
    gastos_value = forms.DecimalField(max_digits=10, help_text="Value", widget=forms.TextInput(
        {'placeholder': 123.43, 'class': 'required', 'type': 'tel', 'required': True}))
    # gastos_author = forms.Select()

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Expenditure

        # What fields do we want to include in our form?
        # This way we don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them...
        # Here, we are hiding the foreign key.
        fields = ('gastos_name', 'gastos_expense_date', 'gastos_category', 'gastos_value')

    def __init__(self, *args, **kwargs):
        super(ExpenditureForm, self).__init__(*args, **kwargs)
        self.fields['gastos_expense_date'].localize = True
        self.fields['gastos_expense_date'].widget.is_localized = True


class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Please enter a username.")
    email = forms.CharField(help_text="Please enter your email.")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter a password.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(help_text="Please enter your website.", required=False)
    picture = forms.ImageField(help_text="Select a profile image to upload.", required=False)

    class Meta:
        model = UserProfile
        fields = ['website', 'picture']


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.

    """
    website = forms.URLField(required=False)
    picture = forms.ImageField(required=False)

    # tos = forms.BooleanField(widget=forms.CheckboxInput,
    #                          label=_('I have read and agree to the Terms of Service'),
    #                          error_messages={'required': _("You must agree to the terms to register")})


class RecurringForm(forms.ModelForm):
    dateTimeOptions = {
        # 'format': 'dd/mm/yyyy',
        'autoclose': True,
        'todayHighlight': True,
        'clearBtn': True,
    }
    category = forms.Select()
    value = forms.DecimalField(max_digits=10, help_text="Value", widget=forms.TextInput(
            {'placeholder': 123.43, 'class': 'required', 'type': 'tel', 'required': True}))
    recurrence = forms.Select()
    in_or_outcome = forms.Select()
    date_from = forms.DateField(initial=date.today(), help_text="From Date",
                                              widget=DateWidget(options=dateTimeOptions, bootstrap_version=2, usel10n=True))
    date_to = forms.DateField(required=False,help_text="To Date",
                                              widget=DateWidget(options=dateTimeOptions, bootstrap_version=2, usel10n=True))
    annotation = forms.Textarea()

    class Meta:
        # Provide an association between the ModelForm and a model
        model = RecurringEvent

        # What fields do we want to include in our form?
        # This way we don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them...
        # Here, we are hiding the foreign key.
        fields = ("category", "value", "recurrence", "in_or_outcome", "date_from", "date_to", "annotation")

    def __init__(self, *args, **kwargs):
        super(RecurringForm, self).__init__(*args, **kwargs)
        self.fields['date_from'].localize = True
        self.fields['date_from'].widget.is_localized = True
        self.fields['date_to'].localize = True
        self.fields['date_to'].widget.is_localized = True