from django.template import RequestContext
from django.shortcuts import render_to_response
from budget.models import Category, Month, Expenditure, UserProfile, RecurringEvent
from datetime import datetime, date, timedelta
from budget.forms import CategoryForm, ExpenditureForm, RecurringForm
from budget.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from registration.forms import RegistrationForm
from registration.backends.simple.views import RegistrationView as BaseRegistrationView
from registration.users import UserModel
from registration import signals
from forms import RegistrationFormTermsOfService



def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)

    month = get_current_month()

    if request.user.is_authenticated():
        user_viewing = request.user
        list_expenditures = get_expenditures(month, user_viewing)
        list_statistics = get_statistics(list_expenditures)
    else:
        user_viewing = False
        list_expenditures = False
        list_statistics = False

    now = date.today()

    # list_statistics = get_statistics(list_expenditures)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    if now.day % 10 == 1:
        context_dict = {
        'boldmessage': "Today is {0:%a}, the {0:%d}st of {0:%B}. You are looking at the expenditures of {0:%B}.".format(
            now)}
    elif now.day % 10 == 2:
        context_dict = {
        'boldmessage': "Today is {0:%a}, the {0:%d}nd of {0:%B}. You are looking at the expenditures of {0:%B}.".format(
            now)}
    elif now.day % 10 == 3:
        context_dict = {
        'boldmessage': "Today is {0:%a}, the {0:%d}rd of {0:%B}. You are looking at the expenditures of {0:%B}.".format(
            now)}
    else:
        context_dict = {
        'boldmessage': "Today is {0:%a}, the {0:%d}th of {0:%B}. You are looking at the expenditures of {0:%B}.".format(
            now)}

    context_dict["expenditures"] = list_expenditures

    context_dict["mes"] = month

    context_dict["user_node"] = user_viewing

    context_dict["statistics"] = list_statistics

    last_month = date(now.year, now.month, 1) - timedelta(days=1)
    last_month_link = str(last_month.year) + "/" + str(last_month.month)

    context_dict["date_links_back"] = last_month_link

    next_month = date(now.year, now.month, 28) + timedelta(days=7)
    next_month_link = str(next_month.year) + "/" + str(next_month.month)

    context_dict["date_links_next"] = next_month_link

    # # A HTTP POST?
    # if request.method == 'POST':
    # form = ExpenditureForm(request.POST)
    #
    #     # Have we been provided with a valid form?
    #     if form.is_valid():
    #         # Save the new category to the database.
    #         form.save(commit=True)
    #         return HttpResponseRedirect('')
    #     else:
    #         # The supplied form contained errors - just print them to the terminal.
    #         print form.errors
    # else:
    #     # If the request was not a POST, display the form to enter details.
    #     form = ExpenditureForm()

    if request.user.is_authenticated():
        if request.method == 'POST':
            form = ExpenditureForm(request.POST)

            if form.is_valid():
                # This time we cannot commit straight away.
                # Not all fields are automatically populated!
                page = form.save(commit=False)

                # Retrieve the associated Category object so we can add it.
                # Wrap the code in a try block - check if the category actually exists!
                page.gastos_author = user_viewing

                # With this, we can then save our new model instance.
                page.save()

                # Now that the page is saved, display the category instead.
                return HttpResponseRedirect('')
            else:
                print form.errors
        else:
            form = ExpenditureForm()
            form.fields['gastos_category'].queryset = Category.objects.filter(author=request.user).order_by(
                "name").all()

        context_dict["form"] = form

        context_dict["block_sidebar"] = True

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('budget/index.html', context_dict, context)


@login_required
def add_category(request):
    # Get the context from the request.
    context = RequestContext(request)

    user_viewing = request.user


    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            entry = form.save(commit=False)

            entry.author = user_viewing

            entry.save()

            # Now call the index() view.
            # The user will be shown the homepage.
            return HttpResponseRedirect('/budget/')
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    context_dict = {"form": form}
    context_dict ["block_sidebar"] = False

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('budget/add_category.html', context_dict, context)


@login_required
def add_expense(request):
    # Get the context from the request.
    context = RequestContext(request)

    user_viewing = request.user

    if request.method == 'POST':
        form = ExpenditureForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists!
            page.gastos_author = user_viewing

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return HttpResponseRedirect('/budget/')
        else:
            print form.errors
    else:
        form = ExpenditureForm()
        form.fields['gastos_category'].queryset = Category.objects.filter(author=request.user).order_by("name").all()

    context_dict = {"form": form}
    context_dict["block_sidebar"] = False

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('budget/add_expense.html', context_dict, context)


@login_required
def month_display(request, year_url, month_url):
    # Request our context from the request passed to us.
    context = RequestContext(request)

    print year_url
    print month_url

    # gat month and year from URL
    month_input = int(month_url)
    year_input = int(year_url)

    user_viewing = request.user

    month = get_specific_month(month_input, year_input)
    list_expenditures = get_expenditures(month, user_viewing)

    now = date(year_input, month_input, 1)

    list_statistics = get_statistics(list_expenditures)

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "You are looking at the expenditures of {0:%B} {0:%Y}.".format(now)}

    context_dict["expenditures"] = list_expenditures

    context_dict["mes"] = month

    context_dict["statistics"] = list_statistics

    last_month = date(now.year, now.month, 1) - timedelta(days=1)
    last_month_link = str(last_month.year) + "/" + str(last_month.month)

    context_dict["date_links_back"] = last_month_link

    next_month = date(now.year, now.month, 28) + timedelta(days=7)
    next_month_link = str(next_month.year) + "/" + str(next_month.month)

    context_dict["date_links_next"] = next_month_link

    context_dict["block_sidebar"] = False

    return render_to_response('budget/month.html', context_dict, context)


