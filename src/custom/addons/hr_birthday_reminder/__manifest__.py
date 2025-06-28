# hr_birthday_reminder/__manifest__.py
{
    'name': "Recordatorio de Cumpleaños RRHH",
    'summary': """
        Modulo para envíar recordatorios automáticos de cumpleaños de los empleados 7 días antes al departamento de RRHH.
    """,
    'description': """
        Este módulo automatiza el envío de recordatorios por correo electrónico
        a los encargados de recursos humanos.
        - Configura una acción planificada (cron) para ejecutarse diariamente.
        - Identifica a los empleados con cumpleaños en los próximos 7 días.
        - Envía un correo electrónico de recordatorio.
        - Incluye una prueba unitaria para validar la funcionalidad.
    """,
    'category': 'Human Resources',
    'version': '17.0.1.0.0',
    'depends': ['hr', 'mail'], 
    'data': [
        'data/email_template_reminder.xml',
        'data/ir_cron_data.xml', 
        
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}