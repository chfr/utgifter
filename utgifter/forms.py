from django import forms

from .models import Matcher, Tag, Account


class MatcherForm(forms.ModelForm):
    searchstrings = forms.CharField(required=False, widget=forms.Textarea(attrs={"cols": 20, "rows": 3}))

    class Meta:
        model = Matcher
        fields = ["name", "method", "tag"]


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "color"]


class AccountForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ["name", "number", "color"]
