from django.core.management.base import BaseCommand

from admin.models import ClientCustomization, LearnerDashboardTile
from django.conf import settings
from django.core.files.storage import default_storage
from util.image_util import resize_image


class Command(BaseCommand):
    help = 'Resize existing LD tiles and logos to recommended sizes'

    def resize(self, file_name, dimensions):
        image = resize_image(default_storage.open(file_name), dimensions)
        if default_storage.exists(file_name):
            default_storage.delete(file_name)

        default_storage.save(file_name, image)

    def handle(self, *args, **options):
        for customization in ClientCustomization.objects.all():
            if customization.client_logo:
                dimensions = settings.IMAGE_SIZES['client_logo']
                file_name = str(customization.client_logo.replace('/accounts/', ''))
                self.resize(file_name, dimensions)

            if customization.global_client_logo:
                dimensions = settings.IMAGE_SIZES['global_client_logo']
                file_name = str(customization.global_client_logo.replace('/accounts/', ''))
                self.resize(file_name, dimensions)

        for tile in LearnerDashboardTile.objects.all():
            if tile.background_image:
                file_name = tile.background_image.name
                dimensions = settings.IMAGE_SIZES['ld_tile_background_image']
                self.resize(file_name, dimensions)
