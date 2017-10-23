"""
Serializers for public_api app
"""
from rest_framework import serializers


class ResetPasswordSerializer(serializers.Serializer):
    """
    Reset password serializer
    """
    email = serializers.EmailField()
