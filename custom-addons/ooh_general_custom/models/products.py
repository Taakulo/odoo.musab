from odoo import models, fields, api, _
from datetime import datetime
import logging
import json
from datetime import date

_logger = logging.getLogger(__name__)
class Product(models.Model):
    _inherit = "product.product"
    @api.model
    def _onchange_company_currency(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        for res in self:
            res.base_currency_id=user.company_id.base_currency_id

    base_currency_id = fields.Many2one(
        "res.currency",compute="_onchange_company_currency",
        help="The base currency for the company"
    )

class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def _compute_date(self):
        for record in self:
            record.date = date.today()

    @api.depends('standard_price','date')
    def _onchange_standard_price(self):
        for product in self:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
            if user.company_id.currency_id != product.base_currency_id and product.standard_price > 0:
                product.cost_price_base_currency = user.company_id.currency_id._convert(
                    product.standard_price,
                    product.base_currency_id,
                    user.company_id,
                    product.date,
                    round=True,
                )
                product.percentage = (
                    (product.list_price - product.standard_price)
                    / product.standard_price
                ) * 100
            elif product.standard_price:
                product.cost_price_base_currency = product.list_price
                product.percentage = (
                                (product.list_price - product.standard_price)
                                / product.standard_price
                            ) * 100
    @api.depends('list_price','date')
    def _onchange_list_price(self):
        for product in self:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid)
            if user.company_id.currency_id != product.base_currency_id and product.cost_price_base_currency:
                product.selling_price_base_currency = user.company_id.currency_id._convert(
                    product.list_price,
                    product.base_currency_id,
                    user.company_id,
                    product.date,
                    round=True,
                )
                product.percentage = (
                    (product.selling_price_base_currency - product.cost_price_base_currency)
                    / product.cost_price_base_currency
                ) * 100
            elif product.standard_price:
                product.selling_price_base_currency = product.list_price

                product.percentage = (
                                (product.list_price - product.standard_price)
                                / product.standard_price
                            ) * 100
    @api.onchange('list_price','standard_price')
    def _check_if_less(self):
        for res in self:
            if res.list_price<res.standard_price:
                res.is_less = True
            else:
                res.is_less = False
    cost_price_base_currency = fields.Float(
        string="Base cost price",
        readonly=True,
        compute="_onchange_standard_price",
        help="Price at which the product is sold to customers in base currency.",
        tracking=True,
        store=True,
    )
    message=fields.Text(default="THE SELLING PRICE IS LESS THAN THE COST PRICE",readonly=True)
    selling_price_base_currency = fields.Float(
        string="Base selling price",
        readonly=True,
        compute="_onchange_list_price",
        help="Price at which the product is sold to customers in base currency.",
        tracking=True,
        store=True,
    )
    percentage = fields.Float(
        string="Percentage", store=True, tracking=True,
        help="Percentage profit for the product",
        required=True
    )
    is_less = fields.Boolean(string="Is Less", compute="_check_if_less",)
    base_currency_id = fields.Many2one(
        "res.currency",compute="_onchange_company_currency",
        help="The base currency for the company"
    )
    date = fields.Datetime(string="Date",compute="_compute_date",readonly=True,default=date.today())
    list_price = fields.Float(
        "Sales Price",
        default=1.0,
        digits="Product Price",
        help="Price at which the product is sold to customers.",
        compute="_onchange_the_standard_price_or_percentage",readonly=False
    )
    @api.model
    def _onchange_company_currency(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        for res in self:
            res.base_currency_id=user.company_id.base_currency_id
    @api.onchange("percentage","standard_price")
    def _onchange_the_standard_price_or_percentage(self):
        for product in self:
            product.list_price = (
                1 + (product.percentage / 100)
            ) * product.standard_price
