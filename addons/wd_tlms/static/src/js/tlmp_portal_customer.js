odoo.define('tlmp.portal_customer', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    var core = require('web.core');

    // 数据通过 ORM call 直接加载，不需要 Controller
    if (document.getElementById('tlmp_orders_page')) {
        rpc.query({
            model: 'tlmp.transport.order',
            method: 'search_read',
            args: [[['partner_id', 'child_of', core.user.partner_id.id]],
                   ['name', 'state', 'carrier_id', 'planned_pickup_date']],
        }).then(function (orders) {
            var tbody = document.querySelector('#tlmp_orders_table tbody');
            orders.forEach(function (o) {
                var tr = document.createElement('tr');
                tr.innerHTML = '<td>'+o.name+'</td><td>'+o.state+'</td>';
                tbody.appendChild(tr);
            });
        });
    }

    if (document.getElementById('tlmp_order_detail_page')) {
        var orderId = document.getElementById('tlmp_order_detail_page').dataset.orderId;
        rpc.query({model: 'tlmp.transport.order', method: 'read', args: [[orderId]]})
            .then(function (orders) {
                if (orders.length) {
                    var o = orders[0];
                    document.getElementById('tlmp_order_name').textContent = o.name;
                    document.getElementById('tlmp_order_state').textContent = o.state;
                }
            });
    }

    // 报价确认
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('tlmp_btn_accept_quote')) {
            var quoteId = e.target.dataset.quoteId;
            rpc.query({model: 'tlmp.transport.quote', method: 'action_accept_from_portal', args: [[quoteId]]})
                .then(function () { location.reload(); })
                .catch(function (err) { alert(err.message); });
        }
        if (e.target.classList.contains('tlmp_btn_confirm_pod')) {
            var podId = e.target.dataset.podId;
            rpc.query({model: 'tlmp.pod', method: 'action_confirm', args: [[podId]]})
                .then(function () { location.reload(); });
        }
    });

    document.addEventListener('change', function (e) {
        if (e.target.id === 'tlmp_transport_type') {
            var type = e.target.value;
            document.querySelectorAll('.tlmp_dg_field').forEach(function (el) {
                el.style.display = (type === 'port_to_warehouse' || type === 'to_customer') ? '' : 'none';
            });
        }
    });
});