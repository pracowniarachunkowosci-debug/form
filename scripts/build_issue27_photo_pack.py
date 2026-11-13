"""Build the visual decision pack for the WINTER 26 photo handoff."""
from __future__ import annotations

import argparse
import csv
import html
import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image as ReportImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


CATALOG_MODELS = [
    ("VASE", "full-soft", "assets/store/full-soft-360.webp"),
    ("KNITTED STAR", "knitted-star", "assets/store/star-360.webp"),
    ("KNITTED MEDALLION", "knitted-medallion", "assets/store/medallion-detail-360.webp"),
]
COLORS = ["dual", "red-matte", "white", "marble"]

# Recommendation layer only. This is deliberately separate from the manifest and
# never writes to data/winter26-products.json or variants[].photoAsset.
MAPPING = {
    "WEB001": ("VASE", "nierozpoznany", "wysoka", "confirmed geometry", "004 and 238 were confirmed by the owner as the same light speckled VASE geometry; color/material are not proven."),
    "WEB002": ("VASE", "nierozpoznany", "średnia", "candidate", "Spiral form is visually compatible with VASE, but the owner confirmed only 004/238, not 008."),
    "WEB003": ("VASE", "nierozpoznany", "średnia", "candidate", "Spiral form is visually compatible with VASE, but the owner did not confirm its relation to 004/238."),
    "WEB004": ("VASE", "nierozpoznany", "średnia", "candidate", "Light speckled spiral appearance is compatible with the VASE family; relation to 004/238 remains open."),
    "WEB005": ("VASE", "nierozpoznany", "wysoka", "confirmed geometry", "238 was confirmed as the same light speckled VASE geometry as 004; visible color/material remain unconfirmed."),
    "WEB006": ("VASE", "white", "średnia", "owner decision required", "Separate smoother spiral variant; white is only a visual color candidate, not evidence of a specific material or filament."),
    "WEB007": ("poza ofertą", "nierozpoznany", "wysoka", "unmatched/outside current assortment", "Flattened rosette geometry does not match the current VASE, KNITTED STAR or KNITTED MEDALLION catalog."),
    "WEB008": ("VASE", "nierozpoznany", "średnia", "candidate", "Full spiral silhouette is compatible with VASE, but the relation to 244 and the catalog color are unconfirmed."),
    "WEB009": ("VASE", "dual", "średnia", "owner decision required", "248 belongs to the visually similar 248/255 Dual candidate family; exact SKU/color and role remain unconfirmed."),
    "WEB010": ("poza ofertą", "nierozpoznany", "wysoka", "unmatched/outside current assortment", "250 was confirmed as a separate rosette form, not a detail of spiral VASE."),
    "WEB011": ("VASE", "dual", "średnia", "owner decision required", "255 is visually similar to 248 and is a Dual candidate; no automatic SKU or color assignment."),
    "WEB012": ("poza ofertą", "red-matte", "wysoka", "unmatched/outside current assortment", "257 was confirmed as a different rosette geometry from 258; red is visual only and no current SKU matches safely."),
    "WEB013": ("VASE", "red-matte", "średnia", "owner decision required", "258 looks like a red spiral VASE; red-matte is a color candidate only and must not be inferred as material."),
    "WEB014": ("KNITTED STAR", "nierozpoznany", "wysoka", "confirmed geometry", "259 was confirmed as part of the KNITTED STAR geometry; exact color/SKU remains open."),
    "WEB015": ("KNITTED STAR", "nierozpoznany", "wysoka", "confirmed geometry", "260 is a detail of the confirmed KNITTED STAR family; exact color/SKU remains open."),
    "WEB016": ("KNITTED MEDALLION", "nierozpoznany", "wysoka", "confirmed geometry", "261 was confirmed as KNITTED MEDALLION; color and material remain unconfirmed."),
    "WEB017": ("KNITTED STAR", "red-matte", "wysoka", "owner decision required", "262 is a confirmed star geometry and visually red; red-matte remains a color candidate only."),
    "WEB018": ("KNITTED STAR", "nierozpoznany", "wysoka", "confirmed geometry", "263 is a confirmed star geometry; its light/warm appearance does not prove White or Marble."),
    "WEB019": ("VASE", "nierozpoznany", "wysoka", "confirmed geometry", "Detail crop of 004, whose VASE geometry matches 238 by owner confirmation."),
    "WEB020": ("VASE", "nierozpoznany", "wysoka", "confirmed geometry", "Detail crop of 238, the owner-confirmed light speckled VASE geometry."),
    "WEB021": ("poza ofertą", "nierozpoznany", "wysoka", "unmatched/outside current assortment", "Detail crop of 250; the rosette geometry is outside the current three-model catalog."),
    "WEB022": ("poza ofertą", "nierozpoznany", "średnia", "unmatched/outside current assortment", "Lifestyle image shows a flattened rosette-like object without enough evidence for one of the current three SKUs."),
    "WEB023": ("VASE", "dual", "średnia", "owner decision required", "Lifestyle image is visually compatible with the dark spiral family around 248/255; Dual is only a visual candidate."),
    "WEB024": ("VASE", "nierozpoznany", "średnia", "owner decision required", "Lifestyle image shows a beige spiral form; beige is not a current catalog color and the exact SKU is unconfirmed."),
    "WEB025": ("KNITTED STAR", "nierozpoznany", "średnia", "candidate", "Lifestyle image visibly shows a star geometry compatible with KNITTED STAR; exact variant/color is not confirmed."),
    "WEB026": ("poza ofertą", "red-matte", "średnia", "unmatched/outside current assortment", "Lifestyle image shows a red rosette-like object; do not force it into VASE or KNITTED STAR."),
}

