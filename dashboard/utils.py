from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from .models import MenuItem, SystemData


def set_context(request):
    context = {}

    try:
        system = SystemData.objects.all()[0]
        context['menu'] = MenuItem.objects.all().order_by('-order')
    except:
        raise Http404(_('System data not registered'))

    context['system'] = system.__dict__

    if not request.user.is_staff:
        context['menu'] = context['menu'].exclude(label='Admin')

    try:
        context['notifications'] = request.session['notifications']
    except:
        context['notifications'] = []
    request.session['notifications'] = []

    if 'intro' in request.session:
        if request.session['intro']:
            context['intro'] = True
            request.session['intro'] = False
        else:
            context['intro'] = False
    else:
        context['intro'] = False

    return context
