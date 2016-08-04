from django.conf import settings

import boto
from boto.s3.key import Key

from rest_framework.views import APIView
from rest_framework.response import Response

def get_connection_settings():
    S3_BUCKET_NAME = settings.S3_BUCKET_NAME
    S3_AWS_ACCESS_KEY_ID = settings.S3_AWS_ACCESS_KEY_ID
    S3_AWS_SECRET_ACCESS_KEY = settings.S3_AWS_SECRET_ACCESS_KEY
    if S3_BUCKET_NAME and S3_AWS_SECRET_ACCESS_KEY and S3_AWS_ACCESS_KEY_ID:
        return {"S3_BUCKET_NAME":S3_BUCKET_NAME,"S3_AWS_ACCESS_KEY_ID":S3_AWS_ACCESS_KEY_ID,
        "S3_AWS_SECRET_ACCESS_KEY":S3_AWS_SECRET_ACCESS_KEY, "S3_BUCKET_PATH":"http://s3.amazonaws.com/"+S3_BUCKET_NAME+"/"}
    else:
        return None

def push_file_to_s3(file, folder=None):
    conn_settings = get_connection_settings()
    if conn_settings:
        conn = boto.connect_s3(conn_settings.get("S3_AWS_ACCESS_KEY_ID",None),conn_settings.get("S3_AWS_SECRET_ACCESS_KEY",None))
        bucket = conn.get_bucket(conn_settings.get("S3_BUCKET_NAME", None))
        # go through each version of the file
        name = file.name
        if folder:
            name = folder+file.name
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
        conn = boto.connect_s3(conn_settings.get("S3_AWS_ACCESS_KEY_ID",None),conn_settings.get("S3_AWS_SECRET_ACCESS_KEY",None))
        bucket = conn.get_bucket(conn_settings.get("S3_BUCKET_NAME", None))
        # go through the list of files
        bucket_list = bucket.list()
        return_file_list = []
        for l in bucket_list:
            keyString = str(l.key)
            if keyString[-1:] != '/':
                return_file_list.append(conn_settings.get("S3_BUCKET_PATH", "")+keyString)

        print return_file_list
        return return_file_list
    else:
        return []


class s3file_api(APIView):
    def get(self, request):
        return Response(get_files_urls())

    def post(self, request):
        list_of_uploaded = []
        for key, file in request.FILES.iteritems():
            path = push_file_to_s3(file)
            if path:
                list_of_uploaded.append(path)
        if len(request.FILES) == len(list_of_uploaded):
            return Response({"status":"ok", "urls":list_of_uploaded})
        else:
            return Response({"status":"error", "message":"Some of the files aren't uploaded, Please upload again!", "urls":list_of_uploaded})