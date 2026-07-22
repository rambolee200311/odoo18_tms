# -*- coding: utf-8 -*-
from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_product_category_ids = fields.Many2many(
        'product.category',
        relation='wd_res_users_product_category_rel',
        column1='user_id',
        column2='category_id',
        string='Allowed Product Categories'
    )