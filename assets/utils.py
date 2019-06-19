import os

from django.conf import settings


def build_file_list(folder, ext, v2=False):
    current_dir = os.getcwd()
    root_dir = settings.ASSETS_SOURCE_ROOT_V2 if v2 else settings.ASSETS_SOURCE_ROOT
    os.chdir(os.path.join(root_dir, folder))
    matching_files = []
    for root, dirs, files in os.walk('.', topdown=True):
        folder_root = root.split('/')
        folder_root[0] = folder
        folder_name = '/'.join(folder_root)

        matching_files.extend(["/".join([folder_name, name]) for name in files if os.path.splitext(name)[-1] == ext])

    os.chdir(current_dir)

    return matching_files


def get_assets_path(relative_path, v2=False):
    root_dir = settings.ASSETS_ROOT_V2 if v2 else settings.ASSETS_ROOT
    root = str(os.path.join(settings.BASE_DIR, root_dir))
    return str(os.path.join(root, relative_path))
