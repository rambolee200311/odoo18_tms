odoo.define('tlmp.portal_helper', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    return {
        call: function (model, method, args, kwargs) {
            kwargs = kwargs || {};
            return rpc.call({model: model, method: method, args: args, kwargs: kwargs});
        },
        searchRead: function (model, domain, fields) {
            return rpc.call({model: model, method: 'search_read', args: [domain, fields]});
        },
    };
});
