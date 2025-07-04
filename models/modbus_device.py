from odoo import models, fields, api
import requests
from datetime import datetime
import logging
import threading
import time
import odoo

_logger = logging.getLogger(__name__)

class ModbusDevice(models.Model):
    _name = 'modbus.device'
    _description = 'Modbus Device'

    name = fields.Char(string='Device Name', required=True)
    plc_ip = fields.Char(string='PLC IP Address', required=True, default='127.0.0.1')
    plc_port = fields.Integer(string='PLC Port', required=True, default=502)
    slave_id = fields.Integer(string='Slave ID', required=True, default=1)
    polling_interval = fields.Integer(string='Polling Interval (ms)', required=True, default=1000)
    starting_register = fields.Integer(string='Starting Register', required=True, default=0)
    number_of_registers = fields.Integer(string='Number of Registers', required=True, default=1)
    api_port = fields.Integer(string='API Port', required=True, default=3001)
    is_polling = fields.Boolean(string='Is Polling', default=False, readonly=True)
    
    api_url = fields.Char(string='API URL', compute='_compute_api_url', store=True)
    status = fields.Selection([
        ('disconnected', 'Disconnected'),
        ('connected', 'Connected'),
        ('error', 'Error'),
        ('polling', 'Polling')
    ], string='Status', default='disconnected', readonly=True)
    last_values = fields.Text(string='Last Values', readonly=True)
    last_error = fields.Text(string='Last Error', readonly=True)
    data_ids = fields.One2many('modbus.data', 'device_id', string='Historical Data')
    data_count = fields.Integer(compute='_compute_data_count', string='Data Count')

    @api.depends('api_port')
    def _compute_api_url(self):
        for record in self:
            record.api_url = f'http://host.docker.internal:{record.api_port}'

    @api.depends('data_ids')
    def _compute_data_count(self):
        for record in self:
            record.data_count = len(record.data_ids)

    def test_connection(self):
        self.ensure_one()
        try:
            _logger.info(f"Testing connection for device {self.name} at {self.api_url}/data")
            # Send device configuration in the request body
            config_data = {
                'ip': self.plc_ip,
                'port': self.plc_port,
                'slaveId': self.slave_id,
                'startingRegister': self.starting_register,
                'numberOfRegisters': self.number_of_registers
            }
            
            # Use the /data endpoint with POST method
            response = requests.post(f"{self.api_url}/data", json=config_data, timeout=10) # Increased timeout for connection test
            response.raise_for_status()
            data = response.json()
            
            # Update device status based on the response from the API
            self.status = data.get('connectionStatus', 'error')
            
            if data.get('error'):
                error_msg = f"Connection test failed: {data.get('error')}"
                self.last_error = error_msg
                _logger.error(error_msg)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Test Failed',
                        'message': error_msg,
                        'type': 'danger',
                        'sticky': True,
                    }
                }
            else:
                success_msg = f"Successfully connected to Modbus device {self.name} at {self.plc_ip}:{self.plc_port}"
                self.last_error = False
                # If polling, keep status as 'polling', else set to 'connected'
                if self.is_polling:
                    self.status = 'polling'
                else:
                    self.status = 'connected'
                _logger.info(success_msg)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Test Successful', # Changed title
                        'message': success_msg,
                        'type': 'success',
                        'sticky': False,
                    }
                }
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Could not connect to Modbus API at {self.api_url}. Please ensure the API server is running and accessible." # More specific error
            self.status = 'error'
            self.last_error = error_msg
            _logger.error(error_msg)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Error', # Changed title
                    'message': error_msg,
                    'type': 'danger',
                    'sticky': True,
                }
            }
        except Exception as e:
            error_msg = f"Error testing connection for device {self.name}: {str(e)}"
            self.status = 'error'
            self.last_error = error_msg
            _logger.error(error_msg)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Test Error', # Changed title
                    'message': error_msg,
                    'type': 'danger',
                    'sticky': True, # Changed to sticky
                }
            }

    def fetch_data(self):

        start_time = time.time() #for measuring the time it takes to fetch data

        self.ensure_one()
        try:
            _logger.info(f"Fetching data from device {self.name} at {self.api_url}/data")
            
            # Send device configuration in the request body
            config_data = {
                'ip': self.plc_ip,
                'port': self.plc_port,
                'slaveId': self.slave_id,
                'startingRegister': self.starting_register,
                'numberOfRegisters': self.number_of_registers
            }
            
            # Use the /data endpoint with POST method
            response = requests.post(f"{self.api_url}/data", json=config_data, timeout=10) # Increased timeout
            response.raise_for_status()
            data = response.json()
            
            # Debug logging
            _logger.info(f"Received data from API for device {self.name}: {data}")
            
            # Update device status based on API response
            self.status = data.get('connectionStatus', 'error')
            
            # Get values array from the response
            values = data.get('values', [])
            if not isinstance(values, list):
                values = []
            
            # Debug logging
            _logger.info(f"Extracted values for device {self.name}: {values}")
            
            # Convert values to strings and handle None/0 values
            formatted_values = []
            # Use the actual starting register from the device config
            for i, value in enumerate(values):
                register_num = self.starting_register + i
                formatted_values.append(f"Register {register_num}: {value}")
                # Debug: print all device monitors
                all_monitors = self.env['device.monitor'].search([])
                print(f"!!! All device monitors: {[(m.id, m.device_id, m.device_id._name if m.device_id else None, m.active) for m in all_monitors]}")
                print(f"!!! Searching for device monitors with device_id={self.id} and active=True")
                reference = f"modbus.device,{self.id}"
                monitors = self.env['device.monitor'].search([('device_id', '=', reference), ('active', '=', True)])
                print(f"!!! Found monitors: {monitors}")
                for monitor in monitors:
                    print(f"!!! DeviceMonitor _process_plc_data called: register={register_num}, value={value}")
                    monitor._process_plc_data(str(register_num), value)
            # Debug logging
            _logger.info(f"Formatted values for device {self.name}: {formatted_values}")
            
            
            # Update the last_values field
            self.last_values = '\n'.join(formatted_values) if formatted_values else 'No data received'
            self.last_error = data.get('error')

            # Determine status and message based on API response
            message = ''
            message_type = 'info'

            if data.get('error'):
                message = f'Error fetching data for device {self.name}: {data.get("error")}'
                message_type = 'danger'
            elif not values:
                 message = f'No data received from device {self.name}'
                 message_type = 'warning'
            else:
                message = f'Data fetched successfully for device {self.name}:\n' + '\n'.join(formatted_values)
                message_type = 'success'
            
            # If polling, keep status as 'polling', else set to 'connected' (if no error)
            if self.is_polling and self.status != 'error': # Added check for error status
                 self.status = 'polling'
            elif self.status != 'error':
                 self.status = 'connected'

            # Create historical data records for each value
            # Only create records if values were successfully read and no major error
            if values and not data.get('error'): # Added check for values and error
                for i, value in enumerate(values):
                    self.env['modbus.data'].create({
                        'device_id': self.id,
                        'timestamp': datetime.now(),
                        'register_number': self.starting_register + i, # Use device's starting register
                        'value': value,
                        'error': data.get('error') # Record error if any for this fetch
                    })
                # Calculate and log latency
                end_time = time.time()
                fetch_time = end_time - start_time
                latency = fetch_time * 1000 #convert to milliseconds
                _logger.info(f"Time taken to fetch data for device {self.name}: {fetch_time} seconds, latency: {latency} ms")

            # Show appropriate message based on status
            # This part is redundant as message and message_type are already determined above
            # if data.get('error'):
            #     message = f'Error: {data.get("error")}'
            #     message_type = 'danger'
            # else:
            #     if not values:
            #         message = 'No data received from device'
            #         message_type = 'warning'
            #     else:
            #         message = 'Data fetched successfully:\n' + '\n'.join(formatted_values)
            #         message_type = 'success'
            
            # Debug logging
            _logger.info(f"Final message for device {self.name}: {message}")
            
            # Only show notification if there is an error or if it's not polling (to avoid spamming notifications)
            if data.get('error') or not self.is_polling:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': f'Modbus Data for {self.name}', # Include device name in title
                        'message': message,
                        'type': message_type,
                        'sticky': bool(data.get('error') or message_type == 'warning'), # Sticky for errors and warnings
                    }
                }
            # If polling and no error/warning, return an empty action to not display a notification
            return False # Return False to suppress notification during successful polling

        except requests.exceptions.ConnectionError as e:
            error_msg = f"Could not connect to Modbus API at {self.api_url} for device {self.name}. Please ensure the API server is running." # Include device name
            self.status = 'error'
            self.last_error = error_msg
            _logger.error(error_msg)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': f'API Connection Error for {self.name}', # Include device name
                    'message': error_msg,
                    'type': 'danger',
                    'sticky': True,
                }
            }
        except Exception as e:
            error_msg = f"Error fetching data for device {self.name}: {str(e)}" # Include device name
            self.status = 'error'
            self.last_error = error_msg
            _logger.error(error_msg)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': f'Data Fetch Error for {self.name}', # Include device name
                    'message': error_msg,
                    'type': 'danger',
                    'sticky': True, # Changed to sticky
                }
            }

    def action_view_data(self):
        self.ensure_one()
        return {
            'name': 'Historical Data',
            'type': 'ir.actions.act_window',
            'res_model': 'modbus.data',
            'view_mode': 'list,form',
            'domain': [('device_id', '=', self.id)],
            'context': {'default_device_id': self.id}
        }

    def action_clear_historical_data(self):
        self.ensure_one()
        # Delete all historical data for this device
        self.env['modbus.data'].search([('device_id', '=', self.id)]).unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Historical Data',
                'message': 'All historical data has been cleared',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_start_polling(self):
        self.ensure_one()
        if self.is_polling:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Polling Already Running',
                    'message': 'Auto fetch is already running for this device.',
                    'type': 'warning',
                    'sticky': False,
                }
            }

        # Create a new cursor for the thread setup
        with self.env.registry.cursor() as cr:
            env = api.Environment(cr, self.env.uid, self.env.context)
            device = env['modbus.device'].browse(self.id)
            
            # Ensure we're not polling and commit this change
            device.write({'is_polling': False})
            cr.commit()
            
            # Start new polling with fresh state
            interval = max(1, int(self.polling_interval / 1000))
            device.write({'is_polling': True, 'status': 'polling'})
            cr.commit()

        def poller(device_id, interval):
            db_name = self.env.cr.dbname
            uid = self.env.uid
            context = self.env.context
            
            while True:
                try:
                    with odoo.registry(db_name).cursor() as cr:
                        env = api.Environment(cr, uid, context)
                        device = env['modbus.device'].browse(device_id)
                        
                        # Check if polling should continue
                        if not device.is_polling:
                            _logger.info(f"Polling stopped for device {device_id}")
                            break
                            
                        _logger.info(f"Polling device {device_id} at interval {interval}s")
                        device.fetch_data()
                        cr.commit()
                        
                        # Sleep outside the cursor context
                        time.sleep(interval)
                except Exception as e:
                    _logger.error(f"Polling thread for device {device_id} crashed: {e}")
                    # Ensure we clean up if there's an error
                    with odoo.registry(db_name).cursor() as cr:
                        env = api.Environment(cr, uid, context)
                        device = env['modbus.device'].browse(device_id)
                        device.write({'is_polling': False, 'status': 'error'})
                        cr.commit()
                    break

        thread = threading.Thread(target=poller, args=(self.id, interval), daemon=True)
        thread.start()
        
        _logger.info(f"Started polling thread for device {self.id}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Polling Started',
                'message': f'Auto fetch started every {self.polling_interval} ms.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_stop_polling(self):
        self.ensure_one()
        if self.is_polling:
            # Use a new cursor to ensure the change is committed
            with self.env.registry.cursor() as cr:
                env = api.Environment(cr, self.env.uid, self.env.context)
                device = env['modbus.device'].browse(self.id)
                device.write({'is_polling': False, 'status': 'connected'})
                cr.commit()
            
            _logger.info(f"Stopped polling for device {self.id}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Polling Stopped',
                    'message': 'Auto fetch stopped.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Polling Not Running',
                    'message': 'No polling thread was running for this device.',
                    'type': 'info',
                    'sticky': False,
                }
            }
        
    def action_clear_historical_data(self):
        self.ensure_one()
        self.env['modbus.data'].search([('device_id', '=', self.id)]).unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Historical Data',
                'message': 'All historical data has been cleared',
                'type': 'success',
                'sticky': False,
            }
        }