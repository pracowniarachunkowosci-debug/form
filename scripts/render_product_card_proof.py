"""Render a conservative A6 product-card proof from the current WINTER 26 catalog."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A6
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class QRPlaceholder(Flowable):
    def __init__(self, width: float = 22 * mm, height: float = 22 * mm) -> None:
        super().__init__()
        self.width = width
        self.height = height

    def draw(self) -> None:
        self.canv.setStrokeColor(colors.HexColor("#1F2723"))
        self.canv.rect(0, 0, self.width, self.height, stroke=1, fill=0)
        self.canv.setFont("PFRegular", 5.5)
        self.canv.setFillColor(colors.HexColor("#1F2723"))
        self.canv.drawCentredString(self.width / 2, self.height / 2, "QR / DO UZUPELNIENIA")


def register_fonts() -> None:
    regular = Path("C:/Windows/Fonts/arial.ttf")
    bold = Path("C:/Windows/Fonts/arialbd.ttf")
    if regular.is_file() and bold.is_file():
        pdfmetrics.registerFont(TTFont("PFRegular", str(regular)))
        pdfmetrics.registerFont(TTFont("PFBold", str(bold)))
    else:
        pdfmetrics.registerFont(TTFont("PFRegular", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
        pdfmetrics.registerFont(TTFont("PFBold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    pdfmetrics.registerFontFamily("PFRegular", normal="PFRegular", bold="PFBold")


def build(output: Path, catalog_path: Path) -> None:
    register_fonts()
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    pricing_path = catalog_path.with_name("winter26-pricing-pl.json")
    pricing = json.loads(pricing_path.read_text(encoding="utf-8"))
    eligible = set(pricing["eligibleModelIds"])
    products = [p for p in catalog["products"] if p["type"] == "pojedynczy" and p["id"] in eligible]
    styles = getSampleStyleSheet()
    eyebrow = ParagraphStyle("eyebrow", parent=styles["Normal"], fontName="PFBold", fontSize=6.5, leading=8, textColor=colors.HexColor("#71806D"), spaceAfter=2)
    title = ParagraphStyle("title", parent=styles["Title"], fontName="PFBold", fontSize=17, leading=18, textColor=colors.HexColor("#17201B"), spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName="PFRegular", fontSize=7.2, leading=8.5, textColor=colors.HexColor("#27312B"))
    small = ParagraphStyle("small", parent=body, fontSize=6.3, leading=7.6, textColor=colors.HexColor("#5A665E"))
    label = ParagraphStyle("label", parent=body, fontName="PFBold", fontSize=6.2, leading=7.5, textColor=colors.HexColor("#5A665E"))

    doc = SimpleDocTemplate(str(output), pagesize=A6, rightMargin=8 * mm, leftMargin=8 * mm, topMargin=8 * mm, bottomMargin=8 * mm, title="WINTER 26 - product card proof")
    story: list[Flowable] = []
    for index, product in enumerate(products):
        story.extend([
            Paragraph("WINTER 26  /  PRODUCT CARD PROOF", eyebrow),
            Paragraph(product["name"], title),
            Paragraph("Karta do wysylki - proof ukladu, nie do druku seryjnego", small),
            Spacer(1, 3 * mm),
            Table([
                [Paragraph("MODEL", label), Paragraph(product["name"], body)],
                [Paragraph("SLUG", label), Paragraph(product["id"], body)],
                [Paragraph("KOLOR", label), Paragraph("Do potwierdzenia", body)],
                [Paragraph("MATERIAL", label), Paragraph("Do potwierdzenia", body)],
            ], colWidths=[25 * mm, 55 * mm], style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.35, colors.HexColor("#D5DCD5")),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ])),
            Spacer(1, 3 * mm),
            Paragraph("Uzytkowanie i pielegnacja", label),
            Paragraph("Do uzupelnienia po potwierdzeniu materialu i instrukcji pielegnacji.", body),
            Spacer(1, 2 * mm),
            Paragraph("Producent / bezpieczenstwo", label),
            Paragraph("Do uzupelnienia na podstawie zatwierdzonej karty produktu i danych GPSR.", body),
            Spacer(1, 3 * mm),
            Table([[QRPlaceholder(), Paragraph("QR do zatwierdzonej strony produktu<br/><br/>Identyfikator zamowienia: __________________", body)]], colWidths=[25 * mm, 77 * mm], style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ])),
            Spacer(1, 3 * mm),
            Paragraph("Nie wpisano cen, stanów ani niepotwierdzonych cech. Finalny tekst i QR powstana z tego samego zatwierdzonego zrodla katalogowego co sklep.", small),
        ])
        if index < len(products) - 1:
            story.append(PageBreak())
    doc.build(story)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=Path("data/winter26-products.json"))
    parser.add_argument("--output", type=Path, default=Path("output/pdf/winter26-product-card-proof.pdf"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build(args.output, args.catalog)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
