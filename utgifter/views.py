import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .charge_parser import parse_nordea
from .forms import TagForm, MatcherForm, AccountForm
from .models import Charge, Matcher, Tag, SearchString, Account
from .templatetags.tags import month_name_short
from .utils import sanitize_date, sanitize_year, dump_data_to_json, load_data_from_json


@login_required
def index(request):
    context = {}
    year, month = sanitize_date(-1, -1)
    now = date(year=year, month=month, day=15)
    prev = now - timedelta(days=30)
    user_charges = Charge.objects.filter(user=request.user)

    this_month_charges = user_charges.filter(amount__lte=0, date__year=now.year, date__month=now.month)
    this_total = this_month_charges.aggregate(Sum("amount"))["amount__sum"]

    if this_total is not None:
        this_total = -this_total

    context["month_total"] = this_total

    prev_month_charges = user_charges.filter(amount__lte=0, date__year=prev.year, date__month=prev.month)
    prev_total = prev_month_charges.aggregate(Sum("amount"))["amount__sum"]

    if prev_total is not None:
        prev_total = -prev_total

    context["prev_total"] = prev_total

    context["month_charges"] = len(this_month_charges)
    context["prev_charges"] = len(prev_month_charges)

    print(str.format("month_total: {}", this_total))
    print(str.format("prev_total: {}", prev_total))

    print(context)

    return render(request, "utgifter/index.html", context)


@login_required
def import_data(request):
    context = {}
    do_tagging = False

    if request.method == "POST":
        print(request.POST)
        if "raw_charges" in request.POST and not "json_data" in request.POST:
            if "autotag" in request.POST:
                if request.POST["autotag"] == "on":
                    do_tagging = True

            try:
                account_id = int(request.POST["account"][0])
            except (ValueError, IndexError):
                return HttpResponseBadRequest("Invalid account id")

            account = get_object_or_404(Account, pk=account_id, user=request.user)

            new_charges = []
            for row in parse_nordea(request.POST["raw_charges"]):
                row["user"] = request.user
                row["account"] = account
                new_charges.append(Charge(**row))

            Charge.objects.bulk_create(new_charges)

            if do_tagging:
                return redirect("assign_charge_tags")
            else:
                return redirect("charges")
        elif "raw_charges" not in request.POST and "json_data" in request.POST:
            load_data_from_json(request.user, json.loads(request.POST["json_data"]))
    context["accounts"] = Account.objects.filter(user=request.user)

    return render(request, "utgifter/import_charges.html", context)


@login_required
def export_data(request):
    json_data = dump_data_to_json(request.user)

    context = {"json_data": json_data}
    return render(request, "utgifter/export_data.html", context)


@login_required
def accounts(request):
    context = {}
    context["accounts"] = Account.objects.filter(user=request.user)

    if request.method == "POST":
        form = AccountForm(request.POST)

        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            return redirect(reverse("accounts"))

    else:
        form = AccountForm()

    context["form"] = form

    return render(request, "utgifter/accounts.html", context)\

@login_required
def account_delete(request, account_id):
    account = get_object_or_404(Account, user=request.user, pk=account_id)
    account.delete()

    return redirect(reverse("accounts"))


@login_required
def charges(request, account_id=None, display="all", year=0, month=0):
    year, month = sanitize_date(year, month)

    if account_id is not None:
        account = get_object_or_404(Account, user=request.user, pk=account_id)
        print("haz account")
    else:
        account = None

    if account:
        charges = Charge.objects.filter(user=request.user, date__year=year, date__month=month,
                                        account=account).order_by("date")
    else:
        charges = Charge.objects.filter(user=request.user, date__year=year, date__month=month)\
            .order_by("date")

    if display == "tagged":
        charges = charges.exclude(tag=None)
    elif display == "untagged":
        charges = charges.filter(tag=None)

    tags = Tag.objects.filter(user=request.user)

    accounts = Account.objects.filter(user=request.user)

    cur_month = date(year=year, month=month, day=15)
    next_month = cur_month + timedelta(days=30)  # will this always work? let's hope!
    prev_month = cur_month - timedelta(days=30)

    months = []
    for i in range(1, 13):
        months.append({"num": i, "cur": i == cur_month.month})

    context = {"charges": charges, "tags": tags, "cur_month": cur_month, "prev_month": prev_month,
               "next_month": next_month, "display": display, "months": months, "year": year,
               "accounts": accounts}

    if account:
        context["cur_account"] = account

    return render(request, 'utgifter/charges.html', context)


