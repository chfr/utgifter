from django import forms

from .models import Matcher, Tag


class MatcherForm(forms.ModelForm):
    searchstrings = forms.CharField(widget=forms.Textarea(attrs={"cols": 20, "rows": 3}))

    class Meta:
        model = Matcher
        fields = ["name", "method", "tag"]


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "color"]
