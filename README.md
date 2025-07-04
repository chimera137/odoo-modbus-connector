# odoo-modbus-connector
Odoo Module for Connecting Modbus Devices

## Overview
This repository contains the `odoo-modbus-connector` module, a custom Odoo ERP add-on designed to facilitate direct and configurable communication with Modbus TCP/IP devices. It serves as a foundational component for integrating shop-floor Modbus-enabled hardware with Odoo's business applications, enabling real-time data acquisition from industrial machinery.
This is a Third Party Module for Odoo ERP

## Features
- **Modbus Device Configuration**: Allows users to easily add and configure Modbus TCP/IP devices directly within Odoo by simply providing their IP address and port.   
- **Holding Register Data Fetching**: Supports configurable fetching of data from specified Holding Registers of connected Modbus devices.
- **Automated Polling**: Implements automatic data polling with a configurable minimum interval of 1000ms (1 second) to ensure near real-time data synchronization.

## System Architecture Context
This `odoo-modbus-connector` module is a vital part of a larger multi-vendor PLC integration system for Odoo ERP. It functions as one of the specialized connectors, working in conjunction with a dedicated Node.js-based REST API server that handles the direct Modbus communication.

## Getting Started

### Prerequisites
- Odoo ERP (v16.0 or higher recommended) instance.
- Node.js (LTS version recommended) installed on your server.
- A Modbus TCP/IP capable device for testing (or Modbus Slave Simulator).

### Installation
1. **Clone this repository:**
`git clone https://github.com/chimera137/odoo-modbus-connector.git`

2. **Place the module:** Copy the `odoo-modbus-connector` folder into your Odoo custom add-ons path (e.g., /path/to/odoo/addons/)

3. **Update and Install in Odoo:**
    - Restart your Odoo service.
    - Navigate to the Apps menu in your Odoo instance.
    - Click "Update Apps List" (if you don't see the module immediately).
    - Search for "Modbus Connector" and install the module.

### Running the Modbus API Server
This Odoo module relies on a companion Node.js server to handle the direct Modbus communication and expose data via a REST API.

1. **Navigate to the server directory:**
Assuming the Node.js server code is located in a server/modbusapi directory within this repository:
`cd /path/to/modbus_connector/server/`

2. **Install dependencies:**
`npm install`

3. **Run the server:**
`node modbusapi.js`
For production environments, it is highly recommended to use a process manager like PM2 to ensure the server runs continuously and automatically restarts on failures:
```
npm install -g pm2 # Install PM2 globally if not already installed
pm2 start modbusapi.js --name modbus_api_server
```

## Usage
Once the modbus_connector module is installed in Odoo and the Modbus API server is running:
1. **Access Modbus Device Configuration:**
Navigate to Manufacturing (or a custom menu if defined) -> Configuration -> Modbus Devices.

2. **Create a New Device:**
Click the "Create" button to add a new Modbus device entry.

3. **Enter Device Details:**
Provide the Modbus device's IP address and port.

4. **Configure Registers:**
Specify the Modbus Holding Registers you wish to read (e.g., register 0 to register 2).

5. **Data Acquisition:**
The Node.js server will automatically poll data from the configured Modbus devices and push it to Odoo according to the defined polling intervals.

### Integrating with Business Logic
This module primarily focuses on establishing connectivity with Modbus devices and fetching raw industrial data. To integrate this data into Odoo's core Manufacturing applications (e.g., updating production orders, real-time machine status, quality control, inventory deductions based on production counts), please refer to our complementary module:
[Device Monitor Module Repository](https://github.com/chimera137/odoo-device-monitor)

### Other Connector Modules
For connecting to OPC UA compatible devices as part of the multi-vendor integration framework, please explore our dedicated module:
[OPC UA Connector Module Repository](https://github.com/chimera137/odoo-opcua-connector)

## Acknowledgement
This project was developed as part of a undergraduate thesis for the Department of Electrical Engineering / Teknik Elektro at Petra Christian University Surabaya, Indonesia. The insights and methodologies explored herein contribute to the academic research in the field of industrial automation (IIoT) and ERP integration.

