from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .charge_parser import parse_nordea
from .forms import TagForm, MatcherForm
from .models import Charge, Matcher, Tag, SearchString


@login_required
def index(request):
    context = {}
    return render(request, "utgifter/index.html", context)


@login_required
def import_charges(request):
    context = {}
    charges = []
    do_tagging = False

    if request.method == "POST":
        if "autotag" in request.POST:
            if request.POST["autotag"] == "on":
                do_tagging = True

        for row in parse_nordea(request.POST["raw_charges"]):
            row["user"] = request.user
            charges.append(Charge(**row))

        Charge.objects.bulk_create(charges)

        if do_tagging:
            return redirect("assign_charge_tags")
        else:
            return redirect("charges")

    return render(request, "utgifter/import_charges.html", context)


@login_required
def charges(request, filter="all"):
    charges = Charge.objects.filter(user=request.user).order_by("date")
    if filter == "tagged":
        charges = charges.exclude(tag=None)
    elif filter == "untagged":
        charges = charges.filter(tag=None)

    tags = Tag.objects.filter(user=request.user)

    context = {"charges": charges, "tags": tags}

    return render(request, 'utgifter/charges.html', context)

@login_required
@csrf_exempt
def charge_set_tag(request):
    if request.method != "POST":
        return redirect("matchers")

    data = request.POST
    print("data: " + str(data))

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
                for charge in charges:
                    tag = tags[0]
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
        if charge.matcher: continue  # don't re-match already matched rows
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
def matchers(request):
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
            for searchstring in searchstrings.split("\n"):
                if not searchstring.strip():
                    continue  # whitespace/empty not allowed

                SearchString.objects.get_or_create(user=request.user, matcher=matcher,
                                                   string=searchstring)

            return redirect("matchers")
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

    return redirect("matchers")


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
def sums(request):
    tags = Tag.objects.filter(user=request.user)
    user_charges = Charge.objects.filter(user=request.user)

    sums = []

    for tag in tags:
        tagsum = user_charges.filter(tag=tag).aggregate(Sum("amount"))["amount__sum"]
        sums.append((tag, tagsum))

    total_out = user_charges.filter(amount__lte=0).aggregate(Sum("amount"))["amount__sum"]
    sums.append(("Total spent", total_out))
    total_in = user_charges.filter(amount__gt=0).aggregate(Sum("amount"))["amount__sum"]
    sums.append(("Total income", total_in))
    if total_out and total_in:
        sums.append(("Total delta", total_in + total_out))

    untagged_out = user_charges.filter(tag=None, amount__lte=0).aggregate(Sum("amount"))["amount__sum"]
    sums.append(("Untagged expenses", untagged_out))
    untagged_in = user_charges.filter(tag=None, amount__gt=0).aggregate(Sum("amount"))["amount__sum"]
    sums.append(("Untagged income", untagged_in))

    context = {"sums": sums}
    return render(request, "utgifter/sums.html", context)
