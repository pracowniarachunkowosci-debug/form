<?php
require '/wordpress/wp-load.php';
function pf_assert($condition, $message) { if (!$condition) { throw new RuntimeException($message); } }
$ids = get_option('pf_local_product');
$parent = wc_get_product($ids['parent']);
pf_assert($parent->is_type('variable'), 'Parent must be variable');
pf_assert(count($parent->get_children()) === 2, 'Expected two variations');
$a = wc_get_product($ids['variants']['A']);
$b = wc_get_product($ids['variants']['B']);
pf_assert($a->get_stock_quantity() === 3 && $a->is_in_stock(), 'A initial stock');
pf_assert($b->get_stock_quantity() === 0 && !$b->is_in_stock(), 'B initial stock');
wc_update_product_stock($a, 2, 'set');
wc_delete_product_transients($a->get_id());
$changed = new WC_Product_Variation($a->get_id());
pf_assert($changed->get_stock_quantity() === 2, 'Stock persisted');
wc_update_product_stock($changed, 3, 'set');
pf_assert(!$a->is_purchasable() && !$b->is_purchasable(), 'Purchase guard');
pf_assert(WC()->payment_gateways()->get_available_payment_gateways() === array(), 'No payment gateway');
pf_assert(wp_mail('nobody@example.invalid', 'Test', 'Synthetic') === false, 'Mail blocked');
pf_assert(is_wp_error(wp_remote_get('https://example.invalid')), 'Outbound blocked');
pf_assert((int)get_option('blog_public') === 0, 'No indexing');
pf_assert(count(wc_get_orders(array('limit'=>1))) === 0, 'No orders created');
delete_option('pf_local_probe_done');
$action_id = as_schedule_single_action(time()-1, 'pf_local_probe', array(), 'pf-local');
ActionScheduler::runner()->run();
wp_cache_delete('pf_local_probe_done', 'options');
$queue_passed = get_option('pf_local_probe_done') === 'done';
// Report the actual queue result separately: this SQLite preview is not a
// qualification of host scheduling. Do not hide an unexecuted probe as a pass.
echo wp_json_encode(array('passed'=>true,'product'=>$ids,'stock_write_read_restored'=>true,'orders'=>0,'purchase_blocked'=>true,'mail_blocked'=>true,'outbound_blocked'=>true,'queue_probe'=>array('id'=>$action_id,'executed'=>$queue_passed,'status'=>ActionScheduler::store()->get_status($action_id)),'database'=>'SQLite; not MySQL qualification'));
