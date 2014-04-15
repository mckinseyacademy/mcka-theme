from django.conf.urls import patterns, include, url
from django.conf import settings

from .api_parser import ApiParser
from .views import MockResponseView

def transform_chunk(chunk):
    if len(chunk) > 2 and chunk[0] == '{' and chunk[-1] == '}':
        chunk = r"(?P<{}>.*)".format(chunk[1:-1])

    return chunk

urlpatterns = patterns(
    '',
)

mock_responses = ApiParser(settings.LOCAL_MOCK_API_FILES).responses()
pattern_list = {}
for mock_response in mock_responses:
    url_chunks = mock_response._address.strip().split('/')
    url_chunks = [transform_chunk(chunk) for chunk in url_chunks if len(chunk) > 0]
    url_chunks.append('$')

    new_url = r'^'
    new_url += '/'.join(url_chunks)

    if new_url in pattern_list:
        pattern_list[new_url].append(mock_response)
    else:
        pattern_list[new_url] = [mock_response]

    #pattern_list.append((new_url, mock_response))
    #urlpatterns += patterns('', url(new_url, MockResponseView.as_view(mock_response_object=mock_response)),)

mock_urls = [key for key in pattern_list]
mock_urls = sorted(mock_urls, key=lambda x: len(x), reverse=True)
for mock_url in mock_urls:
    urlpatterns += patterns('', url(mock_url, MockResponseView.as_view(mock_responses=pattern_list[mock_url])),)
