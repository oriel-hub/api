from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required
def profile_detail(request):
    """ Detail view of a user's profile."""
    try:
        profile_obj = request.user.get_profile()
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/login/')
    context = RequestContext(request)
    context['email'] = request.user.email

    return render_to_response('profiles/profile_detail.html',
                              { 'profile': profile_obj },
                              context_instance=context)


