import datetime

from colorful.fields import RGBColorField
from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False, null=False)
    number = models.CharField(max_length=200, blank=True, verbose_name="Number (optional)")
    color = RGBColorField(default="#b9d8e7")

    def __str__(self):
        if self.number:
            return "{} ({}, {})".format(self.name, self.user, self.number)
        else:
            return "{} ({})".format(self.name, self.user)


class Charge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tag = models.ForeignKey("Tag", null=True, blank=True, default=None, on_delete=models.SET_NULL)
    matcher = models.ForeignKey("Matcher", null=True, blank=True, default=None, on_delete=models.SET_NULL)
    comment = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return str.format("{} {} {} ({})", self.date, self.name, self.amount, self.account.name)

    # Does not call save()
    def clear(self):
        self.tag = None
        self.matcher = None

    def short_date(self):
        return self.date.strftime("%B %d")


class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = RGBColorField(default="#b9d8e7")
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Matcher(models.Model):
    EXACT = "EXACT"
    CONTAINS = "CONTAINS"
    ICONTAINS = "ICONTAINS"
    FUZZY = "FUZZY"
    METHOD_CHOICES = [(EXACT, "Exact"),
                      (CONTAINS, "Contains"),
                      (ICONTAINS, "Contains (case-insensitive)"),
                      (FUZZY, "Fuzzy")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default=ICONTAINS)
    tag = models.ForeignKey(Tag)

    def match(self, needle, haystack):
        if self.method == self.EXACT:
            return needle == haystack
        if self.method == self.CONTAINS:
            return needle in haystack
        if self.method == self.ICONTAINS:
            return needle.lower() in haystack.lower()
        if self.method == self.FUZZY:
            raise NotImplementedError

    def __str__(self):
        return self.name


class SearchString(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    matcher = models.ForeignKey(Matcher, on_delete=models.CASCADE)
    string = models.CharField(max_length=50)

    def __str__(self):
        return self.string
