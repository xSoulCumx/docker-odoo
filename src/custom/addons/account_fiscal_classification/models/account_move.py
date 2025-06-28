from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    fiscal_classification = fields.Selection(
        [('A', 'A'),
         ('B', 'B'),
         ('C', 'C')],
        string='Clasificacion Fiscal',
        default='A',
        required=True,
        help="Clasificación fiscal para propósitos específicos de la factura."
    )