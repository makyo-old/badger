from django.conf.urls.defaults import *
from django.contrib import admin

"""
badger.urls

Django URL definitions for Badger!

This file is part of Badger!.

Badger! is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Badger! is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Badger!.  If not, see <http://www.gnu.org/licenses/>.
                            
"""

admin.autodiscover()

urlpatterns = patterns('',
        # viewing
        (r'^badger/(?P<user>[a-zA-Z0-9]+)/$', 'badge.views.show_badger'),
        (r'^b/(?P<user>[a-zA-Z0-9]+)/$', 'badge.views.ajax_badge'),
        
        # badge management
        (r'^services/$', 'badge.views.list_services'),
        (r'^services/categories/$', 'badge.views.list_categories'),
        (r'^services/category/(?P<category>[a-zA-Z0-9_-]+)/$', 'badge.views.services_by_category'),
        (r'^services/suggest/$', 'badge.views.suggest_service'),
        (r'^services/suggestions/$', 'badge.views.list_suggestions'),
        (r'^add/$', 'badge.views.add_badgelet'),
        (r'^remove/(?P<badgelet>\d+)/$', 'badge.views.remove_badgelet'),
        (r'^update/(?P<badgelet>\d+)/$', 'badge.views.update_badgelet'),
        (r'^reweight/(?P<badgelet>\d+)(/(?P<weight>-?\d+))?/$', 'badge.views.reweight_badgelet'),

        # user management
        (r'^accounts/login/$', 'django.contrib.auth.views.login'),
        (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
        (r'^accounts/create/$', 'account.views.create'),
        (r'^accounts/profile/$', 'account.views.show'),
        (r'^accounts/profile/update/$', 'account.views.update'),
        (r'^accounts/password/change/$', 'django.contrib.auth.views.password_change'),
        (r'^accounts/password/change/done/$', 'django.contrib.auth.views.password_change_done'),
        (r'^accounts/password/reset/$', 'django.contrib.auth.views.password_reset'),
        (r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
        (r'^accounts/password/reset/complete', 'django.contrib.auth.views.password_reset_complete'),
        (r'^accounts/password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),

        (r'^admin/docs/(.*)', include('django.contrib.admindocs.urls')),
        (r'^admin/(.*)', admin.site.root),

        # flatpage fallback
        (r'^(?P<url>.*)$', 'badge.views.flatpage'),
)
