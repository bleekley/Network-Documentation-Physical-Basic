# Network Diagramming Scripts

This project contains Python scripts for generating network topology diagrams using CDP/LLDP information from network devices.

## Features:
- Collect Cisco Catalyst Switch discovery data from devices in the devices.csv file.
- Collect `show cdp neighbors` and `show lldp neighbors` from devices.
- Generate Mermaid diagrams of the network topology.
- Automatically omit certain patterns (like `.strongs.tv`).

## Prerequisites:
Ensure you have the following installed:
- Python 3.8 or later
- Git

## Setup Instructions:

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/network-diagramming-scripts.git
   cd network-diagramming-scripts
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv envNetDocs
   source venv/bin/activate #On Windows: venv\Scripts\activate
3. Install the required Python dependencies:
4. Create an _attributes.py file with your credentials:
5. Ensure that you have devices.csv file formatted like this:

## Running the Discovery Script:

- To collect physical Cisco network discovery:
   ```bash
   python3 scripts/discovery.py
A separate text file will be created in the current directory for each device in the devices.csv file with output from the following commands:
- show version
- show cdp neighbor
- show cdp neighbor detail
- show lldp neighbor
- show interface status
- show ip interface brief
- show ip arp
- show mac address-table
- show run

## Running the Markdown Script:

- To collect static diagram information:
  ```bash
  python3 scripts/localDiagram.py
Diagrams will be generated as .mmd files in the current directory.


