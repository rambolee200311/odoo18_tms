{
    'name': 'Transport Logistics Management',
    'version': '1.0.39',
    'category': 'Transport',
    'summary': '3PL Transport Management System',
    'description': '''
        3PL Transport Module - CMR/ADR/T1 compliance
        Freight transport planning, dispatch, POD, and billing.
    ''',
    'author': 'TLM Team',
    'depends': [
        'base', 'mail', 'stock', 'account',
        'portal', 'contacts', 'product', 'fleet',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/surcharge_data.xml',
        'views/pickup_plan_views.xml',
        'views/transport_request_views.xml',
        'views/transport_inquiry_views.xml',
        'views/transport_quote_views.xml',
        'views/transport_order_views.xml',
        'views/transport_container_views.xml',
        'views/surcharge_views.xml',
        'views/transport_tracking_views.xml',
        'views/pod_views.xml',
        'views/cmr_views.xml',
        'views/customer_bill_views.xml',
        'views/carrier_settlement_views.xml',
        'views/pricing_rule_views.xml',
        'views/portal_customer_templates.xml',
        'views/portal_carrier_templates.xml',
        'reports/report_cmr.xml',
        'reports/report_adr.xml',
        'reports/report_bill.xml',
        'views/container_service_views.xml',
        'views/container_master_views.xml',
        'views/transport_plan_views.xml',
        'views/schedule_calendar_views.xml',
        'views/transport_fee_views.xml',
        'views/tlmp_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
                'wd_tlms/static/src/js/*.js',
                'wd_tlms/static/src/css/*.css',
                'wd_tlms/static/src/xml/*.xml'
            ]
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