@login_required
@csrf_exempt
def charge_set_tag(request):
    if request.method != "POST":
        return redirect("matchers")

    data = request.POST

    response = JsonResponse({"error": 1, "msg": "Unknown error"})

    if "charge" in data and "tagid" in data:
        charge = data["charge"]
        tagid = data["tagid"]
        charges = Charge.objects.filter(pk=charge, user=request.user)
        tags = Tag.objects.filter(pk=tagid, user=request.user)

        if not (tags and charges):
            response = JsonResponse({"error": 1, "msg": "Tag or charge does not exist"})
        else:
            charge = charges[0]
            tag = tags[0]
            charge.tag = tag
            charge.save()
            response = JsonResponse({"success": 1, "tagname": tag.name, "tagcolor": tag.color})
    elif "tagid" in data:
        charge_ids = []
        for k, v in data.items():
            try:
                if k.startswith("charge"):
                    charge_ids.append(int(v))
            except:
                print(str.format("Could not convert {}:{}", k, v))
        tagid = data["tagid"]
        if not charge_ids:
            response = JsonResponse({"error": 1, "msg": "Charges do not exist"})
        else:
            charges = Charge.objects.filter(pk__in=charge_ids, user=request.user)
            tags = Tag.objects.filter(pk=tagid, user=request.user)

            if not (tags and charges):
                response = JsonResponse({"error": 1, "msg": "Tag or charges does not exist"})
            else:
                tag = tags[0]
                for charge in charges:
                    charge.tag = tag
                    charge.save()
                response = JsonResponse({"success": 1, "tagname": tag.name, "tagcolor": tag.color})

    return response


@login_required
def charge_delete(request, charge_id):
    charge = get_object_or_404(Charge, pk=charge_id, user=request.user)

    charge.delete()

    return redirect("charges")


@login_required
def assign_charge_tags(request):
    charges = Charge.objects.filter(user=request.user)
    matchers = Matcher.objects.filter(user=request.user)

    for charge in charges:
        # This means it won't re-match rows that were tagged by a matcher, but it will re-match
        # manually tagged rows, effectively overriding them.
        # if charge.matcher:
        #    continue

        # This means it won't re-match manually tagged rows, so it won't override the manual ones.
        if charge.tag:
            continue

        for matcher in matchers:
            searchstrings = matcher.searchstring_set.all()
            for searchstring in searchstrings:
                if matcher.match(searchstring.string, charge.name):
                    charge.tag = matcher.tag
                    charge.matcher = matcher
                    charge.save()
                    break  # will only match the first searchstring, can't do multi-tagged charges

    return redirect("charges")


@login_required
def change_charge_tag(request, charge_id):
    charge = get_object_or_404(Charge, pk=charge_id, user=request.user)

    return redirect("charges")


@login_required
def clear_charge_tag(request, charge_id):
    charge = get_object_or_404(Charge, pk=charge_id, user=request.user)
    charge.clear()
    charge.save()

    return redirect("charges")


@login_required
def clear_charge_tags(request):
    Charge.objects.filter(user=request.user).update(tag=None, matcher=None)

    return redirect("charges")


