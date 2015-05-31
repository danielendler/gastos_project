__author__ = 'sapiens'

from django.conf.urls import patterns, url
from budget import views

urlpatterns = patterns('',
        url(r'^$', views.index, name='index'),
        url(r'^add_category/$', views.add_category, name='add_category'),
        url(r'^add_expenditure/$', views.add_expense, name='add_expenditure'),
        url(r'^(?P<year_url>[0-9]{1,4})\/(?P<month_url>[0]?[1-9]|[1][0-2])/$', views.month_display, name='month_display'),
        url(r'^register/$', views.RegistrationView.as_view(), name='register'),
        url(r'^login/$', views.user_login, name='login'),
        url(r'^logout/$', views.user_logout, name='logout'),
        url(r'^about/$',views.about,name='about'),
        url(r'^profile/$', views.profile, name='profile'),
        url(r'^add_recurring/$', views.add_recurring, name='add_recurring'),

)