@login_required
def add_recurring(request):
    # Get the context from the request.
    context = RequestContext(request)

    user_viewing = request.user

    if request.method == 'POST':
        form = RecurringForm(request.POST)

        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit=False)

            # Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists!
            page.author = user_viewing

            # With this, we can then save our new model instance.
            page.save()

            # Now that the page is saved, display the category instead.
            return HttpResponseRedirect('/budget/')
        else:
            print form.errors
    else:
        form = RecurringForm()
        form.fields['category'].queryset = Category.objects.filter(author=request.user).order_by("name").all()

    context_dict = {"form": form}
    context_dict["block_sidebar"] = False

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('budget/add_recurring.html', context_dict, context)


class RegistrationView(BaseRegistrationView):
    template_name = 'budget/register.html'
    form_class = RegistrationFormTermsOfService

    def register(self, request, **cleaned_data):
        username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']
        UserModel().objects.create_user(username, email, password)


        new_user = authenticate(username=username, password=password)
        login(request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        UserProfile.objects.create(user=new_user,website=cleaned_data['website'],picture=cleaned_data['picture'])
        # else:
        #     UserProfile.objects.create(user=new_user,website=cleaned_data['website'])
        return new_user

    def get_success_url(self, request, user):
        return ('/budget', (), {})

# def register(request,**cleaned_data):
#     # Like before, get the request's context.
#     context = RequestContext(request)
#
#     # A boolean value for telling the template whether the registration was successful.
#     # Set to False initially. Code changes value to True when registration succeeds.
#     registered = False
#
#     # If it's a HTTP POST, we're interested in processing form data.
#     if request.method == 'POST':
#         # Attempt to grab information from the raw form information.
#         # Note that we make use of both UserForm and UserProfileForm.
#         user_form = RegistrationForm(data=request.POST)
#         profile_form = UserProfileForm(data=request.POST)
#
#         # If the two forms are valid...
#         if profile_form.is_valid():
#             # Save the user's form data to the database.
#             # user = user_form.save()
#
#             # # Now we hash the password with the set_password method.
#             # # Once hashed, we can update the user object.
#             # user.set_password(user.password)
#             # user.save()
#
#             # Now sort out the UserProfile instance.
#             # Since we need to set the user attribute ourselves, we set commit=False.
#             # This delays saving the model until we're ready to avoid integrity problems.
#             profile = profile_form.save(commit=False)
#             profile.user = self.cleaned_data['username']
#
#             # Did the user provide a profile picture?
#             # If so, we need to get it from the input form and put it in the UserProfile model.
#             if 'picture' in request.FILES:
#                 profile.picture = request.FILES['picture']
#
#             # Now we save the UserProfile model instance.
#             profile.save()
#
#             # Update our variable to tell the template registration was successful.
#             registered = True
#
#         # Invalid form or forms - mistakes or something else?
#         # Print problems to the terminal.
#         # They'll also be shown to the user.
#         else:
#             print profile_form.errors
#
#     # Not a HTTP POST, so we render our form using two ModelForm instances.
#     # These forms will be blank, ready for user input.
#     else:
#         user_form = RegistrationForm()
#         profile_form = UserProfileForm()
#
#     # Render the template depending on the context.
#     return render_to_response(
#         'budget/register.html',
#         {'user_form': user_form, 'profile_form': profile_form, 'registered': registered},
#         context)


def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/budget/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('budget/login.html', {}, context)


@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage.
    return HttpResponseRedirect('/budget/')

def about(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    return render_to_response('budget/about.html', {}, context)

@login_required
def profile(request):
    context = RequestContext(request)
    # cat_list = get_category_list()
    context_dict = {'cat_list': False}
    u = User.objects.get(username=request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render_to_response('budget/profile.html', context_dict, context)

def get_specific_month(m_in, y_in):
    month = int(m_in)
    year = int(y_in)
    m = Month.objects.get_or_create(month_date=month, year_date=year)[0]
    return m


def get_current_month():
    now = datetime.now()
    now_month = int(now.month)
    year = int(now.year)
    m = Month.objects.get_or_create(month_date=now_month, year_date=year)[0]
    return m


def get_list_days(m):
    days_list = []
    end = date(m.year_date, m.now_month + 1, 1) - timedelta(days=1)
    for number in range(1, int(end.day) + 1):
        days_list.append(date(m.year_date, m.now_month, number))
    return days_list


def get_expenditures(m, user_input):
    start = date(m.year_date, m.month_date, 1)
    end = date(m.year_date, m.month_date, 28) + timedelta(days=7)
    end = end - timedelta(days=end.day)
    expenditure_list = Expenditure.objects.filter(gastos_expense_date__range=[start, end],gastos_author=user_input).order_by("gastos_expense_date")
    return expenditure_list


def get_statistics(e):
    summation = 0.
    count = 0
    dates = {}
    for exp in e:
        count += 1
        summation += float(exp.gastos_value)
        if not dates.has_key(exp.gastos_expense_date):
            dates[exp.gastos_expense_date] = 1
        if dates.has_key(exp.gastos_expense_date):
            dates[exp.gastos_expense_date] += 1
    days = len(dates)
    if len(dates) != 0:
        average_per_entry = summation / count
        average_per_day = summation / days
    else:
        average_per_entry = 0
        average_per_day = 0
    statistics = {"avg_day": average_per_day, "avg_entry": average_per_entry, "sum": summation, "count_entry": count,
                  "dates": dates, "count_day": days}
    return statistics