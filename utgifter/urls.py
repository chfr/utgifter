from django.urls import re_path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    re_path('^login/$', auth_views.LoginView.as_view(), name="user_login"),
    re_path('^logout/$', auth_views.LogoutView.as_view(), {'template_name': 'registration/logout.html'}, name='user_logout'),
    re_path('^password_change/$', auth_views.PasswordChangeView.as_view(), name='user_password_change'),
    re_path('^password_change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='user_password_change_done'),
    re_path('^password_reset/$', auth_views.PasswordResetView.as_view(), name='user_password_reset'),
    re_path('^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='user_password_reset_done'),
    re_path('^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='user_password_reset_confirm'),
    re_path('^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='user_password_reset_complete'),

    re_path(r'^import/?$', views.import_data, name='import_data'),
    re_path(r'^export/?$', views.export_data, name='export_data'),
    re_path(r'^accounts/?$', views.accounts, name='accounts'),
    re_path(r'^account/(\d+)/delete/?$', views.account_delete, name='account_delete'),
    re_path(r'^charges/?$', views.charges, name='charges'),
    re_path(r'^charges/(?P<year>\d+)/(?P<month>\d+)/?$', views.charges, name='charges'),
    re_path(r'^charges/(?P<display>all|tagged|untagged)/?$', views.charges, name='charges'),
    re_path(r'^charges/(?P<year>\d+)/(?P<month>\d+)/(?P<display>all|tagged|untagged)/?$', views.charges, name='charges'),
    re_path(r'^charges/assign/?$', views.assign_charge_tags, name="assign_charge_tags"),
    re_path(r'^charges/clear/?$', views.clear_charge_tags, name="clear_charge_tags"),
    re_path(r'^charge/set/?$', views.charge_set_tag, name="charge_set_tag"),
    re_path(r'^charge/comment/?$', views.charge_set_comment, name="charge_set_comment"),
    re_path(r'^charge/(\d+)/delete/?$', views.charge_delete, name="charge_delete"),
    re_path(r'^charge/(\d+)/change/?$', views.change_charge_tag, name="change_charge_tag"),
    re_path(r'^charge/(\d+)/clear/?$', views.clear_charge_tag, name="clear_charge_tag"),
    re_path(r'^matcher/delete/(\d+)/??$', views.matcher_delete, name='matcher_delete'),
    re_path(r'^matchers/?$', views.matchers, name='matchers'),
    re_path(r'^matchers/?#(?P<anchor>[-_\w]+)$', views.matchers, name='matchers'),
    re_path(r'^searchstring/add/?$', views.matcher_add_searchstring, name='matcher_add_searchstring'),
    re_path(r'^searchstring/remove/(\d+)/(\d+)/?$', views.matcher_remove_searchstring, name='matcher_remove_searchstring'),
    re_path(r'^tags/?$', views.tags, name='tags'),
    re_path(r'^tags/add/?$', views.add_tag, name='add_tag'),
    re_path(r'^tags/edit/?$', views.edit_tag, name='edit_tag'),
    re_path(r'^tags/delete/(\d+)/?$', views.delete_tag, name='delete_tag'),
    re_path(r'^sums/?$', views.sums, name='sums'),
    re_path(r'^spreadsheet/?$', views.spreadsheet, name='spreadsheet'),
    re_path(r'^spreadsheet/(?P<year>\d+)/?$', views.spreadsheet, name='spreadsheet'),
    re_path(r'^sums/(?P<year>\d+)/(?P<month>\d+)/?$', views.sums, name='sums'),
    re_path(r'^stats/?$', views.stats, name='stats'),
    re_path(r'^stats/(?P<year>\d+)/(?P<month>\d+)/?$', views.stats, name='stats'),
]
