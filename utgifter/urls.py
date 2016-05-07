from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url('^login/$', auth_views.login, name="user_login"),
    url('^logout/$', auth_views.logout, {'template_name': 'registration/logout.html'}, name='user_logout'),
    url('^password_change/$', auth_views.password_change, name='user_password_change'),
    url('^password_change/done/$', auth_views.password_change_done, name='user_password_change_done'),
    url('^password_reset/$', auth_views.password_reset, name='user_password_reset'),
    url('^password_reset/done/$', auth_views.password_reset_done, name='user_password_reset_done'),
    url('^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='user_password_reset_confirm'),
    url('^reset/done/$', auth_views.password_reset_complete, name='user_password_reset_complete'),

    url(r'^import/?$', views.import_data, name='import_data'),
    url(r'^export/?$', views.export_data, name='export_data'),
    url(r'^charges/?$', views.charges, name='charges'),
    url(r'^charges/(?P<year>\d+)/(?P<month>\d+)/?$', views.charges, name='charges'),
    url(r'^charges/(?P<display>all|tagged|untagged)/?$', views.charges, name='charges'),
    url(r'^charges/(?P<year>\d+)/(?P<month>\d+)/(?P<display>all|tagged|untagged)/?$', views.charges, name='charges'),
    url(r'^charges/assign/?$', views.assign_charge_tags, name="assign_charge_tags"),
    url(r'^charges/clear/?$', views.clear_charge_tags, name="clear_charge_tags"),
    url(r'^charge/set/?$', views.charge_set_tag, name="charge_set_tag"),
    url(r'^charge/(\d+)/delete/?$', views.charge_delete, name="charge_delete"),
    url(r'^charge/(\d+)/change/?$', views.change_charge_tag, name="change_charge_tag"),
    url(r'^charge/(\d+)/clear/?$', views.clear_charge_tag, name="clear_charge_tag"),
    url(r'^matcher/delete/(\d+)/??$', views.matcher_delete, name='matcher_delete'),
    url(r'^matchers/?$', views.matchers, name='matchers'),
    url(r'^matchers/?#(?P<anchor>[-_\w]+)$', views.matchers, name='matchers'),
    url(r'^searchstring/add/?$', views.matcher_add_searchstring, name='matcher_add_searchstring'),
    url(r'^searchstring/remove/(\d+)/(\d+)/?$', views.matcher_remove_searchstring, name='matcher_remove_searchstring'),
    url(r'^tags/?$', views.tags, name='tags'),
    url(r'^tags/add/?$', views.add_tag, name='add_tag'),
    url(r'^tags/edit/?$', views.edit_tag, name='edit_tag'),
    url(r'^tags/delete/(\d+)/?$', views.delete_tag, name='delete_tag'),
    url(r'^sums/?$', views.sums, name='sums'),
    url(r'^sums/(?P<year>\d+)/(?P<month>\d+)/?$', views.sums, name='sums'),
    url(r'^stats/?$', views.stats, name='stats'),
    url(r'^stats/(?P<year>\d+)/(?P<month>\d+)/?$', views.stats, name='stats'),
]
