"""Optional Pillow utility: compose actual browser screenshots, never fabricate UI."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / 'docs' / 'previews'
FONT = 'C:/Windows/Fonts/arial.ttf'

def label(draw, xy, text, size=24):
    draw.text(xy, text, fill='#25231f', font=ImageFont.truetype(FONT, size))

def crop_scaled(file, crop_height, width):
    im = Image.open(ROOT / file).convert('RGB')
    im = im.crop((0, 0, im.width, min(crop_height, im.height)))
    return im.resize((width, round(im.height * width / im.width)), Image.Resampling.LANCZOS)

board = Image.new('RGB', (1600, 1410), '#f2eee6')
draw = ImageDraw.Draw(board)
label(draw, (40, 24), 'PRACOWNIA FORM / WINTER 26 / WARM MINIMAL', 28)
label(draw, (40, 70), 'Desktop 1440 px — fragment rzeczywistego podglądu', 18)
label(draw, (1190, 70), 'Mobile 390 px', 18)
board.paste(crop_scaled('winter-26-desktop.jpg', 1580, 1100), (40, 110))
board.paste(crop_scaled('winter-26-mobile.jpg', 1250, 350), (1190, 110))
label(draw, (40, 1360), 'Pełne zrzuty strony i dokumentów: docs/PREVIEWS.md | Sprzedaż i płatności nieaktywne', 20)
board.save(ROOT / 'winter-overview.jpg', quality=90)

board = Image.new('RGB', (1600, 1820), '#f2eee6')
draw = ImageDraw.Draw(board)
label(draw, (35, 25), 'DOKUMENTY / WARM MINIMAL / DESKTOP + MOBILE', 28)
pages = [('regulamin-sklepu', 'Regulamin sklepu'), ('zwroty-i-reklamacje', 'Zwroty i reklamacje'),
         ('dostawa-i-platnosci', 'Dostawa i płatności'), ('polityka-prywatnosci', 'Prywatność'),
         ('zasady-premiery', 'Lista premierowa'), ('formularz-odstapienia', 'Odstąpienie')]
for i, (page, title) in enumerate(pages):
    x, y = 35 + (i % 2) * 795, 100 + (i // 2) * 550
    label(draw, (x, y), title, 22)
    board.paste(crop_scaled(page + '-desktop.jpg', 1250, 530), (x, y + 38))
    board.paste(crop_scaled(page + '-mobile.jpg', 940, 185), (x + 550, y + 38))
label(draw, (35, 1770), 'Fragmenty prawdziwych zrzutów; pełne dokumenty i obrazy w docs/PREVIEWS.md', 20)
board.save(ROOT / 'documents-overview.jpg', quality=90)

# Small, full-length contact sheet for visual QA of the complete layouts.
board = Image.new('RGB', (1600, 1800), '#f2eee6')
draw = ImageDraw.Draw(board)
for i, page in enumerate(['winter-26', 'index'] + [p for p, _ in pages]):
    x = 10 + i * 200
    label(draw, (x, 10), page[:20], 12)
    for size, y, height in [('desktop', 40, 820), ('mobile', 900, 870)]:
        im = Image.open(ROOT / f'{page}-{size}.jpg').convert('RGB')
        im.thumbnail((185, height), Image.Resampling.LANCZOS)
        board.paste(im, (x, y))
board.save(ROOT / 'full-layout-review.jpg', quality=90)
print('Created screenshot overview boards and full-length visual QA sheet.')
