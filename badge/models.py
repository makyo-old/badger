from django.db import models
from django.contrib.auth.models import User

"""
badger.badge.models

Models for the ORM of the Badge component of Badger!

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

class Category(models.Model):
    slug = models.SlugField(unique = True)
    name = models.CharField(max_length = 128)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"

class Service(models.Model):
    slug = models.SlugField(unique = True)
    name = models.CharField(max_length = 128)
    url = models.URLField()
    id_url = models.CharField(max_length = 200, verbose_name = "URL with user identifier", help_text = "Use '%(id)s' where you would like the username to appear")
    description = models.TextField()
    icon = models.FileField(upload_to = 'icons')
    display = models.CharField(max_length = 200, help_text = "Use '%(id)s' where you would like the username to appear")
    category = models.ForeignKey('Category', blank = True, null = True)
    adult = models.BooleanField()
    suggestion = models.BooleanField()

    def __unicode__(self):
        return self.name

    def id_url_example(self):
        return self.id_url % {'id': 'example'}

class Implementation(models.Model):
    OPTIONS = (
            ('none', 'Not supported'),
            ('link', 'Link only'),
            ('static', 'Static badge'),
            ('dynamic', 'Dynamic badge')
            )

    service = models.ForeignKey('Service')
    support = models.CharField(max_length = 7, choices = OPTIONS)
    location = models.CharField(max_length = 100, blank = True, help_text = "The portion of the page where the badge will be posted (i.e.: 'entry' or 'profile page)'")
    notes = models.TextField(blank = True)
    suggestion = models.BooleanField()

    def __unicode__(self):
        return "%s - %s: %s" % (self.service.name, self.location, self.get_support_display())
    
class Badgelet(models.Model):
    user = models.ForeignKey(User)
    service = models.ForeignKey('Service')
    identifier = models.CharField(max_length = 128)
    hidden = models.BooleanField()
    weight = models.IntegerField(default = 0);

    def get_url(self):
        return self.service.id_url % {'id': self.identifier}

    def get_display(self):
        return self.service.display % {'id': self.identifier}

    class Meta:
        ordering = ['weight']
