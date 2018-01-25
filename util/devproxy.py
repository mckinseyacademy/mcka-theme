"""
Basic proxy server for testing mcka_apros without nginx
Depends on twisted, so you must $ pip install twisted
Run with $ python -m util.devproxy
If you want to run this on port 80 instead of 8888,
set DEV_PROXY_PORT=80 in local_settings.py and run this with sudo.
"""
import urlparse
from twisted.internet import reactor
from twisted.web import proxy, server, vhost
from urllib import quote as urlquote

from mcka_apros import settings

PORT = getattr(settings, "DEV_PROXY_PORT", 8888)  # Note: 80 requires this to be run as root with sudo
DOMAIN = getattr(settings, "LMS_BASE_DOMAIN", "mcka.local")


def make_domain(sub, base):
    suffix = ":{}".format(PORT) if PORT != 80 else ""
    return (sub + "." + base + suffix) if sub else base+suffix
APROS_HOST = make_domain(getattr(settings, "APROS_SUB_DOMAIN", ""), DOMAIN)  # mcka.local
LMS_HOST = make_domain(getattr(settings, "LMS_SUB_DOMAIN", "lms"), DOMAIN)  # lms.mcka.local
CMS_HOST = make_domain(getattr(settings, "CMS_SUM_DOMAIN", "studio"), DOMAIN)  # studio.mcka.local

USE_APROS_PORT = getattr(settings, "DEV_PROXY_APROS_PORT", 3000)
USE_LMS_PORT = getattr(settings, "DEV_PROXY_LMS_PORT", 8000)
USE_CMS_PORT = getattr(settings, "DEV_PROXY_CMS_PORT", 3000)


class ReverseProxyResource(proxy.ReverseProxyResource):
    """
    Reverse proxy that leaves the HOST header alone.
    Also supports overriding specific paths.
    """
    def __init__(self, host, port, path, reactor = reactor, path_overrides = None):
        proxy.ReverseProxyResource.__init__(self, host, port, path)
        self.path_overrides = path_overrides
    def getChild(self, path, request):
        if self.path_overrides and path in self.path_overrides:
            return self.path_overrides[path]
        return ReverseProxyResource(
            self.host, self.port, self.path + '/' + urlquote(path, safe=""),
            self.reactor)
    def render(self, request):
        request.content.seek(0, 0)
        qs = urlparse.urlparse(request.uri)[4]
        if qs:
            rest = self.path + '?' + qs
        else:
            rest = self.path
        clientFactory = self.proxyClientFactoryClass(
            request.method, rest, request.clientproto,
            request.getAllHeaders(), request.content.read(), request)
        self.reactor.connectTCP(self.host, self.port, clientFactory)
        return server.NOT_DONE_YET


resource = vhost.NameVirtualHost()
resource.addHost("mcka.local",        ReverseProxyResource('localhost', USE_APROS_PORT, '', reactor, {
    # proxy calls to c4x to lms asset host
    "c4x": ReverseProxyResource('localhost', USE_LMS_PORT, '/c4x')
}))
resource.addHost("lms.mcka.local",    ReverseProxyResource('localhost', USE_LMS_PORT, ''))
resource.addHost("studio.mcka.local", ReverseProxyResource('localhost', USE_CMS_PORT, ''))

site = server.Site(resource)
reactor.listenTCP(PORT, site)
print("Listening on port {}...".format(PORT))
reactor.run()
