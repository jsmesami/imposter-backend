import io

from reportlab.lib.colors import black
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from imposter.models.image import PosterImage, SpecImage

__all__ = 'Renderer',


class TextFrame:

    def __init__(self, **kwargs):
        self.params = kwargs

    def draw(self, canvas):
        x = self.params['x'] * mm
        y = self.params['y'] * mm
        text = self.params['text']
        canvas.drawString(x, y, text)


class ImageFrame:

    def __init__(self, image, **kwargs):
        self.params = kwargs
        self.image = image

    def draw(self, canvas):
        x = self.params['x'] * mm
        y = self.params['y'] * mm
        color = self.params.get('color', black)
        canvas.setFillColor(color)
        canvas.drawImage(self.image.file.path, x, y)


class Renderer:

    def __init__(self, spec, saved_fields):
        self.elements = []

        def get_element(field_name, field_params, images_lookup):
            if field_params['type'] == 'text':
                return TextFrame(**spec.frames[field_name], **field_params)
            else:
                return ImageFrame(images_lookup[field_params['id']], **spec.frames[field_name], **field_params)

        spec_image_ids = {f['id'] for f in spec.static_fields.values() if f['type'] == 'image'}
        spec_images_lookup = {i.pk: i for i in SpecImage.objects.filter(id__in=spec_image_ids)}

        for (name, params) in spec.static_fields.items():
            self.elements.append(get_element(name, params, spec_images_lookup))

        # Filter out fields that are not filled
        poster_fields = {k: v for (k, v) in saved_fields.items() if v.get('id') or v.get('text')}
        poster_image_ids = {f['id'] for f in poster_fields.values() if f['type'] == 'image'}
        poster_images_lookup = {i.pk: i for i in PosterImage.objects.filter(id__in=poster_image_ids)}

        for (name, params) in poster_fields.items():
            self.elements.append(get_element(name, params, poster_images_lookup))

    def render_pdf(self):
        with io.BytesIO() as buffer:
            c = canvas.Canvas(buffer)

            for el in self.elements:
                el.draw(c)

            c.showPage()
            c.save()

            return buffer.getvalue()

    def render_jpg(self, pdf):
        from wand.image import Image
        from wand.color import Color

        with Image(blob=pdf, format='pdf') as img:
            img.format = 'jpeg'
            img.background_color = Color('white')
            img.alpha_channel = 'remove'
            img.transform(resize='640x480>')

            return img.make_blob()
