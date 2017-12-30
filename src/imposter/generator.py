import io

from reportlab.pdfgen import canvas
from wand.image import Image
from wand.color import Color


def render_pdf():
    with io.BytesIO() as buffer:
        c = canvas.Canvas(buffer)
        c.drawString(100, 100, "HELLO WORLD!")
        c.showPage()
        c.save()

        return buffer.getvalue()


def render_jpg(pdf):
    with Image(blob=pdf, format='pdf') as img:
        img.format = 'jpeg'
        img.background_color = Color('white')
        img.alpha_channel = 'remove'
        img.transform(resize='640x480>')

        return img.make_blob()
