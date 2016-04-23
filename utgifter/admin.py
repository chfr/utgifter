from django.contrib import admin

from . import models

admin.site.register(models.Charge)
admin.site.register(models.Tag)
admin.site.register(models.Matcher)
admin.site.register(models.SearchString)
