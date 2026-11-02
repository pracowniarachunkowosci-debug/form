<?php
/** Plugin Name: PF Local Prototype Guard — never deploy */
defined('ABSPATH') || exit;
if (wp_get_environment_type() !== 'local') {
    wp_die('Ten prototyp jest przeznaczony wyłącznie dla lokalnego środowiska.', '', array('response' => 503));
}
add_filter('pre_option_blog_public', '__return_zero');
// The runner can use a separate PHP request: register the probe in every worker.
add_action('pf_local_probe', function () { update_option('pf_local_probe_done', 'done'); });
add_filter('pre_wp_mail', '__return_false');
add_filter('woocommerce_available_payment_gateways', '__return_empty_array', PHP_INT_MAX);
add_filter('woocommerce_is_purchasable', '__return_false', PHP_INT_MAX);
add_filter('woocommerce_variation_is_purchasable', '__return_false', PHP_INT_MAX);
add_filter('woocommerce_add_to_cart_validation', '__return_false', PHP_INT_MAX);
add_filter('pre_http_request', function () {
    return new WP_Error('pf_local_offline', 'Zewnętrzne żądania HTTP są wyłączone w prototypie.');
}, PHP_INT_MAX);
add_filter('rest_pre_dispatch', function ($result, $server, $request) {
    if (preg_match('#^/wc/store/[^/]+/(checkout|cart)#', $request->get_route())) {
        return new WP_Error('pf_local_no_checkout', 'Sprzedaż jest wyłączona.', array('status' => 403));
    }
    return $result;
}, PHP_INT_MAX, 3);
add_action('template_redirect', function () {
    if (function_exists('is_checkout') && (is_checkout() || is_cart())) {
        wp_die('Sprzedaż jest wyłączona w lokalnym prototypie.', '', array('response' => 403));
    }
});
add_action('send_headers', function () { header('X-Robots-Tag: noindex, nofollow'); });
add_action('admin_notices', function () {
    echo '<div class="notice notice-warning"><p>PF LOCAL — tylko dane syntetyczne. Brak sprzedaży, płatności, wysyłki i e-maili. SQLite nie potwierdza działania produkcyjnego MySQL.</p></div>';
});
