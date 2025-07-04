import requests
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class ModbusData(models.Model):
    _name = 'modbus.data'
    _description = 'Modbus Historical Data'
    _order = 'timestamp desc'

    device_id = fields.Many2one('modbus.device', string='Device', required=True, ondelete='cascade')
    timestamp = fields.Datetime(string='Timestamp', required=True, default=fields.Datetime.now)
    register_number = fields.Integer(string='Register Number', required=True)
    value = fields.Float(string='Value')
    error = fields.Text(string='Error Message')

    @api.constrains('value')
    def _check_value(self):
        for record in self:
            if record.value is not None and not isinstance(record.value, (int, float)):
                raise ValidationError('Value must be a number')

    # @api.model
    # def fetch_modbus_data(self):
    #     """Fetch data from Modbus API and create records"""
    #     try:
    #         url = 'http://host.docker.internal:3000/data'
    #         response = requests.get(url, timeout=5)
    #         response.raise_for_status()
    #         data = response.json()

    #         return self.create({
    #             'device_id': data.get('device_id'),
    #             'timestamp': data.get('timestamp') or fields.Datetime.now(),
    #             'register_number': data.get('register_number'),
    #             'value': float(data.get('value', 0.0)),
    #             'error': None
    #         })
    #     except Exception as e:
    #         return self.create({
    #             'device_id': 'Error',
    #             'timestamp': fields.Datetime.now(),
    #             'register_number': 0,
    #             'value': 0.0,
    #             'error': str(e)
    #         })

    # @api.model
    # def _cron_fetch_modbus_data(self):
    #     """Scheduled action to fetch data periodically"""
    #     return self.fetch_modbus_data()