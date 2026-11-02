<?php
defined('ABSPATH') || exit;
add_action('after_setup_theme', function () {
    add_theme_support('title-tag');
    add_theme_support('woocommerce');
});
add_action('wp_enqueue_scripts', function () {
    wp_enqueue_style('pf-r04-local', get_stylesheet_uri(), array(), '0.1.0');
});
add_action('init', function () {
    remove_action('woocommerce_before_shop_loop_item_title', 'woocommerce_template_loop_product_thumbnail', 10);
    add_action('woocommerce_before_shop_loop_item_title', 'pf_local_placeholder', 10);
    remove_action('woocommerce_before_single_product_summary', 'woocommerce_show_product_images', 20);
    add_action('woocommerce_before_single_product_summary', 'pf_local_placeholder', 20);
});
function pf_local_placeholder() {
    echo '<div class="test-art"><b>01</b><span>NEUTRALNY PLACEHOLDER<br>DANE SYNTETYCZNE</span></div>';
}
