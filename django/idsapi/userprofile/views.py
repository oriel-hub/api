from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def profile_detail(request):
    """ Detail view of a user's profile."""
    profile_obj = request.user.userprofile
    if profile_obj.agree_to_licensing == False:
        return HttpResponseRedirect(reverse('edit_profile'))
    context = RequestContext(request)
    context['first_name'] = request.user.first_name
    context['last_name'] = request.user.last_name
    context['email'] = request.user.email

    return render_to_response('profiles/profile_detail.html',
                              { 'profile': profile_obj },
                              context_instance=context)


