# coding: utf-8

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from web_scraping.models import Comment
from dashboard.utils import set_context

from .models import Annotation, KindOfOffence
from .forms import AddAnnotationForm, AnnotationForm


@login_required(redirect_field_name=None)
def annotation(request):
    context = set_context(request)
    context['types'] = KindOfOffence.objects.all()
    user_annotations = Annotation.objects.filter(user=request.user).order_by('id')
    remaining = user_annotations.filter(is_hate_speech=None)
    context['annotation_n'] = user_annotations.count()
    context['annotation_i'] = context['annotation_n'] - remaining.count()

    if context['annotation_n'] == 0:
        return render(request, "without_notes.html", context)

    if remaining.count() == 0:
        context['classifications'] = user_annotations.count()
        context['positive'] = user_annotations.filter(is_hate_speech=True).count()
        context['negative'] = user_annotations.filter(is_hate_speech=False).count()
        return render(request, "completed.html", context)

    if request.POST:
        form = AnnotationForm(request.POST, instance=remaining[0])
        if form.is_valid():
            form.save()
            return redirect('annotation')
    else:
        form = AnnotationForm(instance=remaining[0])

    context['annotation'] = remaining[0]
    context['form'] = form

    return render(request, "annotation.html", context)


@staff_member_required
def dashboard(request):
    context = set_context(request)
    table = []
    total = {}
    comments = Comment.objects.all()
    users = User.objects.filter(is_superuser=False)
    annotations = Annotation.objects.all()

    for user in users:
        item = {}
        item['user'] = user.get_full_name()
        user_annotations = annotations.filter(user=user)
        item['classifications'] = user_annotations.count()
        item['positive'] = user_annotations.filter(is_hate_speech=True).count()
        item['negative'] = user_annotations.filter(is_hate_speech=False).count()
        item['remaining'] = user_annotations.filter(is_hate_speech=None).count()
        table.append(item)
    total['users'] = users.count()
    total['classifications'] = annotations.count()
    total['positive'] = annotations.filter(is_hate_speech=True).count()
    total['negative'] = annotations.filter(is_hate_speech=False).count()
    total['remaining'] = annotations.filter(is_hate_speech=None).count()
    context['n_valid_comments'] = comments.filter(valid=True).count()
    context['n_comments'] = comments.count()

    if request.POST:
        form = AddAnnotationForm(request.POST)
        if form.is_valid():
            if form.save() > 0:
                return redirect('dashboard')
            else:
                context['msg'] = "Não existem comentários válidos disponíveis."
    else:
        form = AddAnnotationForm()

    context['form'] = form
    context['table'] = table
    context['total'] = total

    return render(request, "dashboard.html", context)