def url_info(request):
    from .defines import URL_ROOT
    return {
        'domain_name': request.META['HTTP_HOST'],
        'url_root': URL_ROOT,
    }
