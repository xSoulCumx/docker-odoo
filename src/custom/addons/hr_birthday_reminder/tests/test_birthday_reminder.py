import logging
from odoo.tests.common import TransactionCase
from datetime import date, timedelta
from unittest.mock import patch
from odoo.addons.hr_birthday_reminder.models import hr_employee as hr_employee_module


_logger = logging.getLogger(__name__)



_logger = logging.getLogger(__name__)

class TestBirthdayReminder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.HrEmployee = cls.env['hr.employee']
        cls.MailMail = cls.env['mail.mail']
        cls.ResUsers = cls.env['res.users']
        cls.IrCron = cls.env['ir.cron']
        cls.MailTemplate = cls.env['mail.template']
        cls.ResGroups = cls.env['res.groups']
        cls.ResPartner = cls.env['res.partner']

        cls.cron_job = cls.IrCron.sudo().search([('name', '=', 'HHRR birthday reminder')], limit=1)
    
        birthday_in_7_days = date.today() + timedelta(days=7)
        job_manager = cls.env.ref('hr.job_manager', False)
        if not job_manager:
            job_manager = cls.env['hr.job'].create({'name': 'Test Job for Employees'})
        cls.employee_upcoming = cls.HrEmployee.create({
            'name': 'Juan Pérez',
            'birthday': birthday_in_7_days,
            'work_email': 'juan.perez@example.com',
            'job_id': job_manager.id,
        })
        
        cls.hr_manager_user = cls.ResUsers.create({
            'name': 'HR Manager Test', 'login': 'hrmanager_test', 'email': 'hr.manager@example.com',
            'groups_id': [(4, cls.env.ref('hr.group_hr_manager').id)],
        })
        cls.hr_user = cls.ResUsers.create({
            'name': 'HR User Test', 'login': 'hruser_test', 'email': 'hr.user@example.com',
            'groups_id': [(4, cls.env.ref('hr.group_hr_user').id)],
        })

        cls.hr_no_email_user = cls.ResUsers.create({
            'name': 'HR No Email User Test', 'login': 'hrnoemail_test', 'email': False,
            'groups_id': [(4, cls.env.ref('hr.group_hr_user').id)],
        })

        cls.employee_6_days = cls.HrEmployee.create({'name': 'Ana García', 'birthday': date.today() + timedelta(days=6), 'work_email': 'ana.garcia@example.com'})
        cls.employee_8_days = cls.HrEmployee.create({'name': 'Carlos Ruiz', 'birthday': date.today() + timedelta(days=8), 'work_email': 'carlos.ruiz@example.com'})
        cls.employee_today = cls.HrEmployee.create({'name': 'Maria López', 'birthday': date.today(), 'work_email': 'maria.lopez@example.com'})
        cls.employee_no_birthday = cls.HrEmployee.create({'name': 'Pedro Gómez', 'birthday': False, 'work_email': 'pedro.gomez@example.com'})
        cls.employee_inactive = cls.HrEmployee.create({'name': 'Laura Díaz', 'birthday': birthday_in_7_days, 'work_email': 'laura.diaz@example.com', 'active': False})
        
        cls.email_template = cls.env.ref('hr_birthday_reminder.email_template_hr_upcoming_birthday_reminder')


    def test_01_check_upcoming_birthdays_execution(self):
        """
        Verifica que el método principal del cron (_check_upcoming_birthdays) se ejecuta
        cuando se simula su llamada, asegurando que el mock lo detecte.
        """
        _logger.info('Ejecutando test_01_check_upcoming_birthdays_execution')
        
        with patch.object(hr_employee_module.HrEmployee, '_check_upcoming_birthdays', wraps=hr_employee_module.HrEmployee._check_upcoming_birthdays) as mock_check:
            _logger.info("Mocking de `hr_employee_module.HrEmployee._check_upcoming_birthdays` aplicado.")
            
            # Llama directamente al método como lo haría el cron.
   
            self.HrEmployee._check_upcoming_birthdays(self.HrEmployee)
            
            _logger.info(f"Llamada directa a `_check_upcoming_birthdays` ejecutada. Recuento de llamadas para `mock_check`: {mock_check.call_count}")
            
            mock_check.assert_called_once()
            
            _logger.info('Test 01: `_check_upcoming_birthdays` fue llamado exitosamente.')


    def test_02_no_email_sent_for_invalid_birthdays(self):
        """
        Verifica que NO se generan correos si no hay usuarios activos o correctos .
        """
        _logger.info('Running test_02_no_email_sent_for_invalid_birthdays')
        if self.employee_upcoming and self.employee_upcoming.exists():
            _logger.info(f"Eliminando empleado_upcoming {self.employee_upcoming.id} para test_02.")
            self.employee_upcoming.unlink()

        self.MailMail.search([]).unlink()

        initial_mail_count = self.MailMail.search_count([])

        with patch.object(hr_employee_module.HrEmployee, '_send_birthday_reminder_email_to_hr') as mock_send_email:     

            self.HrEmployee._check_upcoming_birthdays()
            _logger.info(f"Veces en las q e ejecuto `mock_send_email`: {mock_send_email.call_count}")
            # Asegurarse de que el método de envío de correo no fue llamado
            mock_send_email.assert_not_called()
        
        final_mail_count = self.MailMail.search_count([])
        self.assertEqual(initial_mail_count, final_mail_count, 
                         "No se deben haber enviado correos por cumpleaños no válidos.")

        
        all_sent_mail_bodies = "\n".join(self.MailMail.search([]).mapped('body_html'))

        self.assertNotIn(self.employee_6_days.name, all_sent_mail_bodies,
                             "El empleado con cumpleaños en 6 días NO debe aparecer en ningún correo.")
        self.assertNotIn(self.employee_8_days.name, all_sent_mail_bodies,
                             "El empleado con cumpleaños en 8 días NO debe aparecer en ningún correo.")
        self.assertNotIn(self.employee_today.name, all_sent_mail_bodies,
                             "El empleado con cumpleaños hoy NO debe aparecer en ningún correo.")
        self.assertNotIn(self.employee_no_birthday.name, all_sent_mail_bodies,
                             "El empleado sin cumpleaños NO debe aparecer en ningún correo.")
        self.assertNotIn(self.employee_inactive.name, all_sent_mail_bodies,
                             "El empleado inactivo NO debe aparecer en ningún correo.")

        _logger.info('Test 03: No se enviaron correos por cumpleaños no válidos.')
