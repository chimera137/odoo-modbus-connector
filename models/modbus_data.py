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