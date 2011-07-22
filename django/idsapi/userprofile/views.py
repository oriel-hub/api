from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def profile_detail(request):
    """ Detail view of a user's profile."""
    profile_obj = request.user.get_profile()
    if profile_obj.name == None or profile_obj.name == '':
        return HttpResponseRedirect(reverse('edit_profile'))
    context = RequestContext(request)
    context['email'] = request.user.email

    return render_to_response('profiles/profile_detail.html',
                              { 'profile': profile_obj },
                              context_instance=context)


