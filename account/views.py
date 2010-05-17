from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from badge.models import *

"""
badger.account.views

Views for Badger! pertaining to the accounts/registration system.

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

def create(request):
    #
    if request.method == 'POST': 
        if request.POST.get('username', None) and request.POST.get('password', None) and request.POST.get('email', None):
            user = User.objects.create_user(request.POST['username'], request.POST['email'], None)
            user.set_password(request.POST['password'])
            user.save()
            return HttpResponseRedirect('/accounts/login/')
        else:
            request.user.message_set.create(message = '<div class="failure">Oops!  All fields required!</div>')
    return render_to_response("registration/create_user.html", context_instance = RequestContext(request, {}))

@login_required
def show(request):
    #
    return render_to_response("registration/profile_show.html", context_instance = RequestContext(request, {}))

@login_required
def update(request):
    #
    if request.method == 'POST':
        request.user.first_name = request.POST.get('firstname', None) or request.user.first_name
        request.user.last_name = request.POST.get('lastname', None) or request.user.last_name
        request.user.email = request.POST.get('email', None) or request.user.email
        request.user.save()
    return HttpResponseRedirect('/accounts/profile/')
