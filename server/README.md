# Modbus Connector

This is a standalone Modbus TCP connector that provides a REST API for reading Modbus data.

## Features
- Modbus TCP communication
- Configurable through environment variables
- Automatic reconnection with retry logic
- REST API endpoints for data and configuration
- Real-time data polling

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file with your configuration:
```env
MODBUS_SERVER_IP=127.0.0.1
MODBUS_SERVER_PORT=502
MODBUS_SLAVE_ID=1
API_PORT=3000
POLLING_INTERVAL_MS=1000
STARTING_REGISTER=1
NUMBER_OF_REGISTERS=1
```

3. Start the server:
```bash
npm start
```

## API Endpoints

### GET /data
Returns the latest Modbus data:
```json
{
    "value": 123,
    "timestamp": "2024-03-14T12:00:00.000Z",
    "error": null,
    "connectionStatus": "connected"
}
```

### GET /config
Returns the current configuration:
```json
{
    "modbusServer": {
        "ip": "127.0.0.1",
        "port": 502,
        "slaveId": 1
    },
    "polling": {
        "interval": 1000,
        "startingRegister": 1,
        "numberOfRegisters": 1
    }
}
```

## Error Handling
- Automatic reconnection on connection loss
- Retry logic (5 attempts)
- Detailed error reporting in API responses

## Future Improvements
- Add support for multiple registers
- Add write operations
- Add support for different Modbus functions
- Add authentication
- Add data validation 