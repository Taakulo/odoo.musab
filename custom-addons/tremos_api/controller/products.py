from odoo import http
from odoo.http import request, Response
from odoo.tools import float_is_zero, float_compare
import json
import logging
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)


class ProductController(http.Controller):
    @http.route('/product/data', auth='public', type='json', csrf=False, method=['POST'])
    def getProductsData(self, **kw):
        product_data = []
        [product_data.append({
            "name": tremos.name,
            "list_price": tremos.list_price,
            "standard_price": tremos.standard_price,
            "sequencing": tremos.sequencing,
            "image": tremos.image_1920,
            "uom_id": tremos.uom_id.name,
            "uom_po_id": tremos.uom_po_id.name,
            "detailed_type": tremos.detailed_type,
            "percentage": tremos.percentage,
            "categoryName":tremos.categ_id.name
        }) for tremos in
            request.env['product.template'].sudo().search(['|', ('active', '=', True), ('active', '=', False)])]
        return product_data
