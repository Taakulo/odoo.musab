from odoo import models, fields, api, _
from datetime import datetime
import logging
from odoo.exceptions import UserError
import json

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'
    @api.depends('currency_id', 'invoice_date','invoice_line_ids')
    def _compute_active_rate(self):
        for res in self:
            if res.company_id.base_currency_id and res.invoice_date and res.currency_id:
                if res.currency_id != res.company_id.base_currency_id:
                    tax_data = json.loads(res.tax_totals_json)
                    rate = res.currency_id._get_conversion_rate(res.currency_id, res.company_id.base_currency_id, res.company_id, res.invoice_date)
                    amount=res.currency_id._convert(tax_data.get('amount_total'), res.company_id.base_currency_id, res.company_id, res.invoice_date,round=True)
                    res.current_rate = rate
                    res.base_amount=amount
                else:
                    res.current_rate = 1.0
                    res.base_amount=res.amount_total_signed
            else:
                pass
    current_rate = fields.Integer(string='Active Rate', compute='_compute_active_rate', store=True, readonly=True)
    base_amount = fields.Integer(string='Base Amount', compute='_compute_active_rate', store=True, readonly=True,currency_field="company_currency_id")
    company_currency_id=fields.Many2one('res.currency',related="company_id.base_currency_id",readonly=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    percentage = fields.Integer(string="Percentage (%)",store=True,compute="_onchange_values")
    cost_price_base = fields.Integer(string="Base Cost Price",compute="_onchange_values")
    cost_price_company = fields.Integer(string="Company Cost Price", related="product_id.standard_price")
    profit_amt_base = fields.Integer(string="Base Profit Amount", store=True, readonly=True,compute="_onchange_values")
    profit_amt_company = fields.Integer(string="Company Profit Amount", store=True, readonly=True,compute="_onchange_values")
    price_unit_base = fields.Integer(string="Base Price Amount",compute="_onchange_values")



    @api.onchange("price_unit", "price_unit_base", "percentage")
    def _onchange_values(self):
        for res in self:
            if res.currency_id != res.company_id.base_currency_id:
                    res.percentage = ((res.price_unit - res.cost_price_company) / res.cost_price_company) * 100 if res.cost_price_company !=0 else 1
                    res.cost_price_base = res.currency_id._convert(res.product_id.standard_price, res.company_id.base_currency_id, res.company_id, res.move_id.invoice_date, round=True)
                    res.cost_price_company = res.product_id.standard_price
                    res.profit_amt_base = res.currency_id._convert((res.price_unit - res.cost_price_company), res.company_id.base_currency_id, res.company_id, res.move_id.invoice_date, round=True)
                    res.profit_amt_company = res.price_unit - res.cost_price_company
                    res.price_unit_base = res.currency_id._convert(res.price_unit, res.company_id.base_currency_id, res.company_id, res.move_id.invoice_date, round=True)
                    res.price_unit = res.company_id.base_currency_id._convert(res.price_unit_base, res.currency_id, res.company_id, res.move_id.invoice_date, round=True)