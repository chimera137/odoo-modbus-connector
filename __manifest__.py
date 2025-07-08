{
    'name': 'Modbus Connector',
    'version': '1.0',
    'category': 'Industrial Automation',
    'summary': 'Connect Modbus devices to Odoo using a REST API',
    'description': """
        This module provides integration with Modbus devices through a REST API.
        Features:
        - Connect to Modbus devices
        - Fetch real-time data
        - Monitor device status
        - Automatic data polling
        - Historical data tracking
    """,
    'author': 'Chimera',
    'website': 'https://petra.ac.id/',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/modbus_device_views.xml',
        'views/modbus_data_views.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}