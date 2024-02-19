from odoo import models, fields, api, _
from datetime import datetime
import logging
import json

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
            for update in order.order_line:
                if update.product_id.standard_price != update.price_unit:
                    update.product_id.sudo().write({"standard_price": update.price_unit,"percentage": update.percentage})
                else:
                    pass
                    
        return True
class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    @api.model
    def _onchange_company_currency(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        for res in self:
            res.base_currency_id=user.company_id.base_currency_id

    @api.onchange('price_unit')
    def _onchange_order_line_product_id(self):
        for res in self:
            if res.product_id:
                res.base_cost_price = res.currency_id._convert(res.price_unit,res.product_id.base_currency_id,res.company_id,res.date_order,round=True)
                res.percentage=res.product_id.percentage
    base_cost_price = fields.Float(string="Base Cost Price",compute="_onchange_order_line_product_id")
    percentage = fields.Float(string="Percentage",compute="_onchange_order_line_product_id",store=True)
    base_currency_id = fields.Many2one(
        "res.currency",
        compute="_onchange_company_currency",
        help="The base currency for the company"
    )