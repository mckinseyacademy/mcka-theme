from django.http import HttpResponseRedirect

from lib.utils import PriorIdConvert

CONVERT_SEGMENTS = [
    "slashes",
    "location",
]


class PriorIdRequest(object):

    def process_request(self, request):
        redirect = False
        url_path = request.path
        url_segments = url_path.split('/')
        for segment_index in range(0, len(url_segments)):
            url_segment = url_segments[segment_index]
            test_segment = url_segment.split(':')
            if len(test_segment) == 2 and test_segment[0] in CONVERT_SEGMENTS:
                url_segments[segment_index] = PriorIdConvert.new_from_prior(url_segment)
                redirect = True

        if redirect:
            return HttpResponseRedirect('/'.join(url_segments))
