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

2. Start the server:
```bash
npm start
```

3. Run the Modbus API:
`node modbusapi.js`

## API Endpoints

### POST /data
Read Modbus registers from a device.

**Request body:**
```json
{
  "ip": "192.168.1.100",
  "port": 502,
  "slaveId": 1,
  "startingRegister": 0,
  "numberOfRegisters": 2
}
```

**Response:**
```json
{
  "values": [123, 456],
  "timestamp": "2024-03-14T12:00:00.000Z",
  "error": null,
  "connectionStatus": "connected"
}
```
- All configuration is provided per-request in the body.
- The server manages connections and will reconnect as needed.


## Error Handling
- Automatic reconnection on connection loss
- Detailed error reporting in API responses

## Future Improvements
- Add write operations
- Add support for different Modbus functions
- Add authentication
- Add data validation 
- PLC-to-PLC communication inside the Server
- add more API endpoints for flexibility