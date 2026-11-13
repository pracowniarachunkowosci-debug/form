# Issue #27 — proof karty produktu

Skrypt `scripts/render_product_card_proof.py` generuje trzy strony A6 z aktualnego `data/winter26-products.json`: VASE, KNITTED STAR i KNITTED MEDALLION.

Proof celowo nie jest kartą produkcyjną. Pola koloru, materiału, pielęgnacji, danych producenta/GPSR i QR są jawnie oznaczone do uzupełnienia. Dzięki temu karta nie utrwala danych, których pakiet fotograficzny jeszcze nie potwierdza.

Po akceptacji mapowania zdjęć i danych handlowo-prawnych należy wygenerować finalne karty z tego samego źródła katalogowego co sklep i osobno zatwierdzić PDF przed drukiem.
