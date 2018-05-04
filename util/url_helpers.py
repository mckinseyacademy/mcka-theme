from urlparse import urlparse


def get_referer_from_request(request):
    referer = request.META.get('HTTP_REFERER')
    return urlparse(referer).path or None
