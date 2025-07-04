const ModbusRTU = require("modbus-serial");
const express = require("express");
require('dotenv').config();

const app = express();
const port = process.env.API_PORT || 3001;

// Enable JSON parsing for POST requests
app.use(express.json());

// Connection pool to store multiple Modbus clients
const connectionPool = new Map();

// Function to get a unique key for each PLC
const getPlcKey = (ip, port, slaveId) => `${ip}:${port}:${slaveId}`;

// Function to get or create a Modbus client
const getModbusClient = async (ip, port, slaveId) => {
    const key = getPlcKey(ip, port, slaveId);
    
    if (!connectionPool.has(key)) {
        const client = new ModbusRTU();
        connectionPool.set(key, client);
    }
    
    const client = connectionPool.get(key);
    
    if (!client.isOpen) {
        console.log(`Creating new connection to ${ip}:${port} (Slave ID: ${slaveId})`);
        await client.connectTCP(ip, { port: port });
        client.setID(slaveId);
    }
    
    return client;
};

// Function to close a specific PLC connection
const closePlcConnection = async (ip, port, slaveId) => {
    const key = getPlcKey(ip, port, slaveId);
    if (connectionPool.has(key)) {
        const client = connectionPool.get(key);
        if (client.isOpen) {
            await client.close();
        }
        connectionPool.delete(key);
    }
};

// This will store the latest read values (kept for /config status, but not updated by polling)
let latestModbusData = {
    values: [],
    timestamp: null,
    error: null,
    connectionStatus: 'disconnected'
};

// REST API endpoints
app.post("/data", async (req, res) => {
    const { ip, port, slaveId, startingRegister, numberOfRegisters } = req.body;
    
    const start_time = Date.now(); //for measuring the time it takes to fetch data

    // Validate input
    if (!ip || port === undefined || slaveId === undefined || startingRegister === undefined || numberOfRegisters === undefined) {
        console.error("❌ Invalid data request: Missing configuration parameters in body", req.body);
        return res.status(400).json({
            error: "Invalid request",
            message: "Missing configuration parameters (ip, port, slaveId, startingRegister, numberOfRegisters)",
            connectionStatus: 'error'
        });
    }

    let responseData = {
        values: [],
        timestamp: null,
        error: null,
        connectionStatus: 'disconnected'
    };

    try {
        const client = await getModbusClient(ip, port, slaveId);
        console.log(`Reading registers: Starting at ${startingRegister}, Count: ${numberOfRegisters}`);
        const response = await client.readHoldingRegisters(startingRegister, numberOfRegisters);

        responseData.values = response.data;
        responseData.timestamp = new Date().toISOString();
        responseData.connectionStatus = 'connected';

        // Calculate and log latency
        const end_time = Date.now();
        const fetch_time = end_time - start_time;
        console.log(`Time taken to fetch data for ${ip}:${port}: ${fetch_time} ms`);

        console.log(`Read successful for ${ip}:${port}:`, response.data);

    } catch (error) {
        console.error(`❌ Error processing data request for ${ip}:${port}:`, error.message);
        responseData.error = `Error: ${error.message}`;
        responseData.connectionStatus = 'error';
        
        // Close the connection on error
        await closePlcConnection(ip, port, slaveId);
    }

    console.log("Sending data response for request:", responseData);
    res.json(responseData);
});

// Start the server
app.listen(port, () => {
    console.log(`🌐 REST API running at http://host.docker.internal:${port}`);
    console.log(`📝 Data endpoint: POST http://host.docker.internal:${port}/data (requires config in body)`);
    console.log(`📝 Config endpoint: GET/POST http://host.docker.internal:${port}/config`); // unused in this version
    console.log("API server is ready to receive data requests with device configurations.");

});