DECISIONS = [
    ("1 · VASE candidates and roles", ["004", "238", "243", "245"], "Rekomendacja: use 004/238 as the only high-confidence VASE geometry pair; consider 243 a separate smooth candidate and 245 a lower-confidence VASE candidate. Confirm which images are accepted into the 12-variant catalog and choose main/gallery/detail."),
    ("2 · VASE colors and exclusions", ["248", "255", "258", "171", "213"], "Rekomendacja: 248/255 are the Dual candidate pair, 258 is the red VASE candidate; keep 171/213 as lifestyle candidates only until color/SKU is confirmed."),
    ("3 · Outside-current-assortment objects", ["244", "250", "257", "045", "146"], "Rekomendacja: keep these out of the three-model catalog. Their rosette/flattened geometry does not safely match VASE, KNITTED STAR or KNITTED MEDALLION."),
    ("4 · KNITTED STAR color split", ["259", "260", "262", "263", "083"], "Rekomendacja: geometry is confirmed; use 262 as the red-matte candidate, 259/263 as the light-color candidate pool, 260 as detail, and 083 only as lifestyle. Confirm White vs Marble before any SKU mapping."),
    ("5 · KNITTED MEDALLION", ["261"], "Rekomendacja: retain 261 as the sole KNITTED MEDALLION candidate, with no color or material assigned. Confirm which one of the four catalog colors it represents; all other medallion slots need new photography."),
]

