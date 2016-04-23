# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-23 01:02
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import migrations

from utgifter.models import Tag, Matcher, SearchString


def create_superuser(apps, schema_editor):
    u = User.objects.create_user(username="su",
                                 email="a@a.com",
                                 password="qwerasdf",
                                 is_superuser=True,
                                 is_staff=True)
    u.save()

    t = Tag(user=u, color="#B51D1D", name="Mat")
    t.save()
    m = Matcher(user=u, name="Mat-matcher", method=Matcher.ICONTAINS, tag=t)
    m.save()
    ss = SearchString(user=u, matcher=m, string="hemköp")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="ica")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="coop")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="7 eleven")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="willys")
    ss.save()

    t = Tag(user=u, color="#65A372", name="Systemet")
    t.save()
    m = Matcher(user=u, name="Systemet-matcher", method=Matcher.ICONTAINS, tag=t)
    m.save()
    ss = SearchString(user=u, matcher=m, string="ystembolag")
    ss.save()

    t = Tag(user=u, color="#7497A8", name="Restaurant/snabbmat")
    t.save()
    m = Matcher(user=u, name="Restaurant-matcher", method=Matcher.ICONTAINS, tag=t)
    m.save()
    ss = SearchString(user=u, matcher=m, string="pizz")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="kebab")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="sushi")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="grill")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="burger")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="restauran")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="mdconald")
    ss.save()

    t = Tag(user=u, color="#9A7A9E", name="Bar/pub")
    t.save()
    m = Matcher(user=u, name="Bar/pub-matcher", method=Matcher.ICONTAINS, tag=t)
    m.save()
    ss = SearchString(user=u, matcher=m, string="dovas")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="turpin")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="lion")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="bar")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="pub")
    ss.save()
    ss = SearchString(user=u, matcher=m, string="bishops")
    ss.save()

    u = User.objects.create_user(username="user1",
                                 email="b@b.com",
                                 password="qwerasdf",
                                 is_superuser=False,
                                 is_staff=False)
    u.save()


class Migration(migrations.Migration):
    dependencies = [
        ('utgifter', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
