"""Build an isolated WINTER 26 product/media preview from the Issue #27 handoff.

This generator deliberately never writes to the active catalog or store media
registry. Its output is a review artifact under docs/issue-27-photo-review.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "issue-27-photo-review"
ASSET_DIR = OUT / "assets"
PREVIEW_MEDIA = OUT / "preview-media"

COLORS = [
    ("red-matte", "Czerwony", "#9f3b35"),
    ("white", "Biały", "#f3f0e8"),
    ("marble", "Biały nakrapiany (Marble)", "#d8d2c6"),
    ("dual", "Czarno-czerwony (Black / Red)", "#252723"),
    ("cappuccino", "Cappuccino", "#b18c73"),
]

MODELS = [
    ("full-soft", "VASE", "PF-W26-VASE", "VASE / full-soft", "Pełna kula o miękkim, spiralnym rytmie."),
    ("knitted-star", "KNITTED STAR", "PF-W26-STAR", "KNITTED STAR", "Pięć ażurowych ramion z reliefem splotu."),
    ("knitted-medallion", "KNITTED MEDALLION", "PF-W26-MED", "KNITTED MEDALLION", "Okrąg zamyka delikatny, ażurowy splot."),
]

# Product-level preview proposal. It is not a photoAsset assignment.
PROPOSAL = {
    ("full-soft", "dual"): {"main": "WEB009", "gallery": ["WEB011"], "detail": [], "lifestyle": ["WEB023"]},
    ("full-soft", "red-matte"): {"main": "WEB013", "gallery": [], "detail": [], "lifestyle": []},
    ("full-soft", "white"): {"main": "WEB006", "gallery": [], "detail": [], "lifestyle": ["WEB022"]},
    ("full-soft", "marble"): {"main": "WEB005", "gallery": ["WEB001"], "detail": ["WEB019", "WEB020"], "lifestyle": []},
    ("full-soft", "cappuccino"): {"main": "WEB008", "gallery": [], "detail": [], "lifestyle": ["WEB024"]},
    ("knitted-star", "dual"): {"main": None, "gallery": [], "detail": [], "lifestyle": []},
    ("knitted-star", "red-matte"): {"main": "WEB017", "gallery": [], "detail": [], "lifestyle": []},
    ("knitted-star", "white"): {"main": "WEB014", "gallery": [], "detail": ["WEB015"], "lifestyle": ["WEB025"]},
    ("knitted-star", "marble"): {"main": "WEB018", "gallery": [], "detail": [], "lifestyle": []},
    ("knitted-star", "cappuccino"): {"main": None, "gallery": [], "detail": [], "lifestyle": []},
    ("knitted-medallion", "dual"): {"main": None, "gallery": [], "detail": [], "lifestyle": []},
    ("knitted-medallion", "red-matte"): {"main": None, "gallery": [], "detail": [], "lifestyle": []},
    ("knitted-medallion", "white"): {"main": None, "gallery": [], "detail": [], "lifestyle": []},
    ("knitted-medallion", "marble"): {"main": None, "gallery": [], "detail": [], "lifestyle": []},
    ("knitted-medallion", "cappuccino"): {"main": None, "gallery": [], "detail": [], "lifestyle": []},
}


def read_mapping() -> dict[str, dict]:
    rows = {}
    with (OUT / "PHOTO_MAPPING_RECOMMENDATION.csv").open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            rows[row["asset_id"]] = row
    return rows


def label_for(color_id: str) -> str:
    return dict((cid, label) for cid, label, _ in COLORS)[color_id]


def image_path(asset_id: str) -> str:
    return f"assets/{asset_id}.jpg"


ALT_TEXT = {
    "WEB001": "Jasna nakrapiana bombka VASE na ciemnym tle, ujęcie główne.",
    "WEB005": "Jasna nakrapiana bombka VASE na ciemnym tle, ujęcie główne.",
    "WEB006": "Gładka spiralna bombka VASE na ciemnym tle, ujęcie główne.",
    "WEB008": "Ciepła beżowa spiralna bombka VASE na ciemnym tle, ujęcie główne.",
    "WEB009": "Spiralna bombka VASE w ciemnym, dwukolorowym wykończeniu, ujęcie główne.",
    "WEB011": "Spiralna bombka VASE w zbliżeniu, ujęcie główne.",
    "WEB013": "Czerwona spiralna bombka VASE na ciemnym tle, ujęcie główne.",
    "WEB014": "Ażurowa gwiazda KNITTED STAR na złotym sznurku, ujęcie główne.",
    "WEB015": "Zbliżenie ażurowej gwiazdy KNITTED STAR na sznurku.",
    "WEB016": "Ażurowy medalion KNITTED MEDALLION na złotym sznurku, ujęcie modelu.",
    "WEB017": "Ażurowa gwiazda KNITTED STAR na ciemnym tle, ujęcie główne.",
    "WEB018": "Ażurowa gwiazda KNITTED STAR w zbliżeniu, ujęcie główne.",
    "WEB019": "Zbliżenie nakrapianej powierzchni spiralnej bombki VASE.",
    "WEB020": "Zbliżenie spiralnej powierzchni bombki VASE.",
    "WEB022": "Jasna spiralna bombka VASE w zimowej aranżacji.",
    "WEB023": "Ciemna spiralna bombka VASE w zimowej aranżacji.",
    "WEB024": "Beżowa spiralna bombka VASE w zimowej aranżacji.",
    "WEB025": "Ażurowa gwiazda KNITTED STAR w zimowej aranżacji.",
}


def alt_for(asset_id: str, model: str = "", role: str = "") -> str:
    return ALT_TEXT.get(asset_id, f"{model or 'Obiekt'} — fotografia {role or 'produktu'}.")


def img(asset_id: str | None, alt: str, cls: str = "") -> str:
    if not asset_id:
        return '<div class="media-missing"><span>Brak fotografii</span><small>Do uzupełnienia przed akceptacją</small></div>'
    return f'<img class="{cls}" src="{image_path(asset_id)}" alt="{escape(alt)}" loading="lazy">'


def swatches() -> str:
    return "".join(
        f'<span class="swatch" title="{escape(label)}" style="--swatch:{hexv}"><i></i><b>{escape(label)}</b></span>'
        for _, label, hexv in COLORS
    )


def card(model: tuple, rows: dict[str, dict]) -> str:
    slug, name, sku_prefix, model_label, description = model
    first = next((v for (m, _), v in PROPOSAL.items() if m == slug and v["main"]), None)
    # WEB016 is model evidence only: it must not become a color variant.
    main_id = first["main"] if first else ("WEB016" if slug == "knitted-medallion" else None)
    main_row = rows.get(main_id or "", {})
    related = []
    for (m, _), proposal in PROPOSAL.items():
        if m != slug:
            continue
        for role in ("main", "gallery", "detail", "lifestyle"):
            ids = proposal[role] if isinstance(proposal[role], list) else ([proposal[role]] if proposal[role] else [])
            related += [(role, aid, label_for(c)) for aid in ids for c in [next((cid for mm, cid in PROPOSAL if mm == m and PROPOSAL[(mm, cid)] is proposal), "")]]
    # Keep the card editorial and use the strongest confirmed/candidate main only.
    media = img(main_id, alt_for(main_id or "", name, "główna"), "card-main-image")
    gallery_items = []
    for (m, _), proposal in PROPOSAL.items():
        if m == slug:
            gallery_items += [(aid, role) for role in ("gallery", "detail", "lifestyle") for aid in (proposal[role] if isinstance(proposal[role], list) else [])]
    gallery_items = list(dict.fromkeys(gallery_items))
    gallery = "".join(
        f'<figure>{img(aid, alt_for(aid, name, role), "gallery-image " + ("lifestyle" if role == "lifestyle" else "product"))}<figcaption>{role_label(aid, rows)}</figcaption></figure>'
        for aid, role in gallery_items
    )
    variants = []
    for cid, label, _ in COLORS:
        p = PROPOSAL[(slug, cid)]
        state = "Fotografia proponowana" if p["main"] else "Brak fotografii"
        variants.append(f'<li><span class="dot" style="--swatch:{dict((x[0],x[2]) for x in COLORS)[cid]}"></span><span><b>{escape(label)}</b><small>{state}</small></span></li>')
    source_copy = (f"Dowód geometrii: {main_id}. Nie przypisano do koloru ani SKU." if slug == "knitted-medallion" else f"Źródło główne: {main_id or 'brak'}. Kolor z fotografii jest wyłącznie kandydatem wizualnym.")
    return f'''<article class="product-preview-card" id="preview-{slug}">
      <div class="card-media">{media}<span class="preview-stamp">PREVIEW / DO AKCEPTACJI</span></div>
      <div class="card-copy"><p class="eyebrow">{escape(model_label)} · {escape(sku_prefix)}</p><h2>{escape(name)}</h2><p>{escape(description)}</p><p class="micro">{escape(source_copy)}</p>
      <div class="swatches">{swatches()}</div><ul class="variant-list">{''.join(variants)}</ul></div>
      <div class="card-gallery"><h3>Galeria / detale / lifestyle</h3>{gallery or '<p class="empty-note">Brak dodatkowych fotografii zatwierdzonych do tego modelu.</p>'}</div>
    </article>'''


def role_label(asset_id: str, rows: dict[str, dict]) -> str:
    row = rows.get(asset_id, {})
    return f'{asset_id} · {row.get("recommended_site_role", "preview")}'


def combination(model: tuple, color: tuple, rows: dict[str, dict]) -> str:
    slug, name, sku_prefix, _, _ = model
    cid, label, hexv = color
    p = PROPOSAL[(slug, cid)]
    aid = p["main"]
    row = rows.get(aid or "", {})
    image = img(aid, alt_for(aid or "", name, "główna"), "matrix-image")
    sku = f"{sku_prefix}-{cid.upper()}" if cid != "cappuccino" else f"{sku_prefix}-CAPPUCCINO (propozycja)"
    return f'''<article class="combo"><div class="combo-media">{image}</div><div><p class="eyebrow">{escape(name)}</p><h3>{escape(label)}</h3><p class="sku">{escape(sku)}</p><p class="combo-state">{('Kandydat: '+aid) if aid else 'Brak fotografii'}</p></div></article>'''


def build_media_json(rows: dict[str, dict]) -> dict:
    entries = []
    for (slug, cid), proposal in PROPOSAL.items():
        model = next(m for m in MODELS if m[0] == slug)
        for role in ("main", "gallery", "detail", "lifestyle"):
            ids = proposal[role] if isinstance(proposal[role], list) else ([proposal[role]] if proposal[role] else [])
            for aid in ids:
                row = rows[aid]
                entries.append({
                    "assetId": aid,
                    "sourceRole": row["source_role"],
                    "recommendedSiteRole": role,
                    "modelId": slug,
                    "model": model[1],
                    "colorId": cid,
                    "colorLabel": label_for(cid),
                    "kind": "fotografia",
                    "status": "preview-do-akceptacji",
                    "approved": False,
                    "alt": alt_for(aid, model[1], role),
                    "source": f'assets/{aid}.jpg',
                    "srcset": {"webp": [], "avif": [], "jpeg": [f'assets/{aid}.jpg']},
                    "derivativeStatus": "NOT RUN / BLOCKED — local WebP/AVIF encoder unavailable",
                    "note": "Kandydat wizualny; nie wpisywać do variants[].photoAsset przed akceptacją.",
                })
    return {
        "preview": True,
        "automatic_assignment_allowed": False,
        "activeCatalogUntouched": True,
        "targetColors": [{"id": cid, "label": label, "displayHex": hexv, "status": "propozycja"} for cid, label, hexv in COLORS],
        "models": [{"id": slug, "name": name, "slug": slug, "skuPrefix": prefix, "existingSkuConvention": f"{prefix}-<COLOR_ID>"} for slug, name, prefix, _, _ in MODELS],
        "media": entries,
        "missing": [{"modelId": slug, "colorId": cid, "label": label_for(cid), "reason": "Brak fotografii głównej w handoffie"} for (slug, cid), proposal in PROPOSAL.items() if not proposal["main"]],
    }


def build_html(rows: dict[str, dict]) -> str:
    cards = "".join(card(model, rows) for model in MODELS)
    matrix = "".join(combination(model, color, rows) for model in MODELS for color in COLORS)
    decision = """<section class=decisions><h2>Decyzje do akceptacji</h2><ol><li>Potwierdzić wyświetlane nazwy pięciu kolorów; rekomendowany techniczny ID piątego koloru: <code>cappuccino</code>.</li><li>Potwierdzić, czy kandydaci VASE WEB006/WEB008/WEB009/WEB013 mogą wejść do katalogu po weryfikacji próbek.</li><li>Uzupełnić fotografie KNITTED STAR dla Dual i Cappuccino oraz wszystkie pięć wariantów KNITTED MEDALLION.</li><li>Potwierdzić, czy WEB015 może być detalem White KNITTED STAR, bo jego kolor pozostaje nierozpoznany.</li><li>Po akceptacji przygotować właściwe QR-y i dopiero wtedy zasilić media sklepu.</li></ol></section>"""
    html = '''<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WINTER 26 — product preview</title><link rel="stylesheet" href="../../winter-atelier.css"><style>
:root{{--ink:#1f2723;--porcelain:#f4f0e8;--surface:#e9e3d8;--muted:#68736a;--rule:#c8c9c0;--accent:#9a6b32}}*{{box-sizing:border-box}}body{{margin:0;overflow-x:hidden;background:var(--porcelain);color:var(--ink);font:15px/1.55 system-ui,sans-serif}}main{{width:min(1180px,92vw);margin:auto;padding:clamp(2rem,5vw,5rem) 0 8rem;min-width:0}}h1,h2,h3{{font-family:Georgia,serif;font-weight:400;line-height:1.05}}h1{{font-size:clamp(3rem,8vw,7.5rem);max-width:9ch;margin:.15em 0 .25em}}h2{{font-size:clamp(2rem,4vw,3.5rem);margin:0 0 1rem}}h3{{font-size:1.35rem;margin:.2rem 0}}.eyebrow{{font:600 .68rem/1.4 system-ui,sans-serif;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin:0 0 .55rem}}.lead{{font:1.18rem/1.55 Georgia,serif;max-width:42rem;color:#454d47;overflow-wrap:anywhere}}.notice{{border:1px solid var(--ink);padding:1rem 1.2rem;margin:2rem 0;background:#ede7dc;overflow-wrap:anywhere}}code{{font-family:ui-monospace,monospace}}.product-preview-card{{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(300px,.9fr);gap:2.4rem;border-top:1px solid var(--rule);padding:3rem 0;margin-top:2rem;min-width:0}}.card-media{{position:relative;background:#ded7ca;min-height:430px;display:grid;place-items:center;overflow:hidden}}.card-main-image{{width:100%;height:100%;min-height:430px;object-fit:contain;padding:1rem;display:block}}.preview-stamp{{position:absolute;top:1rem;left:1rem;background:var(--ink);color:var(--porcelain);font-size:.64rem;letter-spacing:.14em;padding:.5rem .7rem}}.card-copy{{align-self:center;min-width:0}}.card-copy h2{{font-size:clamp(2.8rem,5vw,5rem);margin:.1rem 0 .5rem}}.micro,.sku,.combo-state,.empty-note{{font-size:.78rem;color:var(--muted);overflow-wrap:anywhere}}.swatches{{display:flex;flex-wrap:wrap;gap:.5rem;margin:1.4rem 0}.swatch{{display:inline-flex;align-items:center;gap:.35rem;border:1px solid var(--rule);padding:.35rem .5rem;font-size:.72rem;background:#f8f5ee}}.swatch i,.dot{{display:inline-block;width:1rem;height:1rem;border-radius:50%;background:var(--swatch);border:1px solid #888}}.variant-list{{list-style:none;padding:0;margin:1rem 0;display:grid;grid-template-columns:1fr 1fr;gap:.4rem .8rem}}.variant-list li{{display:flex;align-items:center;gap:.45rem;font-size:.75rem;min-width:0}}.variant-list small{{display:block;color:var(--muted);font-size:.65rem}}.card-gallery{{grid-column:1/-1}}.card-gallery h3{{border-bottom:1px solid var(--rule);padding-bottom:.65rem}}.card-gallery{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}.card-gallery h3{{grid-column:1/-1}}.card-gallery figure{{margin:0;background:#e5dfd4;min-width:0}}.gallery-image.product{{display:block;width:100%;height:190px;object-fit:contain;padding:.75rem}}.gallery-image.lifestyle{{display:block;width:100%;height:190px;object-fit:cover}}figcaption{{font-size:.65rem;padding:.5rem;color:var(--muted);overflow-wrap:anywhere}}.media-missing{{min-height:190px;background:repeating-linear-gradient(-45deg,#e5dfd4,#e5dfd4 10px,#ddd5c8 10px,#ddd5c8 20px);display:grid;place-content:center;text-align:center;color:var(--muted);padding:1rem;min-width:0}}.media-missing span{{font:1.2rem Georgia,serif;color:var(--ink)}}.media-missing small{{font-size:.65rem}}.matrix{{margin-top:5rem;border-top:1px solid var(--ink);padding-top:2rem}}.matrix-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--rule);border:1px solid var(--rule)}}.combo{{background:var(--porcelain);padding:.6rem;min-width:0;overflow:hidden}}.combo-media{{background:#e5dfd4;aspect-ratio:1/1;display:grid;place-items:center;overflow:hidden}}.matrix-image{{width:100%;height:100%;object-fit:contain;padding:.5rem}}.combo h3{{font-size:1rem;margin:.35rem 0;overflow-wrap:anywhere}}.combo .eyebrow{{font-size:.55rem;margin-top:.45rem}}.combo .sku,.combo-state{{font-size:.62rem;margin:.2rem 0;overflow-wrap:anywhere}}.decisions{{background:var(--ink);color:var(--porcelain);padding:2rem;margin-top:4rem;overflow-wrap:anywhere}}.decisions h2{{color:var(--porcelain)}}.decisions li{{margin:.6rem 0}}.footer-note{{margin-top:4rem;border-top:1px solid var(--rule);padding-top:1rem;color:var(--muted);font-size:.78rem;overflow-wrap:anywhere}}@media(max-width:760px){{main{{width:min(92vw,560px)}}.product-preview-card{{grid-template-columns:1fr;gap:1.3rem;padding:2.2rem 0}}.card-media,.card-main-image{{min-height:350px}}.card-gallery{{grid-template-columns:repeat(2,1fr);gap:.6rem}}.gallery-image.product,.gallery-image.lifestyle{{height:150px}}.matrix-grid{{grid-template-columns:repeat(2,1fr)}}.matrix-grid .combo:last-child{{grid-column:1/-1}}.variant-list{{grid-template-columns:1fr}}}}
</style></head><body><main><p class=eyebrow>WINTER 26 / ISSUE #27</p><h1>Karty produktów</h1><p class=lead>Rzeczywisty podgląd trzech modeli i piętnastu potencjalnych kombinacji. Każde zdjęcie i przypisanie ma status PREVIEW / DO AKCEPTACJI.</p><div class=notice><b>To nie jest aktywny katalog.</b> Rejestr wariantów, zdjęć, cen, stanów, dostępności i checkoutu pozostaje bez zmian; w bazowej gałęzi zmieniono wyłącznie komunikaty dostawy w sekcji <code>release</code> pliku `data/winter26-products.json` (`delivery` / `carrierNotice`). Piąty kolor ma rekomendację nazwy i ID, ale nie ma jeszcze aktywnego SKU.</div><section><h2>Trzy karty produktów</h2>__CARDS__</section><section class=matrix><p class=eyebrow>02 / Porównanie</p><h2>15 potencjalnych kombinacji</h2><p class=lead>Brak fotografii oznacza realną lukę w pakiecie, nie zastępczy obraz.</p><div class=matrix-grid>__MATRIX__</div></section>__DECISIONS__<p class=footer-note>Źródła: 08_PRODUCT_WEB_HANDOFF / PHOTO_MAPPING_RECOMMENDATION.csv. Kolor fotografii nie jest dowodem filamentu ani materiału. QR i identyfikatory produkcyjne pozostają do uzupełnienia po akceptacji.</p></main></body></html>'''
    return html.replace("{{", "{").replace("}}", "}").replace("__CARDS__", cards).replace("__MATRIX__", matrix).replace("__DECISIONS__", decision)


def build_print_html(rows: dict[str, dict]) -> str:
    """Create a print-ready A6 proof source; Chrome exports it to PDF."""
    pages = []
    main_for_model = {"full-soft": "WEB005", "knitted-star": "WEB014", "knitted-medallion": "WEB016"}
    urls = {
        "full-soft": "https://pracowniaform.com/winter-full-soft.html",
        "knitted-star": "https://pracowniaform.com/winter-knitted-star.html",
        "knitted-medallion": "https://pracowniaform.com/winter-knitted-medallion.html",
    }
    for slug, name, prefix, model_label, description in MODELS:
        aid = main_for_model[slug]
        row = rows[aid]
        color_rows = "".join(
            f'<li><i style="background:{hexv}"></i><span><b>{escape(label)}</b><small>ID: {escape(cid)}{" · propozycja" if cid == "cappuccino" else ""}</small></span></li>'
            for cid, label, hexv in COLORS
        )
        pages.append(f'''<section class="print-card"><div class="top"><span>WINTER 26</span><b>PREVIEW / DO AKCEPTACJI</b></div><div class="image-wrap"><img src="{image_path(aid)}" alt="{escape(alt_for(aid, name, "główna"))}"></div><p class="eyebrow">{escape(model_label)} · {escape(prefix)}</p><h1>{escape(name)}</h1><p class="desc">{escape(description)}</p><p class="source">Zdjęcie propozycji: {aid}. Kolor i materiał nie są jeszcze zatwierdzone.</p><div class="colour-block"><p class="label">PALETA ROBOCZA / 5 KOLORÓW</p><ul>{color_rows}</ul></div><div class="bottom"><div class="qr"><span>QR</span><small>do generacji po akceptacji</small></div><div><p class="label">STRONA PRODUKTU</p><a href="{urls[slug]}">{urls[slug]}</a><p class="blank">Materiał / producent / pielęgnacja / GPSR: do uzupełnienia.</p></div></div></section>''')
    return '''<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>WINTER 26 / A6 product cards</title><style>
@page{size:A6;margin:0}*{box-sizing:border-box}html,body{margin:0;padding:0;background:#e6e0d6;color:#1f2723;font-family:Arial,sans-serif}.print-card{width:105mm;height:148mm;page-break-after:always;background:#f4f0e8;padding:7mm;overflow:hidden}.print-card:last-child{page-break-after:auto}.top{display:flex;justify-content:space-between;align-items:center;font-size:6pt;letter-spacing:.12em}.top b{background:#1f2723;color:#f4f0e8;padding:3px 5px;font-size:5.2pt}.image-wrap{height:43mm;margin:4mm 0 3mm;background:#ded7ca;overflow:hidden;display:grid;place-items:center}.image-wrap img{width:100%;height:100%;object-fit:contain;padding:3mm;display:block}.eyebrow,.label{font-size:5.6pt;letter-spacing:.15em;text-transform:uppercase;color:#68736a;margin:0 0 1.5mm}.print-card h1{font:normal 22pt Georgia,serif;margin:0 0 1.5mm;line-height:1}.desc{font:8pt Georgia,serif;line-height:1.2;margin:0 0 1.5mm;max-width:80mm}.source{font-size:5.8pt;line-height:1.2;color:#68736a;border-top:1px solid #c8c9c0;padding-top:1.5mm}.colour-block{border-top:1px solid #c8c9c0;margin-top:2mm;padding-top:1.5mm}.colour-block ul{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(3,1fr);gap:1.2mm}.colour-block li{display:flex;align-items:center;gap:1mm;font-size:5.4pt;min-width:0}.colour-block i{width:4mm;height:4mm;border-radius:50%;border:1px solid #9a9a90;flex:none}.colour-block small{display:block;color:#68736a;font-size:4.2pt;margin-top:.2mm;white-space:nowrap}.bottom{border-top:1px solid #c8c9c0;margin-top:2mm;padding-top:2mm;display:grid;grid-template-columns:18mm 1fr;gap:3mm;align-items:center}.qr{width:17mm;height:17mm;border:1px solid #1f2723;display:grid;place-content:center;text-align:center}.qr span{font:bold 13pt Arial}.qr small{font-size:4.3pt;line-height:1.05;padding:0 1mm}.bottom a{font-size:5.8pt;overflow-wrap:anywhere;color:#1f2723}.blank{font-size:5pt;color:#68736a;line-height:1.15;margin:1.5mm 0 0}
</style></head><body>__PAGES__</body></html>'''.replace("__PAGES__", "".join(pages))


def build_converter_html(rows: dict[str, dict]) -> str:
    assets = [f"WEB{i:03d}" for i in range(1, 27)]
    payload = json.dumps(assets, ensure_ascii=False)
    return f'''<!doctype html><meta charset="utf-8"><title>WINTER 26 preview media converter</title><p>Generating local preview derivatives…</p><pre id=log></pre><script>
const assets={payload}, sizes=[360,680,1120], log=document.querySelector('#log');
function say(x){{log.textContent+=x+'\\n';}}
async function one(id){{const image=new Image(); image.src='assets/'+id+'.jpg'; await image.decode(); for(const w of sizes){{const h=Math.round(image.naturalHeight*w/image.naturalWidth); const canvas=document.createElement('canvas'); canvas.width=w; canvas.height=h; canvas.getContext('2d').drawImage(image,0,0,w,h); for(const [type,ext,quality] of [['image/webp','webp',.82],['image/avif','avif',.6]]){{const url=canvas.toDataURL(type,quality); if(!url.startsWith('data:'+type)){{say(id+' '+ext+' unsupported'); continue}} const a=document.createElement('a'); a.href=url; a.download=id+'-'+w+'.'+ext; a.textContent=id+'-'+w+'.'+ext; a.className='derivative'; document.body.append(a);}}}} say(id+' done')}}
(async()=>{{for(const id of assets) await one(id); say('DONE')}})();
</script>'''


def main() -> None:
    rows = read_mapping()
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW_MEDIA.mkdir(parents=True, exist_ok=True)
    (OUT / "product-preview.html").write_text(build_html(rows), encoding="utf-8")
    print_html = build_print_html(rows).replace("@page{size:A6;margin:0}", "@page{size:105mm 148mm;margin:0}")
    (OUT / "product-cards-print.html").write_text(print_html, encoding="utf-8")
    (OUT / "media-converter.html").write_text(build_converter_html(rows), encoding="utf-8")
    (OUT / "store-media.preview.json").write_text(json.dumps(build_media_json(rows), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Keep a manifest of the optimized derivative contract. The source JPGs are
    # preserved. If the local encoder is available, the next pipeline step can
    # fill these paths without changing the preview mapping.
    (PREVIEW_MEDIA / "README.md").write_text("""# Preview media derivatives\n\nThis directory is reserved for 360/680/1120 WebP and AVIF derivatives of the handoff JPGs. Originals remain in `../assets/`. The preview JSON references these paths but does not activate them in the store registry.\n\nLocal image encoders were not assumed by this generator; the QA report records whether derivatives were produced.\n""", encoding="utf-8")
    print(f"Built {OUT / 'product-preview.html'}")
    print(f"Built {OUT / 'store-media.preview.json'}")


if __name__ == "__main__":
    main()
