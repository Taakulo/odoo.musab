from odoo import models, fields, api, _
from datetime import datetime
import logging
import json
_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = "res.company"

    base_currency_id=fields.Many2one("res.currency",string="Base Currency")