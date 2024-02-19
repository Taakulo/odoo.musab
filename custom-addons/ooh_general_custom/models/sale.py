from odoo import models, fields, api, _
from datetime import datetime
import logging
from odoo.exceptions import UserError
import json

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('order_line.product_id')
    def _change_values(self):
        for order in self:
            for line in order.order_line:
                if line.product_id.percentage is not None:  # Check if percentage is not None
                    line.percentage = line.product_id.percentage
                    line.price_unit = (1 + line.percentage / 100) * line.product_id.standard_price
                else:
                    line.percentage = 0.0
                    line.price_unit = line.product_id.standard_price

    @api.depends('currency_id','date_order','order_line')
    def _compute_active_rate(self):
        for res in self:
            if res.company_id.base_currency_id and res.date_order and res.currency_id:
                tax_data = json.loads(res.tax_totals_json)
                if res.currency_id != res.company_id.base_currency_id:
                    rate = res.currency_id._get_conversion_rate(res.currency_id, res.company_id.base_currency_id, res.company_id, res.date_order)
                    amount=res.currency_id._convert(tax_data.get('amount_total'), res.company_id.base_currency_id, res.company_id, res.date_order,round=True)
                    res.current_rate = rate
                    res.base_amount=amount
                else:
                    res.current_rate = 1.0
                    res.base_amount=tax_data.get('amount_total')
            else:
                pass
    

    current_rate = fields.Float(string='Active Rate', compute='_compute_active_rate', store=True, readonly=True)
    base_amount = fields.Float(string='Base Amount', compute='_compute_active_rate', store=True, readonly=True)
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange("price_unit_base")
    def _onchange_price_unit_base(self):
        for line in self:
            if line.product_id and line.order_id.company_id.currency_id != line.order_id.company_id.base_currency_id:
                line.price_unit = line.order_id.company_id.base_currency_id._convert(line.price_unit_base,line.order_id.company_id.currency_id,line.order_id.company_id,line.order_id.date_order,round=True)
            else:
                pass

    @api.onchange("price_unit")
    def _onchange_price_unit(self):
        for line in self:
            if line.order_id.company_id.currency_id != line.order_id.company_id.base_currency_id and line.product_id:
                line.price_unit_base = line.order_id.company_id.currency_id._convert(line.price_unit,line.order_id.company_id.base_currency_id,line.order_id.company_id,line.order_id.date_order,round=True)
            else:
                line.price_unit_base = line.price_unit
    @api.depends("cost_price_company")
    def _compute_cost_price_base(self):
        for line in self:
            if line.product_id and line.cost_price_company:
                line.cost_price_base = line.order_id.company_id.currency_id._convert(line.cost_price_company,line.order_id.company_id.base_currency_id,line.order_id.company_id,line.order_id.date_order,round=True)
            else:
                line.cost_price_base = 0.0

    @api.depends("cost_price_company","price_unit")
    def _get_percentage(self):
        for line in self:
            if line.product_id:
                line.percentage = ((line.price_unit-line.cost_price_company)/line.cost_price_company)*100
            else:
                line.percentage = 0.0

    @api.depends("cost_price_company","price_unit","cost_price_base","price_unit_base")
    def _calculate_profit(self):
        for line in self:
            if line.product_id and line.price_unit_base and line.price_unit:
               line.profit_amt_base = line.price_unit_base-line.cost_price_base
               line.profit_amt_company = line.price_unit-line.cost_price_company
            else:
                line.profit_amt_base = 0.0
                line.profit_amt_company = 0.0
    percentage = fields.Float(string="%",store=True,readonly=True,compute="_get_percentage")
    cost_price_base = fields.Float(string="Base Cost Price",readonly=True,compute="_compute_cost_price_base")
    cost_price_company = fields.Float(string="Company Cost Price",related="product_id.standard_price",readonly=True,)
    profit_amt_base = fields.Float(string="Base Profit Amount",store=True, readonly=True,compute='_calculate_profit')
    profit_amt_company = fields.Float(string="Company Profit Amount", store=True, readonly=True,compute='_calculate_profit')
    price_unit_base = fields.Float('Base Unit Price', required=True, digits='Product Price',readonly=False)
    price_unit = fields.Float('Unit Price', required=True,store=True, digits='Product Price',readonly=True)


