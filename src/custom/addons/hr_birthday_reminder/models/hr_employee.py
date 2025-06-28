from odoo import fields, models, api, _
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _check_upcoming_birthdays(self):

        today = date.today()
        
        target_birthday_date = today + timedelta(days=7)


        target_month = target_birthday_date.month
        target_day = target_birthday_date.day
        birthday_pattern = f'%-{target_month:02d}-{target_day:02d}'

        domain = [
            ('active', '=', True),
            ('birthday', '!=', False),
            ('birthday', 'like', birthday_pattern)
        ]

        employees_for_reminder = self.search(domain)

        if employees_for_reminder:
            _logger.info(f"Se encontraron {len(employees_for_reminder)} empleados con cumpleaños exactamente en 7 días.")
            
            actual_upcoming_employees = self.env['hr.employee']
            for employee in employees_for_reminder:
                employee_birthday_date = employee.birthday
                
                birthday_this_year = employee_birthday_date.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = employee_birthday_date.replace(year=today.year + 1)
                
                delta = birthday_this_year - today
                
                if delta == timedelta(days=7):
                    actual_upcoming_employees += employee
            
            if actual_upcoming_employees:
                self._send_birthday_reminder_email_to_hr(actual_upcoming_employees)
            else:
                _logger.info("Nada para notificar luego de validar")

        else:
            _logger.info("Ningun cumpleaños encontrado")

        return True

    def _send_birthday_reminder_email_to_hr(self, employees):
       
        _logger.info(f"Preparando envío de recordatorio a RRHH para {len(employees)} empleado(s) con cumpleaños en 7 días.")

        hr_user_group = self.env.ref('hr.group_hr_user', raise_if_not_found=False)
        hr_manager_group = self.env.ref('hr.group_hr_manager', raise_if_not_found=False)

        if not hr_user_group and not hr_manager_group:
            _logger.error("Ninguno de los grupos de RRHH (group_hr_user, group_hr_manager) fue encontrado. No se pudo enviar el recordatorio.")
            return

        hr_users = self.env['res.users']
        if hr_user_group:
            hr_users |= hr_user_group.users
        if hr_manager_group:
            hr_users |= hr_manager_group.users

        # Filtra usuarios activos y con email de partner_id
        hr_users = hr_users.filtered(lambda u: u.partner_id and u.partner_id.email and u.active)

        if not hr_users:
            _logger.warning("No se encontraron usuarios de RRHH activos con correo electrónico en los grupos especificados. No se pudo enviar el recordatorio.")
            return
        
        hr_partner_ids = hr_users.mapped('partner_id').ids
        if not hr_partner_ids:
            _logger.warning("No se pudieron recopilar partners de los usuarios de RRHH. No se pudo enviar el recordatorio.")
            return

        template = self.env.ref('hr_birthday_reminder.email_template_hr_upcoming_birthday_reminder', raise_if_not_found=False)

        if not template:
            _logger.error("Plantilla de correo 'email_template_hr_upcoming_birthday_reminder' no encontrada. No se pudo enviar el recordatorio a RRHH.")
            return

        today = date.today()
        
        rendering_context = {
            'employees': employees, 
            'today_date': today.strftime('%d/%m/%Y'),
            'user': self.env.user,
            'object': self.env['hr.employee'],
            'company_id': self.env.user.company_id.id,
        }

        try:
            template.with_context(**rendering_context).send_mail(
                res_id=0, 
                force_send=True,
                email_values={
                    'recipient_ids': [(6, 0, hr_partner_ids)],
                    'email_from': self.env.user.company_id.email_formatted or self.env.user.email_formatted,
                },
                
            )

            _logger.info(f"Recordatorio de cumpleaños enviado a RRHH a los partners {hr_partner_ids} para {len(employees)} empleado(s).")

        except Exception as e:
            _logger.error(f"Error al enviar el recordatorio de cumpleaños a RRHH: {e}")