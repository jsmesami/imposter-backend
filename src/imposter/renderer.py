import io
import math
import os

from django.conf import settings

from PIL import Image

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph

from imposter.models.image import PosterImage, SpecImage

__all__ = 'Renderer',


class TextFrame:
    def __init__(self, **kwargs):
        self.params = kwargs
        self.style = ParagraphStyle(
            name='Normal',
            fontName=settings.RENDERER['default_font_name'],
            fontSize=settings.RENDERER['default_font_size'],
            textColor=settings.RENDERER['default_text_color'],
            leading=settings.RENDERER['default_font_size'] * 1.2
        )

    def draw(self, canvas):
        x = self.params['x'] * mm
        y = self.params['y'] * mm
        w = self.params.get('w', 0) * mm
        h = self.params.get('h', 0) * mm
        align = self.params.get('align', 'left')
        color = self.params.get('color', settings.RENDERER['default_text_color'])
        font_size = self.params.get('font_size', settings.RENDERER['default_font_size'])
        text = self.change_case(self.params['text'], self.params.get('case', 'initial'))

        canvas.setFont(settings.RENDERER['default_font_name'], font_size)
        canvas.setFillColor(color)

        if w and h:
            self.draw_frame(canvas, x, y, w, h, text)
        else:
            self.draw_string(canvas, x, y, align, text)

    def draw_string(self, canvas, x, y, alignment, text):
        method = {
            'left': canvas.drawString,
            'center': canvas.drawCentredString,
            'right': canvas.drawRightString,
        }

        method[alignment](x, y, text)

    def draw_frame(self, canvas, x, y, w, h, text):
        frame = Frame(x, y, w, h, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
        frame.add(Paragraph(text, self.style), canvas)

    def change_case(self, text, case):
        method = {
            'upper': lambda t: t.upper(),
            'lower': lambda t: t.lower(),
        }

        return text if case == 'initial' else method[case](text)


class ImageFrame:

    def __init__(self, image, **kwargs):
        self.params = kwargs
        self.image = image

    def draw(self, canvas):
        x = self.params['x'] * mm
        y = self.params['y'] * mm
        w = self.params.get('w', 0) * mm
        h = self.params.get('h', 0) * mm
        scaling_method = self.params.get('scale')

        if w and h:
            path = self._scale(self.image.file.path, scaling_method, w, h)
            canvas.drawImage(path, x, y, w, h, preserveAspectRatio=True)
        else:
            canvas.drawImage(self.image.file.path, x, y)

    @classmethod
    def _scale(cls, orig_path, method, w, h):
        """
        Scale an image to the aspect ratio specified, leave untouched if the original ratio almost equals.
        """
        img = Image.open(orig_path)

        orig_w, orig_h = img.size
        if math.isclose(orig_w / orig_h, w / h, abs_tol=0.06):
            return orig_path

        new_path, ext = os.path.splitext(orig_path)
        new_path = '{path}_scaled{ext}'.format(path=new_path, ext=ext)

        if method == 'crop':
            cls._crop(img, w, h).save(new_path, img.format)
            return new_path

        return orig_path

    @classmethod
    def _crop(cls, img, w, h):
        i_w, i_h = img.size
        crop_w, crop_h = cls.fit_rectangle_into_container(w, h, i_w, i_h)
        crop_x = (i_w - crop_w) / 2
        crop_y = (i_h - crop_h) / 2
        img = img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
        return img

    @staticmethod
    def fit_rectangle_into_container(rect_w, rect_h, cont_w, cont_h):
        rect_ratio = cont_w / cont_h
        cont_ratio = rect_w / rect_h
        if cont_ratio >= rect_ratio:
            scale_ratio = cont_w / rect_w
        else:
            scale_ratio = cont_h / rect_h
        return rect_w * scale_ratio, rect_h * scale_ratio


class Renderer:

    def __init__(self, spec, saved_fields):
        self.page_size = spec.w * mm, spec.h * mm
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
        default_font = settings.RENDERER.get('default_font_file')
        if default_font:
            pdfmetrics.registerFont(TTFont(settings.RENDERER['default_font_name'], default_font))

        with io.BytesIO() as buffer:
            c = canvas.Canvas(buffer)

            c.setPageSize(self.page_size)

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
            img.transform(resize=settings.RENDERER['thumbnail_size'])

            return img.make_blob()
