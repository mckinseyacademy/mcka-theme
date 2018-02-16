import ddt

from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware

from lib.context_processors import geolocate_ip_address
from lib.middleware.handle_prior_ids import PriorIdRequest
from lib.utils import PriorIdConvert


class PriorIdsTest(TestCase):
    def test_new_from_prior_course(self):
        prior_format = "slashes:Me+MY101+2014_1"
        new_format = "Me/MY101/2014_1"

        self.assertEqual(new_format, PriorIdConvert.new_from_prior(prior_format))

    def test_new_from_prior_chapter(self):
        prior_format = "location:Me+MY101+2014_1+chapter+01d1c90e6588470b821142474f504c58"
        new_format = "i4x://Me/MY101/chapter/01d1c90e6588470b821142474f504c58"

        self.assertEqual(new_format, PriorIdConvert.new_from_prior(prior_format))

    def test_new_from_prior_page(self):
        prior_format = "location:Me+MY101+2014_1+vertical+345ebe791ee4494f963420cac9c6d7a6"
        new_format = "i4x://Me/MY101/vertical/345ebe791ee4494f963420cac9c6d7a6"

        self.assertEqual(new_format, PriorIdConvert.new_from_prior(prior_format))

    def _check_middleware_operation(self, prior_url, expect_url):
        fake_request = RequestFactory().get(prior_url)
        response = PriorIdRequest().process_request(fake_request)
        if expect_url == prior_url:
            self.assertEqual(response, None)
        else:
            self.assertEqual(response._headers['location'][1], expect_url)

    def test_middleware_course_url_path_convert(self):
        prior_url = "/courses/slashes:C1+C1+C1/cohort"
        redirect_to_url = "/courses/C1/C1/C1/cohort"
        self._check_middleware_operation(prior_url, redirect_to_url)

    def test_middleware_course_url_path_not_convert(self):
        prior_url = "/courses/C1/C1/C1/cohort"
        redirect_to_url = prior_url
        self._check_middleware_operation(prior_url, redirect_to_url)

    def test_middleware_module_url_path_convert(self):
        prior_url = "/blah/something/location:Me+MY101+2014_1+vertical+345ebe791ee4494f963420cac9c6d7a6/something_else"
        redirect_to_url = "/blah/something/i4x://Me/MY101/vertical/345ebe791ee4494f963420cac9c6d7a6/something_else"
        self._check_middleware_operation(prior_url, redirect_to_url)

    def test_middleware_module_url_path_not_convert(self):
        prior_url = "/blah/something/i4x://Me/MY101/vertical/345ebe791ee4494f963420cac9c6d7a6/something_else"
        redirect_to_url = prior_url
        self._check_middleware_operation(prior_url, redirect_to_url)

    def test_middleware_course_and_module_path_convert(self):
        prior_url = "/courses/slashes:C1+C1+C1/lessons/location:C1+C1+C1+chapter+7b5635e674e621502708dbde4594f825/module/location:C1+C1+C1+vertical+c65b10f90552e061807431380140b552"
        redirect_to_url = "/courses/C1/C1/C1/lessons/i4x://C1/C1/chapter/7b5635e674e621502708dbde4594f825/module/i4x://C1/C1/vertical/c65b10f90552e061807431380140b552"
        self._check_middleware_operation(prior_url, redirect_to_url)

    def test_middleware_course_and_module_path_not_convert(self):
        prior_url = "/courses/C1/C1/C1/lessons/i4x://C1/C1/chapter/7b5635e674e621502708dbde4594f825/module/i4x://C1/C1/vertical/c65b10f90552e061807431380140b552"
        redirect_to_url = prior_url
        self._check_middleware_operation(prior_url, redirect_to_url)


@ddt.ddt
class GeoLocateIPAddressTest(TestCase):

    def setup_session(self, request):
        """Annotate a request object with a session"""
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        request.session['country_code'] = None

    @ddt.data(
        ('8.8.8.8', 'US'),  # US Google Servers
        ('202.46.33.58', 'CN'),  # Chinese DNS Server
        ('212.28.34.65', 'DE'),  # German DNS Server
        ('127.0.0.1', None),  # Local Server
    )
    @ddt.unpack
    def test_ip_address_to_country(self, ip_address, expected_country):
        fake_request = RequestFactory().get('/')
        fake_request.META['HTTP_X_FORWARDED_FOR'] = ip_address
        fake_request.META['REMOTE_ADDR'] = ip_address
        self.setup_session(fake_request)
        data = geolocate_ip_address(fake_request)
        self.assertEqual(data['country_code'], expected_country)
