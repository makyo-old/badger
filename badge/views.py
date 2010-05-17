from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage
from badge.models import *

"""
badger.badge.views

Views for Badger! pertaining to the badges themselves.

This file is part of Badger!.

Badger! is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Badger! is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Badger!.  If not, see <http://www.gnu.org/licenses/>.
                            
"""

def get_count():
    return User.objects.count()

def flatpage(request, url):
    fp = get_object_or_404(FlatPage, url='/%s' % url)
    return render_to_response('flatpages/default.html', context_instance = RequestContext(request, {'flatpage': fp, 'count': get_count()}))

def show_badger(request, user):
    """
    Show badge for a user (most of the work is done in the template)
    """
    impl = []
    for blet in User.objects.get(username = user).badgelet_set.all():
        for i in blet.service.implementation_set.all():
            if i not in impl:
                impl.append(i)
    return render_to_response('badge/badge.html', context_instance = RequestContext(request, {'badger': User.objects.get(username = user), 'impl': impl, 'count': get_count()}))


def ajax_badge(request, user):
    """
    Render a badge to an ajax template based on the GET key 'style', default to 'style=icons'
    """
    return render_to_response('badge/badge_ajax_%s.html' % request.GET.get('style', 'icons'), context_instance = RequestContext(request, {'badger': User.objects.get(username = user), 'count': get_count()}))


def list_services(request):
    """
    List all services that aren't suggestions
    """
    return render_to_response('badge/services_list.html', context_instance = RequestContext(request, {'services': Service.objects.filter(suggestion = False), 'count': get_count()}))


@permission_required('badge.change_service')
def list_suggestions(request):
    """
    List service suggestions to those who can take action on them
    """
    return render_to_response('badge/suggestion_list.html', context_instance = RequestContext(request, {'services': Service.objects.filter(suggestion = True), 'count': get_count()}))


def list_categories(request):
    """
    List all categories
    """
    return render_to_response('badge/categories_list.html', context_instance = RequestContext(request, {'categories': Category.objects.all(), 'count': get_count()}))


def services_by_category(request, category):
    """
    List all services that aren't suggestions within a category
    """
    cat = get_object_or_404(Category, slug = category)
    return render_to_response('badge/services_list.html', context_instance = RequestContext(request, {'services': Service.objects.filter(category = cat), 'category': cat, 'count': get_count()}))


@login_required
def suggest_service(request):
    """
    Let users suggest services to add to the list
    """
    if request.method == 'POST':
        if not request.POST.get('name', None) or not request.POST.get('description', None) or not request.POST.get('url', None) or not request.POST.get('egurl', None):
            request.user.message_set.create(message = '<div class="failure">All fields required!</div>')
        else:
            from time import localtime, mktime
            from django.core.files import File
            from django.conf import settings
            suggestion = Service(
                    slug = 'suggest-%s-%d' % (request.user.username, int(mktime(localtime()))),
                    name = request.POST['name'],
                    description = request.POST['description'],
                    url = request.POST['url'],
                    id_url = request.POST['egurl'],
                    suggestion = True);
            suggestion.save()
            request.user.message_set.create(message = '<div class="success">Thanks for the suggestion!  We\'ll take a look at it!</div>') 
    return render_to_response('badge/suggest_service.html', context_instance = RequestContext(request, {'count': get_count()}))


@login_required
def add_badgelet(request):
    """
    Add a badgelet to a user's badge
    """
    if (request.method == 'GET') and request.GET.get('service', None) and request.GET.get('identifier', None):
        badgelet = Badgelet(user = request.user,
                            service = Service.objects.get(slug = request.GET['service']),
                            identifier = request.GET['identifier'],
                            hidden = request.GET.get('hidden', 'false') == 'true' and True or False)
        badgelet.save()
        request.user.message_set.create(message = '<div class="success">Success!  Badgelet applied!</div>')
    else:
        request.user.message_set.create(message = '<div class="failure">Uh-oh... looks like something went awry!  Try again?</div>')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def remove_badgelet(request, badgelet):
    """
    Delete a badgelet, make sure we've asked for confirmation
    """
    blet = get_object_or_404(Badgelet, id = badgelet)
    if (blet.user == request.user):
        if request.GET.get('confirm', None) == 'yes':
            blet.delete()
            request.user.message_set.create(message = '<div class="success">*Poof!*  All gone!</div>')
    else:
        request.user.message_set.create(message = '<div class="failure">That badgelet doesn\'t seem to belong to you!</div>')
    return HttpResponseRedirect('/badger/%s/' % request.user.username)


@login_required
def update_badgelet(request, badgelet):
    """
    update a badgelet based on user input from a form
    """
    blet = get_object_or_404(Badgelet, id = badgelet)
    if (blet.user == request.user):
        if request.GET.get('identifier', None) is not None:
            blet.identifier = request.GET['identifier']
            request.user.message_set.create(message = '<div class="success">Identifier updated</div>')
        if request.GET.get('hidden', None) is not None:
            blet.hidden = request.GET['hidden'] == 'false' and True or False
            request.user.message_set.create(message = '<div class="success">Hidden status updated</div>')
    else:
        request.user.message_set.create(message = '<div class="failure">That badgelet doesn\'t seem to belong to you!</div>')
    return HttpResponseRedirect('/badger/%s/' % request.user.username)


@login_required
def reweight_badgelet(request, badgelet, weight = None):
    """
    Set a badgelet's weight, indicating its position (low weight = higher position) while making sure the weights are fairly unique within each badge
    """
    # get the badge
    blet = get_object_or_404(Badgelet, id = badgelet)

    from locale import atoi
    if weight is None:
        # could be from a form..?  Otherwise, don't do anything, really
        weight= request.GET.get('weight', None) is none and blet.weight or atoi(request.GET['weight'])
    else:
        weight = atoi(weight)


    # shift weights above or below
    if (blet.weight - weight > 0):
        for b in request.user.badgelet_set.filter(weight__lt = weight - 1):
            b.weight -= 1
            b.save()
    elif (blet.weight - weight < 0):
        for b in request.user.badgelet_set.filter(weight__gt = blet.weight + 1):
            b.weight += 1
            b.save()

    # set the weight
    blet.weight = weight
    blet.save()

    # reset the weights of all the badgelets within the badge to make sure they're fairly unique
    blets = request.user.badgelet_set.all()
    i = 0
    for b in blets:
        b.weight = i
        b.save()
        i += 1
    # set a message and return
    request.user.message_set.create(message = '<div class="success">Badgelet moved!</div>')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
