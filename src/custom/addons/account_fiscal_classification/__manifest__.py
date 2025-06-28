{
    'name': "Clasificación Fiscal en Facturas",
    'summary':  """
        Añade un campo de selección para la clasificación fiscal (A, B, C) en las facturas.
    """ ,
    'description': """
        Este módulo introduce un campo 'Clasificación Fiscal' en el modelo account.move,
        permitiendo asignar una categoría (A, B, C) a cada factura con un valor por defecto 'A'.
    """,
    'author': "Saul Ortega",
    'category': 'Accounting/Localizations',
    'version': '17.0.1.0.0',
    'depends': ['account'], 
    'data': [
        'views/account_move_views.xml',
    ],
    
    'installable': True,
    'application': False, 
    'license': 'LGPL-3',
}