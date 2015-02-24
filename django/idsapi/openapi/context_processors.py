from django.contrib.sites.models import Site


def url_info(request):
    from .defines import URL_ROOT
    return {
        'domain_name': request.META.get('HTTP_HOST', Site.objects.get(id=1).domain),
        'url_root': URL_ROOT,
    }
