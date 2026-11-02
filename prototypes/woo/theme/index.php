<?php defined('ABSPATH') || exit; ?>
<!doctype html><html <?php language_attributes(); ?>><head><meta charset="<?php bloginfo('charset'); ?>"><meta name="viewport" content="width=device-width, initial-scale=1"><?php wp_head(); ?></head>
<body <?php body_class(); ?>><?php wp_body_open(); ?>
<a class="skip" href="#content">Przejdź do treści</a>
<header class="site-header"><div class="shell header-row"><a class="brand" href="<?php echo esc_url(home_url('/')); ?>"><span>PF</span>PRACOWNIA FORM</a><small>WINTER AFTER DARK · R04</small></div></header>
<section class="opening"><div class="shell"><div class="eyebrow">Studium sklepu · bez sprzedaży</div><h1>WINTER<br><em>26.</em></h1><p>Lokalny prototyp katalogu. Sprawdzamy warianty i magazyn w WooCommerce. Produkt, nazwy wariantów i cena są wyłącznie danymi testowymi.</p></div></section>
<aside class="notice"><div class="shell">PROTOTYP LOKALNY — płatności, wysyłka i wiadomości e-mail wyłączone.</div></aside>
<main id="content" class="shell catalog woocommerce">
<?php if (function_exists('woocommerce_content')) { woocommerce_content(); } else { echo '<p>WooCommerce nieaktywne.</p>'; } ?>
</main><footer class="site-footer"><div class="shell">Pracownia Form · koncepcja sklepu do przeglądu. Zatwierdzona strona pozostaje bez zmian.</div></footer>
<?php wp_footer(); ?></body></html>
