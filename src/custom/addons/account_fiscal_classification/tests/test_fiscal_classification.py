from odoo.tests.common import TransactionCase
from datetime import datetime

class TestFiscalClassification(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.AccountMove = cls.env['account.move']
        cls.AccountJournal = cls.env['account.journal']
        cls.ResPartner = cls.env['res.partner']

        # Buscar-crear diario de ventas
        cls.sales_journal = cls.AccountJournal.search([('type', '=', 'sale')], limit=1)
        if not cls.sales_journal:
            cls.sales_journal = cls.AccountJournal.create({
                'name': 'Diario de Ventas de Prueba',
                'type': 'sale',
                'code': 'TVENTAS',
                'company_id': cls.env.company.id,
            })

        # Crear cliente de prueba
        cls.partner = cls.ResPartner.create({
            'name': 'Cliente de Prueba',
            'type': 'contact',
            'email': 'test_client@example.com',
        })

    def test_01_default_fiscal_classification_on_invoice_creation(self):
        """
        verificar 'fiscal_classification' tiene el valor por defecto 'A'
        al crear una nueva factura.
        """
        # Crear una nueva factura
        invoice = self.AccountMove.create({
            'partner_id': self.partner.id,
            'move_type': 'out_invoice', # Factura de cliente
            'journal_id': self.sales_journal.id,
            'invoice_date': datetime.now().date(),
        })

        # Verificar el valor por defecto
        self.assertEqual(invoice.fiscal_classification, 'A',
                         "El campo 'fiscal_classification' no tiene el valor por defecto 'A' al crear la factura.")

        # Verificar que se puede cambiar el valor
        invoice.write({'fiscal_classification': 'B'})
        self.assertEqual(invoice.fiscal_classification, 'B',
                         "No se pudo cambiar el valor de 'fiscal_classification'.")

        invoice.write({'fiscal_classification': 'C'})
        self.assertEqual(invoice.fiscal_classification, 'C',
                         "No se pudo cambiar el valor de 'fiscal_classification'.")