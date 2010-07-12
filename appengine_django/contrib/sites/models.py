#!/usr/bin/python2.4
#
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Replaces Site with datastore api friendly object.
"""

from google.appengine.ext import db
from appengine_django.models import BaseModel
from django.utils.translation import ugettext_lazy as _

SITE_CACHE = {}

class Site(BaseModel):
    """
    Replaces django.contrib.sites.models.Site.  Since the BaseModel uses a ModelManager, this 
    also replaces django.contrib.sites.models.SiteManager.
    """
    id = db.IntegerProperty(required=True)
    """ django expects you to reference Site by Integer in settings module """
    domain = db.StringProperty(required=True)
    name = db.StringProperty()

    class Meta:
        db_table = 'django_site'
        verbose_name = _('site')
        verbose_name_plural = _('sites')
        ordering = ('domain',)

    @classmethod
    def kind(cls):
        return cls.Meta.db_table

    @classmethod
    def create(cls, **kwargs):
        """
        wrap create to constructor/save for legacy code
        """
        obj = cls(**kwargs)
        obj.save()
        return obj

    @classmethod    
    def get_current(cls):
        """
        Returns the current ``Site`` based on the SITE_ID in the
        project's settings. The ``Site`` object is cached the first
        time it's retrieved from the database.
        """

        from django.conf import settings
        try:
            sid = settings.SITE_ID
        except AttributeError:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured("You're using the Django \"sites framework\" without having set the SITE_ID setting. Create a site in your database and set the SITE_ID setting to fix this error.")

        try:
            current_site = SITE_CACHE[sid]
        except KeyError:
            current_site = Site.all().filter("id =",sid).get()
            SITE_CACHE[sid] = current_site
        return current_site

    def clear_cache(self):
        """Clears the ``Site`` object cache."""
        global SITE_CACHE
        SITE_CACHE = {}


    def __unicode__(self):
        return self.domain

    def save(self, *args, **kwargs):
        self.put()
        # Cached information will likely be incorrect now.
        if self.id in SITE_CACHE:
            del SITE_CACHE[self.id]

    def delete(self):
        super(Site,self).delete()
        try:
            del SITE_CACHE[self.id]
        except KeyError:
            pass
        