CATALOG_PROPOSAL = [
    ("VASE", "full-soft", "dual", "WEB009", "WEB011", "—", "candidate pair; confirm Dual and exact main/gallery roles"),
    ("VASE", "full-soft", "red-matte", "WEB013", "—", "—", "candidate only; gallery/detail missing"),
    ("VASE", "full-soft", "white", "WEB006", "—", "—", "separate smooth spiral candidate; acceptance as current VASE required"),
    ("VASE", "full-soft", "marble", "WEB005", "WEB001", "WEB019, WEB020", "best high-confidence geometry set; color/material still require confirmation"),
    ("KNITTED STAR", "knitted-star", "dual", "—", "—", "—", "missing photography"),
    ("KNITTED STAR", "knitted-star", "red-matte", "WEB017", "—", "—", "red color candidate; gallery/detail missing"),
    ("KNITTED STAR", "knitted-star", "white", "WEB014", "WEB025 (lifestyle)", "WEB015", "candidate pool; confirm White and allow lifestyle gallery"),
    ("KNITTED STAR", "knitted-star", "marble", "WEB018", "—", "—", "candidate pool; exact color/material and gallery/detail missing"),
    ("KNITTED MEDALLION", "knitted-medallion", "dual", "—", "—", "—", "missing photography; WEB016 color unresolved"),
    ("KNITTED MEDALLION", "knitted-medallion", "red-matte", "—", "—", "—", "missing photography; no red medallion candidate"),
    ("KNITTED MEDALLION", "knitted-medallion", "white", "WEB016", "—", "—", "only provisional color slot; 261 color/material unresolved"),
    ("KNITTED MEDALLION", "knitted-medallion", "marble", "—", "—", "—", "missing photography; WEB016 cannot be duplicated before color confirmation"),
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [Path("C:/Windows/Fonts") / path, Path("/usr/share/fonts/truetype/dejavu") / path]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def register_pdf_fonts() -> None:
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.is_file() and bold.is_file():
        pdfmetrics.registerFont(TTFont("PackRegular", str(regular)))
        pdfmetrics.registerFont(TTFont("PackBold", str(bold)))
    else:
        pdfmetrics.registerFont(TTFont("PackRegular", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("PackBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFontFamily("PackRegular", normal="PackRegular", bold="PackBold")


def crop_contain(image: Image.Image, width: int, height: int, background: str = "#151B17") -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    fitted = ImageOps.contain(image, (width - 20, height - 20), method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), background)
    canvas.paste(fitted, ((width - fitted.width) // 2, (height - fitted.height) // 2))
    return canvas


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font_obj: ImageFont.ImageFont, fill: str, max_width: int | None = None) -> int:
    if max_width is None:
        draw.text(xy, text, font=font_obj, fill=fill)
        return xy[1] + font_obj.size + 4
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font_obj) > max_width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    y = xy[1]
    for current in lines:
        draw.text((xy[0], y), current, font=font_obj, fill=fill)
        y += font_obj.size + 3
    return y


def make_tile(asset: dict, source: Path, destination: Path) -> None:
    canvas = crop_contain(Image.open(source), 460, 420)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 460, 42), fill="#101510")
    draw.text((14, 11), f"{asset['source_image_id']}  /  {asset['asset_id']}", font=font("arialbd.ttf", 16), fill="#E7C982")
    draw.rectangle((0, 378, 460, 420), fill="#101510")
    draw.text((14, 387), f"{asset['image_role']} · {asset['width']}×{asset['height']}", font=font("arial.ttf", 13), fill="#F3EFE7")
    canvas.save(destination, quality=88, optimize=True)


def make_board(title: str, assets: list[dict], thumb_dir: Path, destination: Path, columns: int = 3) -> None:
    tile_w, tile_h = 460, 420
    header_h = 86
    rows = (len(assets) + columns - 1) // columns
    board = Image.new("RGB", (columns * tile_w, header_h + rows * tile_h), "#F3EFE7")
    draw = ImageDraw.Draw(board)
    draw.rectangle((0, 0, board.width, header_h), fill="#142019")
    draw.text((28, 20), title, font=font("arialbd.ttf", 27), fill="#F3EFE7")
    draw.text((28, 54), "Porównanie wizualne · geometria / kandydat / decyzja właściciela", font=font("arial.ttf", 15), fill="#E7C982")
    for index, asset in enumerate(assets):
        tile = Image.open(thumb_dir / f"{asset['asset_id']}.jpg")
        x = (index % columns) * tile_w
        y = header_h + (index // columns) * tile_h
        board.paste(tile, (x, y))
    board.save(destination, quality=88, optimize=True)


def make_catalog_board(repo_root: Path, destination: Path) -> None:
    width, height = 1800, 960
    board = Image.new("RGB", (width, height), "#F3EFE7")
    draw = ImageDraw.Draw(board)
    draw.text((48, 32), "AKTUALNY KATALOG WINTER 26", font=font("arialbd.ttf", 34), fill="#17201B")
    draw.text((48, 82), "Widok referencyjny · nie jest mapowaniem fotografii do SKU", font=font("arial.ttf", 19), fill="#66736B")
    card_w, card_h = 540, 760
    for index, (name, slug, image_path) in enumerate(CATALOG_MODELS):
        x = 48 + index * (card_w + 42)
        y = 140
        draw.rectangle((x, y, x + card_w, y + card_h), outline="#C9D0C8", width=2)
        source = repo_root / image_path
        if source.is_file():
            image = crop_contain(Image.open(source), card_w - 40, 420, "#1A1E1B")
            board.paste(image, (x + 20, y + 20))
        draw.text((x + 20, y + 462), name, font=font("arialbd.ttf", 25), fill="#17201B")
        draw.text((x + 20, y + 500), f"slug: {slug}", font=font("arial.ttf", 18), fill="#66736B")
        draw.text((x + 20, y + 550), "Kolory katalogu:", font=font("arialbd.ttf", 18), fill="#17201B")
        draw.text((x + 20, y + 584), " · ".join(COLORS), font=font("arial.ttf", 17), fill="#66736B")
        draw.text((x + 20, y + 640), "Brak przypisania photoAsset", font=font("arialbd.ttf", 17), fill="#9A6B32")
    board.save(destination, quality=90, optimize=True)


def metadata_line(asset: dict) -> str:
    candidate = asset.get("candidate_product_name") or "brak"
    slug = asset.get("candidate_product_slug") or "brak"
    return f"kandydat: {candidate} / {slug}; kolor: {asset.get('color_variant', 'brak')}; materiał: {asset.get('material_variant', 'brak')}"


def recommendation(asset: dict) -> tuple[str, str, str, str, str]:
    return MAPPING[asset["asset_id"]]


def recommendation_line(asset: dict) -> str:
    model, color, confidence, status, evidence = recommendation(asset)
    return f"rekomendacja: {model} · kolor: {color} · pewność: {confidence} · status: {status} · {evidence}"


def mapping_csv(output_dir: Path, assets: list[dict]) -> None:
    path = output_dir / "PHOTO_MAPPING_RECOMMENDATION.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["source_id", "asset_id", "filename", "role", "model", "color", "confidence", "status", "evidence"])
        for asset in assets:
            model, color, confidence, status, evidence = recommendation(asset)
            writer.writerow([asset["source_image_id"], asset["asset_id"], asset["asset_filename"], asset["image_role"], model, color, confidence, status, evidence])


def make_html(output_dir: Path, assets: list[dict], groups: list[tuple[str, list[str], str]]) -> None:
    by_source: dict[str, list[dict]] = {}
    for asset in assets:
        by_source.setdefault(str(asset["source_image_id"]), []).append(asset)
    cards = []
    for asset in assets:
        model, color, confidence, status, _evidence = recommendation(asset)
        cards.append(f"""<article class=asset-card><img src=assets/{html.escape(asset['asset_id'])}.jpg alt=\"{html.escape(asset['visual_description'])}\"><div class=asset-copy><h3>{html.escape(asset['source_image_id'])} · {html.escape(asset['asset_id'])}</h3><p><b>{html.escape(asset['image_role'])}</b> · {asset['width']}×{asset['height']} · {html.escape(asset['editing_source'])}</p><p class=filename>{html.escape(asset['asset_filename'])}</p><p>{html.escape(asset['visual_description'])}</p><p class=muted>Manifest: {html.escape(metadata_line(asset))}</p><p class=map>Rekomendacja: {html.escape(model)} · {html.escape(color)} · pewność {html.escape(confidence)}</p><p class=blocked>{html.escape(status)}</p></div></article>""")
    group_sections = []
    for title, source_ids, question in groups:
        related = [asset for asset in assets if str(asset["source_image_id"]) in source_ids]
        board_name = "board-" + "-".join(source_ids).lower() + ".jpg"
        lines = "".join(f"<li><b>{html.escape(a['source_image_id'])}</b> · {html.escape(a['asset_filename'])} · {html.escape(a['image_role'])}</li>" for a in related)
        group_sections.append(f"<section class=question><h3>{html.escape(title)}</h3><p class=question-text>{html.escape(question)}</p><img class=board src=boards/{html.escape(board_name)} alt=\"Porównanie {html.escape(title)}\"><ul>{lines}</ul></section>")
    mapping_rows = "".join(f"<tr><td>{html.escape(a['source_image_id'])}</td><td>{html.escape(a['asset_id'])}</td><td>{html.escape(a['asset_filename'])}</td><td>{html.escape(a['image_role'])}</td><td>{html.escape(recommendation(a)[0])}</td><td>{html.escape(recommendation(a)[1])}</td><td>{html.escape(recommendation(a)[2])}</td><td>{html.escape(recommendation(a)[3])}</td><td>{html.escape(recommendation(a)[4])}</td></tr>" for a in assets)
    proposal_rows = "".join(f"<tr><td>{html.escape(model)}</td><td>{html.escape(slug)}</td><td>{html.escape(color)}</td><td>{html.escape(main)}</td><td>{html.escape(gallery)}</td><td>{html.escape(detail)}</td><td>{html.escape(note)}</td></tr>" for model, slug, color, main, gallery, detail, note in CATALOG_PROPOSAL)
    html_text = f"""<!doctype html><html lang=pl><head><meta charset=utf-8><meta name=viewport content=width=device-width,initial-scale=1><title>WINTER 26 · pakiet decyzyjny fotografii</title><style>
:root{{color-scheme:light;--ink:#17201b;--paper:#f3efe7;--muted:#66736b;--gold:#9a6b32;--line:#ccd4cc}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 Arial,sans-serif}}main{{max-width:1500px;margin:auto;padding:40px 28px 80px}}h1,h2,h3{{font-family:Georgia,serif;line-height:1.1}}h1{{font-size:clamp(38px,6vw,80px);margin:.2em 0}}h2{{font-size:38px;margin:70px 0 20px;border-top:1px solid var(--line);padding-top:20px}}h3{{font-size:22px;margin:12px 0 4px}}p{{margin:8px 0}}.eyebrow{{letter-spacing:.14em;text-transform:uppercase;font-size:12px;color:var(--gold);font-weight:700}}.lead{{max-width:900px;font-size:20px}}.notice{{padding:18px 20px;border-left:4px solid var(--gold);background:#fff9ef;margin:24px 0}}.summary{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.stat{{border-top:1px solid var(--line);padding:12px 0}}.stat strong{{display:block;font:32px Georgia,serif}}.contact{{width:100%;height:auto;border:1px solid var(--line)}}.questions{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px}}.question{{border-top:1px solid var(--line);padding-top:16px}}.question-text{{font-weight:700}}.board{{width:100%;height:auto;background:#142019}}ul{{padding-left:20px}}.asset-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}}.asset-card{{background:#fff;border:1px solid var(--line)}}.asset-card img{{display:block;width:100%;background:#151b17}}.asset-copy{{padding:14px}}.asset-copy h3{{font:700 19px Arial,sans-serif;margin:0 0 6px}}.filename{{font-size:12px;overflow-wrap:anywhere;color:var(--muted)}}.muted{{font-size:13px;color:var(--muted)}}.map{{font-size:13px;color:#3c5c4b}}.blocked{{font-size:12px;color:#9a6b32;font-weight:700}}.catalog{{width:100%;border:1px solid var(--line)}}.table-wrap{{overflow:auto;background:#fff;border:1px solid var(--line)}}table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:8px 9px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{background:#142019;color:#f3efe7;position:sticky;top:0}}tr:nth-child(even){{background:#faf8f3}}footer{{margin-top:70px;border-top:1px solid var(--line);padding-top:18px;color:var(--muted)}}@media(max-width:900px){{.summary,.questions,.asset-grid{{grid-template-columns:1fr}}main{{padding:24px 15px 50px}}h2{{font-size:30px;margin-top:45px}}}}
</style></head><body><main><p class=eyebrow>WINTER 26 / ISSUE #27</p><h1>Pakiet decyzyjny fotografii</h1><p class=lead>Rekomendowane mapowanie 26 assetów do katalogu WINTER 26 na podstawie manifestu, fotografii i potwierdzeń właściciela. To propozycja do akceptacji, nie zapis do katalogu sprzedażowego.</p><div class=notice><b>Status: automatic_assignment_allowed = false.</b><br>Potwierdzone są wybrane geometrie; kolory, materiały, SKU i role katalogowe pozostają jawnie oznaczone jako kandydat lub decyzja właściciela.</div><div class=summary><div class=stat><strong>26</strong>assetów webowych</div><div class=stat><strong>23</strong>źródła zdjęciowe</div><div class=stat><strong>5</strong>decyzji właściciela</div><div class=stat><strong>0</strong>zmienionych photoAsset</div></div><h2>Wszystkie assety</h2><img class=contact src=boards/contact-sheet-all.jpg alt="Plansza kontaktowa wszystkich 26 assetów"><h2>Pięć decyzji</h2><div class=questions>{''.join(group_sections)}</div><h2>Rekomendowane mapowanie 26 assetów</h2><div class=table-wrap><table><thead><tr><th>Źródło</th><th>WEB</th><th>Plik</th><th>Rola</th><th>Model</th><th>Kolor</th><th>Pewność</th><th>Status</th><th>Uzasadnienie</th></tr></thead><tbody>{mapping_rows}</tbody></table></div><h2>Propozycja katalogu · 12 wariantów</h2><div class=table-wrap><table><thead><tr><th>Model</th><th>Slug</th><th>Kolor</th><th>Main</th><th>Galeria</th><th>Detale</th><th>Uwagi</th></tr></thead><tbody>{proposal_rows}</tbody></table></div><h2>Aktualny katalog referencyjny</h2><p>Widok modeli i kolorów jest referencją. Żadna propozycja powyżej nie jest automatycznym przypisaniem do SKU.</p><img class=catalog src=boards/catalog-reference.jpg alt="Aktualny katalog modeli i paleta kolorów"><h2>Pełne metadane assetów</h2><div class=asset-grid>{''.join(cards)}</div><footer><p>Źródło: 08_PRODUCT_WEB_HANDOFF / PRODUCT_PHOTO_MANIFEST.json. Oryginały pozostają poza repozytorium i nie zostały zmienione.</p><p>CSV: <a href=PHOTO_MAPPING_RECOMMENDATION.csv>PHOTO_MAPPING_RECOMMENDATION.csv</a> · PDF: <a href=issue-27-photo-decision-pack.pdf>issue-27-photo-decision-pack.pdf</a></p></footer></main></body></html>"""
    html_path = output_dir / "index.html"
    html_path.write_text(html_text.replace("../../output/pdf/issue-27-photo-decision-pack.pdf", "issue-27-photo-decision-pack.pdf"), encoding="utf-8")


def make_pdf(pdf_path: Path, assets: list[dict], thumb_dir: Path, board_dir: Path) -> None:
    register_pdf_fonts()
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], fontName="PackBold", fontSize=25, leading=28, textColor=colors.HexColor("#17201B"), spaceAfter=10)
    heading = ParagraphStyle("heading", parent=styles["Heading2"], fontName="PackBold", fontSize=18, leading=21, textColor=colors.HexColor("#17201B"), spaceBefore=6, spaceAfter=8)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName="PackRegular", fontSize=8.5, leading=11, textColor=colors.HexColor("#27312B"))
    small = ParagraphStyle("small", parent=body, fontSize=7, leading=9, textColor=colors.HexColor("#66736B"))
    doc = SimpleDocTemplate(str(pdf_path), pagesize=landscape(A4), rightMargin=14 * mm, leftMargin=14 * mm, topMargin=12 * mm, bottomMargin=12 * mm, title="WINTER 26 - Issue 27 photo decision pack")
    story = [Paragraph("WINTER 26 / ISSUE #27", small), Paragraph("Pakiet decyzyjny fotografii", title), Paragraph("26 assetów · 23 źródła · automatic_assignment_allowed = false", body), Spacer(1, 5 * mm), Paragraph("Ten dokument służy wyłącznie do potwierdzenia tożsamości zdjęć. Kandydaci z manifestu nie są decyzją o modelu, kolorze, materiale ani SKU.", body), Spacer(1, 5 * mm), ReportImage(str(board_dir / "contact-sheet-all.jpg"), width=252 * mm, height=112 * mm), PageBreak()]
    for title_text, source_ids, question in DECISIONS:
        board_name = "board-" + "-".join(source_ids).lower() + ".jpg"
        story.extend([Paragraph(title_text, heading), Paragraph(question, body), Spacer(1, 3 * mm), ReportImage(str(board_dir / board_name), width=252 * mm, height=108 * mm), Spacer(1, 3 * mm), Paragraph("Porównaj geometrię, powierzchnię, zawieszkę, kolor i zgodność egzemplarza. Jeśli nie ma pewności, pozostaw bez przypisania.", small), PageBreak()])
    story.append(Paragraph("Rekomendowane mapowanie 26 assetów", heading))
    mapping_rows = [[Paragraph(label, small) for label in ["Źródło / WEB", "Rola", "Model", "Kolor", "Pewność", "Status", "Uzasadnienie"]]]
    for asset in assets:
        model, color, confidence, status, evidence = recommendation(asset)
        mapping_rows.append([
            Paragraph(html.escape(f"{asset['source_image_id']} / {asset['asset_id']}"), small),
            Paragraph(html.escape(asset["image_role"]), small),
            Paragraph(html.escape(model), small),
            Paragraph(html.escape(color), small),
            Paragraph(html.escape(confidence), small),
            Paragraph(html.escape(status), small),
            Paragraph(html.escape(evidence), small),
        ])
    mapping_table = Table(mapping_rows, colWidths=[27 * mm, 21 * mm, 29 * mm, 23 * mm, 20 * mm, 34 * mm, 98 * mm], repeatRows=1)
    mapping_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#142019")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#CCD4CC")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story.extend([mapping_table, PageBreak(), Paragraph("Propozycja katalogu · 12 wariantów", heading)])
    proposal_rows = [[Paragraph(label, small) for label in ["Model", "Slug", "Kolor", "Main", "Galeria", "Detale", "Uwagi"]]]
    for model, slug, color, main, gallery, detail, note in CATALOG_PROPOSAL:
        proposal_rows.append([Paragraph(html.escape(value), small) for value in [model, slug, color, main, gallery, detail, note]])
    proposal_table = Table(proposal_rows, colWidths=[31 * mm, 32 * mm, 22 * mm, 24 * mm, 34 * mm, 30 * mm, 79 * mm], repeatRows=1)
    proposal_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#142019")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#CCD4CC")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story.extend([proposal_table, PageBreak(), Paragraph("Pełna lista assetów z metadanymi manifestu", heading)])
    story.append(Paragraph("Pełna lista assetów", heading))
    rows = [[Paragraph("Źródło / asset", small), Paragraph("Rola / wymiary", small), Paragraph("Plik", small), Paragraph("Metadane manifestu", small)]]
    for asset in assets:
        rows.append([Paragraph(f"{asset['source_image_id']} / {asset['asset_id']}", small), Paragraph(f"{asset['image_role']} / {asset['width']}×{asset['height']}", small), Paragraph(asset['asset_filename'], small), Paragraph(metadata_line(asset), small)])
    table = Table(rows, colWidths=[32 * mm, 30 * mm, 70 * mm, 110 * mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#142019")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#CCD4CC")), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.extend([table, Spacer(1, 6 * mm), Paragraph("Źródło: 08_PRODUCT_WEB_HANDOFF / PRODUCT_PHOTO_MANIFEST.json. Oryginały nie zostały zmienione.", small)])
    doc.build(story)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--pdf-output", type=Path, default=None)
    args = parser.parse_args()
    output_dir = args.output_dir or args.repo_root / "docs" / "issue-27-photo-review"
    pdf_output = args.pdf_output or args.repo_root / "output" / "pdf" / "issue-27-photo-decision-pack.pdf"
    thumb_dir = output_dir / "assets"
    board_dir = output_dir / "boards"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    board_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((args.handoff / "PRODUCT_PHOTO_MANIFEST.json").read_text(encoding="utf-8"))
    assets = sorted(manifest["assets"], key=lambda asset: asset["asset_id"])
    for asset in assets:
        source = args.handoff / asset["relative_path"]
        make_tile(asset, source, thumb_dir / f"{asset['asset_id']}.jpg")
    make_board("Wszystkie 26 assetów", assets, thumb_dir, board_dir / "contact-sheet-all.jpg", columns=4)
    for title_text, source_ids, _question in DECISIONS:
        group_assets = [asset for asset in assets if str(asset["source_image_id"]) in source_ids]
        make_board(title_text, group_assets, thumb_dir, board_dir / ("board-" + "-".join(source_ids).lower() + ".jpg"), columns=3)
    make_catalog_board(args.repo_root, board_dir / "catalog-reference.jpg")
    mapping_csv(output_dir, assets)
    make_html(output_dir, assets, DECISIONS)
    pdf_output.parent.mkdir(parents=True, exist_ok=True)
    make_pdf(pdf_output, assets, thumb_dir, board_dir)
    tracked_pdf = output_dir / "issue-27-photo-decision-pack.pdf"
    shutil.copy2(pdf_output, tracked_pdf)
    print(f"HTML: {output_dir / 'index.html'}")
    print(f"PDF: {pdf_output}")
    print(f"TRACKED_PDF: {tracked_pdf}")
    print(f"ASSETS: {len(assets)} thumbnails, {len(DECISIONS)} decision boards, {len(CATALOG_PROPOSAL)} catalog proposals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
