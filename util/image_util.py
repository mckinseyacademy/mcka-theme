import io

from PIL import Image


def resize_image(uploaded_image, dimensions):
    max_width, max_height = dimensions
    image = Image.open(uploaded_image, mode='r')
    image.thumbnail([max_width, max_height], Image.ANTIALIAS)
    b = io.BytesIO()
    image.save(b, "JPEG")
    b.seek(0)
    return b
