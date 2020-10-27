from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext


@login_required
def profile_detail(request):
    """ Detail view of a user's profile."""

    profile_obj = request.user.userprofile

    if profile_obj.agree_to_licensing == False:
        return HttpResponseRedirect(reverse('edit_profile'))

    context = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'profile': profile_obj,
    }

    return render(request, 'profiles/profile_detail.html', context)