@csrf_exempt
@login_required
def add_tag(request):
    if request.method != "POST":
        return redirect("matchers")

    data = request.POST

    response = JsonResponse({"error": 1, "msg": "Unknown error"})

    if "tag" in data:
        tagname = data["tag"]
        tag, created = Tag.objects.get_or_create(name=tagname, user=request.user)

        if not created:
            response = JsonResponse({"error": 1, "msg": "Tag already exists"})
        else:
            response = JsonResponse({"success": 1, "tagid": tag.pk, "tagname": tagname})

    return response


@csrf_exempt
@login_required
def edit_tag(request):
    if request.method != "POST":
        return redirect("tags")

    data = request.POST

    response = JsonResponse({"error": 1, "msg": "Unknown error"})

    if "tagid" in data and "name" in data and "color" in data:
        tag_id = data["tagid"]
        name = data["name"]
        color = data["color"]

        tag = get_object_or_404(Tag, pk=tag_id, user=request.user)
        tag.name = name
        tag.color = color
        tag.save()

        response = JsonResponse({"success": 1})

    return response


@login_required
def delete_tag(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id, user=request.user)
    tag.delete()

    return redirect("tags")


@login_required
def matchers(request, anchor=None):
    matchers = Matcher.objects.filter(user=request.user)

    tags = Tag.objects.filter(user=request.user)

    if request.method == "POST":
        form = MatcherForm(request.POST)

        if form.is_valid():
            matcher = form.save(commit=False)
            matcher.user = request.user
            matcher.save()
            form.save_m2m()

            searchstrings = form.cleaned_data["searchstrings"]
            for searchstring in searchstrings.splitlines():
                if not searchstring.strip():
                    continue  # whitespace/empty not allowed

                SearchString.objects.get_or_create(user=request.user, matcher=matcher,
                                                   string=searchstring)

            url = reverse("matchers", kwargs={"anchor": "emptyAddRow"}).replace("%23", "#")
            return redirect(url)
    else:
        form = MatcherForm()

    form.fields["tag"].queryset = tags

    context = {"matchers": matchers, "form": form}
    return render(request, "utgifter/matchers.html", context)


@login_required
def matcher_delete(request, matcher_id):
    matcher = get_object_or_404(Matcher, pk=matcher_id, user=request.user)
    matcher.delete()

    return redirect(matchers)


@login_required
def matcher_remove_searchstring(request, matcher_id, searchstring_id):
    matcher = get_object_or_404(Matcher, pk=matcher_id, user=request.user)
    searchstring = get_object_or_404(SearchString, pk=searchstring_id, user=request.user)

    if searchstring.matcher == matcher:
        searchstring.delete()

    url = reverse("matchers", kwargs={"anchor": str.format("matcherRow{}", matcher_id)}).replace("%23", "#")
    return redirect(url)


@login_required
@csrf_exempt
def matcher_add_searchstring(request):
    if request.method != "POST":
        return redirect("matchers")
    data = request.POST

    response = JsonResponse({"error": 1})

    if "string" in data and "matcher" in data:
        matcher = data["matcher"]
        string = data["string"]
        matcher = get_object_or_404(Matcher, pk=matcher)
        searchstring = SearchString(user=request.user, matcher=matcher, string=string)
        searchstring.save()

        response = JsonResponse({"success": 1})

    return response


@login_required
def tags(request):
    tags = Tag.objects.filter(user=request.user)

    if request.method == "POST":
        form = TagForm(request.POST)

        if form.is_valid():
            tag = form.save(commit=False)
            tag.user = request.user
            tag.save()
            form.save_m2m()

            return redirect("tags")
    else:
        form = TagForm()

    color = Tag._meta.get_field('color')
    default_color = color.get_default()

    context = {"tags": tags, "form": form, "default_color": default_color}
    return render(request, "utgifter/tags.html", context)


