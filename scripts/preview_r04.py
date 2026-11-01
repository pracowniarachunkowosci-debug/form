"""Compose real R04 browser screenshots for review (optional Pillow dependency)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / 'docs/previews'
FONT = 'C:/Windows/Fonts/arial.ttf'

def label(board, x, y, text, size=22):
    ImageDraw.Draw(board).text((x, y), text, fill='#d1b889', font=ImageFont.truetype(FONT, size))

def shot(name, width, crop_height=None, crop_top=0):
    im = Image.open(ROOT / name).convert('RGB')
    if crop_height: im = im.crop((0, crop_top, im.width, min(crop_top + crop_height, im.height)))
    return im.resize((width, round(im.height * width / im.width)), Image.Resampling.LANCZOS)

board = Image.new('RGB', (1600, 1410), '#12110f')
label(board, 40, 24, 'PRACOWNIA FORM / R04 / WINTER AFTER DARK', 28)
label(board, 40, 70, 'Desktop 1440 px / projekt', 18)
label(board, 1190, 70, 'Mobile 390 px', 18)
board.paste(shot('winter-r04-hero-desktop.jpg', 1100), (40, 110))
label(board, 40, 900, 'Kontrastowe sekcje produktu / fragment', 18)
board.paste(shot('winter-r04-products-desktop.jpg', 1100, 500, 110), (40, 935))
board.paste(shot('winter-r04-hero-mobile.jpg', 350), (1190, 110))
label(board, 40, 1360, 'Editorial AI bez produktów / zachowany układ / draft do decyzji / bez publikacji', 20)
board.save(ROOT / 'winter-r04-overview.jpg', quality=90)

board = Image.new('RGB', (1600, 680), '#12110f')
label(board, 40, 25, 'SPÓJNOŚĆ MARKI / DESKTOP 1440', 26)
label(board, 40, 70, 'Aktualny homepage — produkcja, tylko odczyt', 18)
label(board, 820, 70, 'WINTER AFTER DARK — R04, lokalny draft', 18)
board.paste(shot('homepage-production-desktop.jpg', 740), (40, 110))
board.paste(shot('winter-r04-hero-desktop.jpg', 740), (820, 110))
label(board, 40, 642, 'Wspólne: ciemna baza, ciepłe światło, szeryfowa typografia i champagne / bez zmiany produkcji', 18)
board.save(ROOT / 'r04-homepage-comparison-desktop.jpg', quality=90)

board = Image.new('RGB', (840, 1430), '#12110f')
label(board, 30, 24, 'SPÓJNOŚĆ MARKI / MOBILE 390', 26)
label(board, 30, 70, 'Homepage / produkcja', 18)
label(board, 435, 70, 'WINTER / R04 draft', 18)
board.paste(shot('homepage-production-mobile.jpg', 375), (30, 110))
board.paste(shot('winter-r04-hero-mobile.jpg', 375), (435, 110))
label(board, 30, 1380, 'Rzeczywiste zrzuty przeglądarki / bez publikacji', 18)
board.save(ROOT / 'r04-homepage-comparison-mobile.jpg', quality=90)
print('Created R04 overview and homepage comparisons from actual browser captures.')
