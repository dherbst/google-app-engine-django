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
Replaces django.contrib.flatpages.models.FlatPage with GAE version.
"""

from google.appengine.ext import db
from appengine_django.models import BaseModel
from django.utils.translation import ugettext_lazy as _

class FlatPage(BaseModel):
    url = db.StringProperty(required=True, indexed=True)
    title = db.StringProperty()
    content = db.TextProperty()
    enable_comments = db.BooleanProperty()
    template_name = db.StringProperty()
    registration_required = db.BooleanProperty()
    sites = db.ListProperty(db.Key)
    
    class Meta:
        db_table = 'django_flatpage'
        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ('url',)
    

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

    def __unicode__(self):
        return u"%s -- %s" % (self.url, self.title)

    def get_absolute_url(self):
        return self.url
