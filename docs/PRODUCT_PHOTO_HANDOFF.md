# WINTER 26 — przyjęcie rzeczywistych fotografii

Status po korekcie priorytetu 03.11.2026: **tymczasowy hero z otwartą bombką już działa**. Wycięto samą scenę z dostarczonego screenshotu i oznaczono ją jako wizualizację koncepcyjną AI. [Porównanie przed/po, źródło i eksporty](HERO_CONCEPT_PREVIEW.md). Na rzeczywiste zdjęcia oczekuje wyłącznie kolejny etap finalnej fotografii, nie lokalny preview. Nie generowano nowej geometrii.

Decyzja: otwarta rzeźbiarska bombka z szerokich przecinających się wstęg, jasna matowa lekko nakrapiana powierzchnia i rzeczywista istniejąca ozdobna zawieszka. Nie zamknięta spirala, nie relief swetra. Nie przypisujemy jej automatycznie do modelu HELIX ani konkretnego SKU bez potwierdzenia właściciela.

Zachowane: treść poza podpisem/alt hero, CTA, nagłówek, nawigacja, paleta R04 i cztery neutralne placeholdery. Aktualny podpis: „Wizualizacja koncepcyjna AI na podstawie modelu Pracowni Form. Fotografia produktu w przygotowaniu.” Nie przedstawia obrazu jako rzeczywistej fotografii.

Po otrzymaniu zdjęć:

1. Obejrzeć oryginały, ustalić model/ujęcie i prawa do użycia; wybrać ostre zdjęcie pokazujące przecinające się wstęgi, otwory i zawieszkę. Zachować oryginał; nie zgadywać niewidocznych fragmentów.
2. Wyrównać ekspozycję i balans bieli, wykonać naturalny retusz tła/zabrudzeń bez zmiany geometrii, materiału, faktury, koloru i elementów zawieszki. Niedostateczna jakość źródła oznacza prośbę o kolejne ujęcie, nie domyślanie detali.
3. Przygotować osobną propozycję kompozycji: ciemne kamienne podłoże, gałązki, burgundowa wstążka, światło zgodne ze zdjęciem. Jeśli tło jest generowane, jawnie podpisać kompozycję z rzeczywistą fotografią produktu i przygotowanym tłem; nie nazywać jej dokumentalną fotografią całej sceny.
4. Pokazać obok oryginału podglądy desktop/mobile, sprawdzić krawędzie, prześwity, zawieszkę, skalę i cień; uzyskać akceptację konkretnego pliku przed użyciem.
5. Przygotować AVIF/WebP 480/768/1024/1536 (tylko rozdzielczości uzasadnione źródłem), WebP fallback, `srcset`/`sizes`, stałe wymiary i wysoki priorytet hero. Unikać upscalingu. Cel <150 KB/wariant sprawdzić przy zachowaniu faktury i otworów. Social 1200×800 lub adekwatny zatwierdzony kadr.
6. Dopiero po akceptacji podmienić `picture`, alt, podpis i OG/Twitter oraz zaktualizować test zamrożonego hero. Zapisać mapowanie źródło→wersja→eksporty i hashe. Nie zmieniać typografii, układu, CTA ani nawigacji.

Karty mają cztery istniejące miejsca: `#knitted-star`, `#knitted-medallion`, `#helix`, `#full-soft`. Właściciel mapuje zdjęcie na model; brak zdjęcia pozostaje jawnym placeholderem. Dla każdej karty przygotować opis alternatywny opisujący widoczny realny model, wymiary obrazu i lazy loading. Nie dopisywać cech, cen, wariantów ani stanów na podstawie ilustracji.
