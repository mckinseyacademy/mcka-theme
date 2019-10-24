import uuid

from django.conf import settings
from django.utils.translation import ugettext as _

import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection

from rest_framework.views import APIView
from rest_framework.response import Response


def get_connection_settings():
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    S3_BUCKET_URL = settings.S3_BUCKET_URL

    S3_AWS_ACCESS_KEY_ID = None
    if hasattr(settings, "S3_AWS_ACCESS_KEY_ID"):
        S3_AWS_ACCESS_KEY_ID = settings.S3_AWS_ACCESS_KEY_ID

    S3_AWS_SECRET_ACCESS_KEY = None
    if hasattr(settings, "S3_AWS_SECRET_ACCESS_KEY"):
        S3_AWS_SECRET_ACCESS_KEY = settings.S3_AWS_SECRET_ACCESS_KEY

    if S3_BUCKET_NAME and S3_BUCKET_URL:
        return {"S3_BUCKET_NAME": S3_BUCKET_NAME, "S3_AWS_ACCESS_KEY_ID": S3_AWS_ACCESS_KEY_ID,
                "S3_AWS_SECRET_ACCESS_KEY": S3_AWS_SECRET_ACCESS_KEY, "S3_BUCKET_PATH": S3_BUCKET_URL}
    else:
        return None


def push_file_to_s3(file, folder=None):
    conn_settings = get_connection_settings()
    if conn_settings:

        if conn_settings.get("S3_AWS_ACCESS_KEY_ID", None) and conn_settings.get("S3_AWS_SECRET_ACCESS_KEY", None):
            conn = boto.connect_s3(conn_settings.get("S3_AWS_ACCESS_KEY_ID", None),
                                   conn_settings.get("S3_AWS_SECRET_ACCESS_KEY", None))
        else:
            conn = S3Connection(anon=True)

        bucket = conn.get_bucket(conn_settings.get("S3_BUCKET_NAME", None))
        # go through each version of the file
        name = file.name
        if folder:
            name = folder+file.name

        last_dot_index = name.rfind(".")
        if last_dot_index >= 0:
            name = name[:last_dot_index] + "-" + str(uuid.uuid4()) + "." + name[last_dot_index+1:]

        # create a key to keep track of our file in the storage
        k = Key(bucket)
        k.key = name
        k.set_contents_from_file(file)
        # we need to make it public so it can be accessed publicly
        # using a URL like http://s3.amazonaws.com/bucket_name/key
        k.make_public()
        return conn_settings.get("S3_BUCKET_PATH", "")+name
    else:
        return None


def get_files_urls():
    conn_settings = get_connection_settings()
    if conn_settings:
        # connect to the bucket

        if conn_settings.get("S3_AWS_ACCESS_KEY_ID", None) and conn_settings.get("S3_AWS_SECRET_ACCESS_KEY", None):
            conn = boto.connect_s3(conn_settings.get("S3_AWS_ACCESS_KEY_ID", None),
                                   conn_settings.get("S3_AWS_SECRET_ACCESS_KEY", None))
        else:
            conn = S3Connection(anon=True)

        bucket = conn.get_bucket(conn_settings.get("S3_BUCKET_NAME", None))
        # go through the list of files
        bucket_list = bucket.list()
        return_file_list = []
        for l in bucket_list:
            keyString = str(l.key)
            if keyString[-1:] != '/':
                return_file_list.append(conn_settings.get("S3_BUCKET_PATH", "")+keyString)

        print(return_file_list)
        return return_file_list
    else:
        return []


class s3file_api(APIView):
    def get(self, request):
        return Response(get_files_urls())

    def post(self, request):
        list_of_uploaded = []
        for key, file in request.files.items():
            path = push_file_to_s3(file)
            if path:
                list_of_uploaded.append(path)
        if len(request.files) == len(list_of_uploaded):
            return Response({"status": "ok", "urls": list_of_uploaded})
        else:
            return Response({"status": "error", "message": _("Some of the files aren't uploaded, Please upload again!"),
                             "urls": list_of_uploaded})
