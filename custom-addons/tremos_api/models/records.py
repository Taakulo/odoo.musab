# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import json
import requests
from odoo import fields, models,api
import random
import string

_logger = logging.getLogger(__name__)
generated_codes = set()

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    @api.model
    def create(self, vals):
        vals.update({
            'sequencing': self.env['ir.sequence'].next_by_code('product.template')
        })
        result = super(ProductTemplate, self).create(vals)
        return result
    sequencing=fields.Char(string='Sequencing',readonly=True)
    def update_products_code(self):
        query = """
            UPDATE product_template
            SET sequencing = subquery.seq
            FROM (
                SELECT id, ROW_NUMBER() OVER () AS seq
                FROM product_template
            ) AS subquery
            WHERE product_template.id = subquery.id;
            """
        self.env.cr.execute(query)
    def update_product_data(self):
        payload = json.dumps({
            "name": "import_data",
        })
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", "http://164.92.100.42:8069/product/data", headers=headers, data=payload)
        _logger.error(response.text)
        response_data = json.loads(response.text)
        for tremos in response_data['result']:
            filtered_data = {
                "name": tremos['name'],
                "list_price": tremos['list_price'],
                "standard_price": tremos['standard_price'],
                "sequencing": tremos['sequencing'],
                "image_1920": tremos['image'],
                "detailed_type": tremos['detailed_type'],
                "percentage": tremos['percentage'],
            }
            # Check and create/update UOM
            unit_of_measure = self.env['uom.uom'].sudo().search([('name', '=', tremos['uom_id'])], limit=1)
            if not unit_of_measure:
                unit_of_measure = self.env['uom.uom'].sudo().create({'name': tremos['uom_id']})
            filtered_data['uom_id'] = unit_of_measure.id

            unit_of_po_measure = self.env['uom.uom'].sudo().search([('name', '=', tremos['uom_po_id'])], limit=1)
            if not unit_of_po_measure:
                unit_of_po_measure = self.env['uom.uom'].sudo().create({'name': tremos['uom_po_id']})
            filtered_data['uom_po_id'] = unit_of_po_measure.id

            # Check and create/update category
            category_name = self.env['product.category'].sudo().search([('name', '=', tremos['categoryName'])], limit=1)
            if not category_name:
                category_name = self.env['product.category'].sudo().create({'name': tremos['categoryName']})
            filtered_data['categ_id'] = category_name.id

            # Check and create/update product
            product_template = self.env['product.template'].sudo().search([('sequencing', '=', tremos['sequencing'])])
            if product_template:
                product_template.write(filtered_data)
            else:
                self.env['product.template'].sudo().create(filtered_data)