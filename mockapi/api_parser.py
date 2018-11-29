from models import MockHttpResponse


class ApiParser(object):

    _responses = []

    def __init__(self, file_path_list):
        for file_path in file_path_list:
            f = open(file_path, 'r')
            response_data = None
            for line in f:
                if line[0] == '#':
                    if response_data:
                        self._responses.append(MockHttpResponse(response_data))
                        response_data = None

                if response_data:
                    response_data += line

                if line[0:3] == '###':
                    response_data = line

            if response_data:
                self._responses.append(MockHttpResponse(response_data))

            f.close()

    def responses(self):
        return self._responses
