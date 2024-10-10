import csv
import os
from netmiko import ConnectHandler
import logging

# Initialize logger with console output
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s', handlers=[
    logging.FileHandler("mermaid_diagrams.log"),
    logging.StreamHandler()  # This will print to the terminal as well
])

# Function to load device credentials from a file (_attributes.py)
def load_credentials():
    from _attributes import username, password
    return username, password

# Function to SSH into a device and run commands
def ssh_to_device(ip, device_name, username, password):
    device = {
        'device_type': 'cisco_ios',  # Assuming Cisco IOS devices
        'ip': ip,
        'username': username,
        'password': password,
        'timeout': 10  # Adding a timeout of 10 seconds
    }

    try:
        logging.info(f"Connecting to {device_name} ({ip})")
        connection = ConnectHandler(**device)
        logging.info(f"Successfully connected to {device_name} ({ip})")

        # Collect command outputs
        commands = ['show cdp neighbors', 'show lldp neighbors']
        output = {}
        for cmd in commands:
            logging.debug(f"Running command: {cmd} on {device_name}")
            output[cmd] = connection.send_command(cmd)

        logging.info(f"Command output collected from {device_name} ({ip})")

        connection.disconnect()
        logging.info(f"Disconnected from {device_name} ({ip})")

        return output

    except Exception as e:
        logging.error(f"Failed to connect to {device_name} ({ip}): {str(e)}")
        return None

# Function to parse CDP output and extract neighbors
def parse_cdp_neighbors(cdp_output):
    neighbors = []
    current_device = None

    # Iterate over each line of the output
    for line in cdp_output.splitlines():
        logging.debug(f"Processing line: {line}")
        # Device ID indicates the start of a new neighbor block
        if not line.strip():
            continue  # Skip empty lines
        if line.startswith(" "):
            # Continuation of the current neighbor's data
            parts = line.split()
            if len(parts) >= 2 and current_device:
                local_interface = parts[0] + " " + parts[1]  # Local interface
                remote_interface = parts[-1]  # Remote device interface
                neighbors.append((current_device, local_interface, remote_interface))
                logging.debug(f"Neighbor added: {current_device}, Local: {local_interface}, Remote: {remote_interface}")
        else:
            # This is the Device ID (neighbor)
            parts = line.split()
            if len(parts) > 0:
                current_device = parts[0].replace(".strongs.tv", "")  # Remove .strongs.tv suffix
                logging.debug(f"Current device set to: {current_device}")

    return neighbors

# Function to create a Mermaid flowchart for a device
def create_mermaid_diagram(device_name, neighbors):
    device_name = device_name.replace(".strongs.tv", "")  # Remove .strongs.tv suffix from local device
    diagram = "graph TD\n"
    for neighbor in neighbors:
        neighbor_device = neighbor[0].replace(".strongs.tv", "")  # Remove .strongs.tv from neighbor device
        if "Capability" not in neighbor_device:  # Skip entries with "Capability"
            diagram += f"    {device_name} --> {neighbor_device}\n"
            logging.debug(f"Added to diagram: {device_name} --> {neighbor_device}")
    
    # Save the diagram to a file
    file_path = f'{device_name}_diagram.mmd'
    try:
        with open(file_path, 'w') as f:
            f.write(diagram)
        logging.info(f"Diagram saved: {file_path}")
    except Exception as e:
        logging.error(f"Failed to write file {file_path}: {str(e)}")

# Main function
def main():
    # Load credentials
    username, password = load_credentials()

    # Read the CSV file
    with open('devices.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_name = row['name']
            device_ip = row['ip']
            logging.info(f"Processing device: {device_name} ({device_ip})")

            # Connect to the device and get the CDP/LLDP outputs
            cmd_output = ssh_to_device(device_ip, device_name, username, password)
            if cmd_output:
                # Parse neighbors from the CDP output
                logging.debug(f"Parsing CDP neighbors for {device_name}")
                cdp_neighbors = parse_cdp_neighbors(cmd_output['show cdp neighbors'])

                # Create Mermaid diagram for the device
                create_mermaid_diagram(device_name, cdp_neighbors)
            else:
                logging.warning(f"No output collected from {device_name}")

    logging.info("Script completed successfully")

if __name__ == "__main__":
    main()
