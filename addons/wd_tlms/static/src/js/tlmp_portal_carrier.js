odoo.define('tlmp.portal_carrier', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    var core = require('web.core');

    if (document.getElementById('tlmp_inquiries_page')) {
        rpc.query({
            model: 'tlmp.transport.inquiry',
            method: 'search_read',
            args: [[['partner_id', '=', core.user.partner_id.id]],
                   ['name', 'state', 'total_amount']],
        }).then(function (inquiries) {
            var tbody = document.querySelector('#tlmp_inquiries_table tbody');
            inquiries.forEach(function (i) {
                var tr = document.createElement('tr');
                tr.innerHTML = '<td>'+i.name+'</td><td>'+i.state+'</td>';
                tbody.appendChild(tr);
            });
        });
    }
});