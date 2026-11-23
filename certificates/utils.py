import os
import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

# Base coordinates & styling for 3508 x 2480 (A4 @ 300 DPI) certificate
TEMPLATE_WIDTH = 3508
TEMPLATE_HEIGHT = 2480
TARGET_CENTER_X = 1754
TARGET_CENTER_Y = 1220
NAVY_TEXT_COLOR = (20, 51, 76)      # Exact dark navy #14334c
GOLD_ACCENT_COLOR = (212, 175, 55)  # Certificate gold accent


def get_template_path():
    """Return path to clean certificate template image."""
    possible_paths = [
        settings.BASE_DIR / 'static' / 'certificates' / 'images' / 'template.jpg',
        settings.BASE_DIR / 'certificate_template_clean.jpg',
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return str(p)
    raise FileNotFoundError("Certificate template image not found.")


def get_font_path(font_name='AlexBrush-Regular.ttf'):
    """Return path to custom font file."""
    possible_paths = [
        settings.BASE_DIR / 'static' / 'certificates' / 'fonts' / font_name,
        settings.BASE_DIR / 'fonts' / font_name,
        settings.BASE_DIR / 'static' / 'certificates' / 'fonts' / 'GreatVibes-Regular.ttf',
        '/System/Library/Fonts/Supplemental/Zapfino.ttf',
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return str(p)
    return None


def generate_certificate_image(student_name: str) -> Image.Image:
    """
    Renders candidate name on the high-resolution certificate template.
    Returns a Pillow Image object.
    """
    # Guarantee first letter of every word is capitalized
    if student_name:
        words = student_name.strip().split()
        formatted = []
        for w in words:
            if '.' in w:
                parts = [p.capitalize() for p in w.split('.')]
                formatted.append('.'.join(parts))
            elif '-' in w:
                parts = [p.capitalize() for p in w.split('-')]
                formatted.append('-'.join(parts))
            else:
                formatted.append(w.capitalize())
        student_name = ' '.join(formatted)

    template_path = get_template_path()
    im = Image.open(template_path).convert('RGB')
    draw = ImageDraw.Draw(im)

    font_path = get_font_path('AlexBrush-Regular.ttf')
    
    # Target maximum width for student name so it never exceeds margins
    max_text_width = 2100
    font_size = 145

    if font_path:
        font = ImageFont.truetype(font_path, font_size)
    else:
        # Fallback to default if no font file found
        font = ImageFont.load_default()

    # Calculate text bounding box
    bbox = draw.textbbox((0, 0), student_name, font=font)
    text_width = bbox[2] - bbox[0]

    # Auto-scale font size if name is particularly long
    if font_path:
        while text_width > max_text_width and font_size > 65:
            font_size -= 4
            font = ImageFont.truetype(font_path, font_size)
            bbox = draw.textbbox((0, 0), student_name, font=font)
            text_width = bbox[2] - bbox[0]

    text_height = bbox[3] - bbox[1]

    # Calculate exact coordinates to center the name
    text_x = TARGET_CENTER_X - (text_width // 2)
    # Baseline vertical alignment
    text_y = TARGET_CENTER_Y - (bbox[3] + bbox[1]) // 2

    # Draw Candidate Name
    draw.text((text_x, text_y), student_name, font=font, fill=NAVY_TEXT_COLOR)

    # Draw subtle elegant accent underline matching original template
    line_y = text_y + bbox[3] + 16
    line_x1 = max(TARGET_CENTER_X - (text_width // 2) - 45, 1050)
    line_x2 = min(TARGET_CENTER_X + (text_width // 2) + 45, 2450)

    # Primary line in dark navy
    draw.line([(line_x1, line_y), (line_x2, line_y)], fill=NAVY_TEXT_COLOR, width=3)
    # Center accent mark in gold
    draw.line([(TARGET_CENTER_X - 35, line_y), (TARGET_CENTER_X + 35, line_y)], fill=GOLD_ACCENT_COLOR, width=4)

    return im


def generate_certificate_jpeg_bytes(student_name: str, quality: int = 95) -> io.BytesIO:
    """Generate JPEG binary stream for certificate."""
    im = generate_certificate_image(student_name)
    buf = io.BytesIO()
    im.save(buf, format='JPEG', quality=quality, dpi=(300, 300))
    buf.seek(0)
    return buf


def generate_certificate_pdf_bytes(student_name: str) -> io.BytesIO:
    """Generate 300 DPI Print-Ready PDF stream for certificate."""
    im = generate_certificate_image(student_name)
    buf = io.BytesIO()
    # Save as high-resolution PDF
    im.save(buf, format='PDF', resolution=300.0)
    buf.seek(0)
    return buf

