"""
All utilities related to queries or DB access
"""

def get_object_or_none(model, *args, **kwargs):
    """
    Returns object of Model if exists else returns None
    """
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
