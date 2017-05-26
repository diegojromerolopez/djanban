
from django.http import HttpResponseRedirect
from django.shortcuts import render


# Creation of object
def new(request, instance, form_class, template_path, ok_url, extra_form_parameters=None):
    if extra_form_parameters is None:
        extra_form_parameters = {}

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance, **extra_form_parameters)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(ok_url)
    else:
        form = form_class(instance=instance, **extra_form_parameters)

    replacements = {"form": form, "instance": instance}
    replacements.update(extra_form_parameters)
    return render(request, template_path, replacements)


# Edition of object
def edit(request, instance, form_class, template_path, ok_url, extra_form_parameters=None):
    if extra_form_parameters is None:
        extra_form_parameters = {}

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance, **extra_form_parameters)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(ok_url)
    else:
        form = form_class(instance=instance, **extra_form_parameters)

    replacements = {"form": form, "instance": instance}
    replacements.update(extra_form_parameters)
    return render(request, template_path, replacements)


# Delete an object
def delete(request, instance, form_class, next_url, template_path="base/forms/delete.html", template_replacements=None):
    if request.method == "POST":
        form = form_class(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            instance.delete()
            return HttpResponseRedirect(next_url)

    else:
        form = form_class()

    instance.meta_verbose_name = instance._meta.verbose_name

    replacements = {"form": form, "instance": instance}
    if template_replacements:
        replacements.update(template_replacements)
    return render(request, template_path, replacements)