@login_required
def spreadsheet(request, year=0):
    year = sanitize_year(year)

    tags = Tag.objects.filter(user=request.user)
    user_charges = Charge.objects.filter(user=request.user, date__year=year)

    months = [month_name_short(i + 1) for i in range(12)]
    tag_stats = []

    for tag in tags:
        sums_per_month = []  # list of each month's total for this particular tag
        tag_year_total = 0  # total sum for this tag over the year
        num_empty = 0  # the number of empty (0) cells for this particular tag

        for month in range(12):
            month_sum = user_charges.filter(tag=tag, date__month=month + 1).aggregate(Sum("amount"))["amount__sum"]
            if month_sum is None:  # no charges for this month
                month_sum = 0
                num_empty += 1

            sums_per_month.append(month_sum)
            tag_year_total += month_sum

        # Filtered average over the year, only averages over non-empty months.
        # In other words, if you had 100 EUR tagged as "food" in January and
        # nothing else for the rest of the year, the filtered average for
        # "food" that year would be 100. The "true" average would of course
        # be 100/12 = ~8.3
        filtered_avg = 0 if num_empty == 12 else tag_year_total/(12-num_empty)  # no zero division here mister
        true_avg = tag_year_total/12

        tag_stats.append((tag, sums_per_month, tag_year_total, filtered_avg, true_avg))
        #print("Tag {}: sums_per_month: {}, tag_year_total: {}, filtered_avg: {}".format(tag, sums_per_month, tag_year_total, filtered_avg))

    context = {"months": months, "tag_stats": tag_stats, "year": year}

    return render(request, "utgifter/spreadsheet.html", context)


@login_required
def sums(request, year=0, month=0):
    year, month = sanitize_date(year, month)

    tags = Tag.objects.filter(user=request.user)
    user_charges = Charge.objects.filter(user=request.user, date__year=year, date__month=month)

    sums = []

    for tag in tags:
        tagsum = user_charges.filter(tag=tag).aggregate(Sum("amount"))["amount__sum"]
        sums.append((tag, tagsum if tagsum else 0))

    total_out = user_charges.filter(amount__lte=0).aggregate(Sum("amount"))["amount__sum"]
    sums.append(("Total spent", total_out if total_out else 0))
    total_in = user_charges.filter(amount__gt=0).aggregate(Sum("amount"))["amount__sum"]
    sums.append(("Total income", total_in if total_in else 0))
    if total_out and total_in:
        sums.append(("Total delta", total_in + total_out))
    else:
        sums.append(("Total delta", 0))

    untagged_out = user_charges.filter(tag=None, amount__lte=0).aggregate(Sum("amount"))["amount__sum"]
    sums.append(("Untagged expenses", untagged_out if untagged_out else 0))
    untagged_in = user_charges.filter(tag=None, amount__gt=0).aggregate(Sum("amount"))["amount__sum"]
    sums.append(("Untagged income", untagged_in if untagged_in else 0))

    cur_month = date(year=year, month=month, day=15)
    next_month = cur_month + timedelta(days=30)  # will this always work? let's hope!
    prev_month = cur_month - timedelta(days=30)

    context = {"sums": sums, "cur_month": cur_month, "prev_month": prev_month,
               "next_month": next_month}
    return render(request, "utgifter/sums.html", context)


@login_required
def stats(request, year=0, month=0):
    year, month = sanitize_date(year, month)

    cur_month = date(year=year, month=month, day=15)
    next_month = cur_month + timedelta(days=30)  # will this always work? let's hope!
    prev_month = cur_month - timedelta(days=30)

    tags = Tag.objects.filter(user=request.user)
    charges = Charge.objects.filter(user=request.user)

    totals = {}

    for tag in tags:
        prev = None
        for month in range(1, 13):
            tagsum = charges.filter(tag=tag, date__year=2016, date__month=month).aggregate(Sum("amount"))["amount__sum"]
            delta = 0
            if prev is None:
                delta = 0
                prev = tagsum
            if not tagsum is None:
                delta = prev - tagsum
                prev = tagsum
            totals.setdefault(tag.name, []).append((tagsum, delta))

    context = {"cur_month": cur_month, "prev_month": prev_month, "next_month": next_month, "totals": totals}
    return render(request, "utgifter/stats.html", context)
