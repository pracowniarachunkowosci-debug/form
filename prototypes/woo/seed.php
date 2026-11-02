<?php
require '/wordpress/wp-load.php';
if (!class_exists('WC_Product_Variable')) { throw new RuntimeException('WooCommerce not loaded'); }
switch_theme('pf-r04-local');
update_option('blogname', 'Pracownia Form — lokalny prototyp');
update_option('blog_public', '0');
update_option('woocommerce_currency', 'PLN');
update_option('woocommerce_default_country', 'PL');
update_option('woocommerce_allow_tracking', 'no');
update_option('woocommerce_onboarding_profile', array('completed' => true));
update_option('woocommerce_task_list_hidden', 'yes');
update_option('woocommerce_coming_soon', 'no'); // Local catalog only; guard blocks sales.
update_option('woocommerce_manage_stock', 'yes');
update_option('woocommerce_hold_stock_minutes', '15');
$shop = wp_insert_post(array('post_type'=>'page','post_status'=>'publish','post_title'=>'Katalog testowy'));
update_option('woocommerce_shop_page_id', $shop);
update_option('show_on_front', 'page');
update_option('page_on_front', $shop);
$product = new WC_Product_Variable();
$product->set_name('TEST — obiekt techniczny');
$product->set_status('publish');
$product->set_sku('PF-TEST-PARENT');
$product->set_description('Jeden syntetyczny produkt do testowania panelu. Nie jest ofertą ani modelem kolekcji. Wariant A: 3 sztuki; wariant B: brak stanu. Cena 1 zł jest wyłącznie testowa.');
$attribute = new WC_Product_Attribute();
$attribute->set_name('Wariant testowy');
$attribute->set_options(array('A', 'B'));
$attribute->set_visible(true);
$attribute->set_variation(true);
$product->set_attributes(array($attribute));
$parent_id = $product->save();
$ids = array();
foreach (array('A'=>3, 'B'=>0) as $label=>$quantity) {
    $variation = new WC_Product_Variation();
    $variation->set_parent_id($parent_id);
    $variation->set_attributes(array('wariant-testowy'=>$label));
    $variation->set_sku('PF-TEST-'.$label);
    $variation->set_regular_price('1.00');
    $variation->set_manage_stock(true);
    $variation->set_stock_quantity($quantity);
    $variation->set_backorders('no');
    $variation->set_stock_status($quantity ? 'instock' : 'outofstock');
    $ids[$label] = $variation->save();
}
WC_Product_Variable::sync($parent_id);
update_option('pf_local_product', array('parent'=>$parent_id, 'variants'=>$ids));
echo wp_json_encode(array('product'=>$parent_id, 'variants'=>$ids, 'wordpress'=>get_bloginfo('version'), 'woocommerce'=>WC_VERSION, 'php'=>PHP_VERSION));
