"""
Tests for the oauth2_requests utility methods and classes.
"""
import ddt
import mock
from django.test import TestCase

from api_client.oauth2_requests import get_and_unpaginate


@ddt.ddt
class TestGetAndUnpaginate(TestCase):
    """
    Tests the get_and_unpaginate method and its options.
    """
    MAX_PAGE = 5

    def setUp(self):
        def build_test_url(page, numbered=False, format_=None):
            if 0 < page <= self.MAX_PAGE:
                return 'http://example.test/api/{}{}?page={}'.format(
                    '{}/'.format(format_.strip('/')) if format_ else '',
                    'numbered' if numbered else '',
                    page
                )
            return None

        def get_pagination(page, numbered=False):
            return {
                'count': 10,
                'previous': build_test_url(page - 1, numbered=True),
                'next': build_test_url(page + 1, numbered=True),
                'num_pages': self.MAX_PAGE,
            }

        self.paginated_url = build_test_url(1)
        self.data = {
            build_test_url(page): {
                'pagination': get_pagination(page),
                'results': [
                    {
                        'name': 'page-{}-object-{}'.format(page, num)
                    }
                    for num in range(2)
                ]
            }
            for page in range(1, self.MAX_PAGE + 1)
        }
        self.data.update({
            build_test_url(page, numbered=True): {
                'pagination': get_pagination(page, numbered=True),
                'results': [
                    {
                        'name': 'page-{}-object-{}'.format(page, num)
                    }
                    for num in range(2)
                ]
            }
            for page in range(1, self.MAX_PAGE + 1)
        })
        self.numbered_url = build_test_url(1, numbered=True)

        self.paginated_url_simplified = build_test_url(1, format_='simplified')
        self.data.update({
            build_test_url(page, format_='simplified'): {
                'count': 10,
                'previous': build_test_url(page - 1, format_='simplified'),
                'next': build_test_url(page + 1, format_='simplified'),
                'num_pages': self.MAX_PAGE,
                'results': [
                    {
                        'name': 'page-{}-object-{}'.format(page, num)
                    }
                    for num in range(2)
                ],
            }
            for page in range(1, self.MAX_PAGE + 1)
        })

        self.unpaginated_url = 'http://example.test/api/unpaginated'
        self.data.update({
            self.unpaginated_url: {
                'results': [
                    {
                        'name': 'unpaginated-object-{}'.format(num)
                    }
                    for num in range(2)
                ]
            }
        })

        self.mock_session = mock.Mock()
        self.mock_session.get = lambda url: mock.Mock(json=lambda: self.data[url])
        self.mock_session.post = lambda url, json: mock.Mock(json=lambda: self.data[url])

    def _assert_data(self, data, max_page):
        """
        Check that the returned data has data from the max_page.
        """
        max_page = min(max_page or self.MAX_PAGE, self.MAX_PAGE)
        self.assertTrue(data[-1]['name'].startswith('page-{}'.format(max_page)))

    @ddt.data(
        (None, 10, False),  # No page limit should return all objects
        (3, 6, False),
        (8, 10, False),  # Page count over max should return all objects
        # Same tests, but using a POST requests
        (None, 10, True),  # No page limit should return all objects
        (3, 6, True),
        (8, 10, True),  # Page count over max should return all objects
    )
    @ddt.unpack
    def test_get_and_unpaginate(self, max_page, count, use_post):
        data = get_and_unpaginate(self.paginated_url, self.mock_session, max_page=max_page, use_post=use_post)
        self.assertEqual(len(data), count)
        self._assert_data(data, max_page)

    @ddt.data(
        (None, 10),  # No page limit should return all objects
        (3, 6),
        (8, 10),  # Page count over max should return all objects
    )
    @ddt.unpack
    def test_get_and_unpaginate_numbered(self, max_page, count):
        data = get_and_unpaginate(self.numbered_url, self.mock_session, max_page=max_page)
        self.assertEqual(len(data), count)
        self._assert_data(data, max_page)

    @ddt.data(
        (None, 10),  # No page limit should return all objects
        (3, 6),
        (8, 10),  # Page count over max should return all objects
    )
    @ddt.unpack
    def test_get_and_unpaginate_simplified(self, max_page, count):
        data = get_and_unpaginate(self.paginated_url_simplified, self.mock_session, max_page=max_page)
        self.assertEqual(len(data), count)
        self._assert_data(data, max_page)

    def test_get_and_unpaginate_non_paginated_url(self):
        data = get_and_unpaginate(self.unpaginated_url, self.mock_session)
        self.assertEqual(len(data), 2)
