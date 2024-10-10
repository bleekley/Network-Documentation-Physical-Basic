import csv
import os
from ping3 import ping
from netmiko import ConnectHandler
import logging

# Initialize logger
logging.basicConfig(filename='session_data.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Function to load device credentials from a file (_attributes.py)
def load_credentials():
    from _attributes import username, password
    return username, password

# Function to ping a device
def ping_device(ip):
    response = ping(ip, timeout=2)
    return response is not None

# Function to SSH into a device and run commands
'''def ssh_to_device(ip, device_name, username, password):
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
    }

    try:
        logging.info(f"Connecting to {device_name} ({ip})")
        connection = ConnectHandler(**device)

        # Collect command outputs
        commands = [
            'show version', 'show cdp neighbor', 'show cdp neighbor detail',
            'show lldp neighbor', 'show interface status', 'show ip interface brief',
            'show ip arp', 'show mac address-table', 'show run'
        ]

        output = {}
        for cmd in commands:
            output[cmd] = connection.send_command(cmd)

        logging.info(f"Command output collected from {device_name} ({ip})")

        connection.disconnect()

        return output

    except Exception as e:
        logging.error(f"Failed to connect to {device_name} ({ip}): {str(e)}")
        return None'''
def ssh_to_device(ip, device_name, username, password):
    device = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password,
    }

    try:
        logging.info(f"Connecting to {device_name} ({ip})")
        connection = ConnectHandler(**device)

        # Collect command outputs
        commands = [
            'show version', 'show cdp neighbor', 'show cdp neighbor detail',
            'show lldp neighbor', 'show interface status', 'show ip interface brief',
            'show ip arp', 'show mac address-table', 'show run'
        ]

        output = {}
        for cmd in commands:
            output[cmd] = connection.send_command(cmd)

        logging.info(f"Command output collected from {device_name} ({ip})")

        # Disconnect after running the commands
        connection.disconnect()

        # Save output to a file
        with open(f'{device_name}_output.txt', 'w') as f:
            for cmd, cmd_output in output.items():
                f.write(f"### Output of {cmd} ###\n")
                f.write(cmd_output)
                f.write("\n\n")

        return output

    except Exception as e:
        logging.error(f"Failed to connect to {device_name} ({ip}): {str(e)}")
        return None

# Function to parse collected data and identify interfaces with no CDP/LLDP neighbors and more than 3 MACs
def analyze_interface_neighbors(cmd_output):
    # This function would parse the collected command outputs.
    # For simplicity, I'm assuming a parsed output for the sake of example.
    # You'd need to parse `show cdp neighbor`, `show lldp neighbor`, and `show mac address-table` carefully.

    interfaces_without_neighbors = []

    # Example logic to check interfaces and mac address table
    # You should parse real data based on your command output format.
    mac_table = cmd_output.get('show mac address-table')
    cdp_neighbors = cmd_output.get('show cdp neighbor')
    lldp_neighbors = cmd_output.get('show lldp neighbor')

    # Simplified logic to filter interfaces with no neighbors and more than 3 MAC addresses
    if mac_table and len(mac_table) > 3:
        interfaces_without_neighbors.append("interface_x")

    return interfaces_without_neighbors

# Main function
def main():
    # Load credentials
    username, password = load_credentials()

    # Dictionaries for reachable and unreachable devices
    reachable = {}
    unreachable = {}

    # Read the CSV file
    with open('devices.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            device_name = row['name']
            device_ip = row['ip']

            if ping_device(device_ip):
                logging.info(f"{device_name} ({device_ip}) is reachable")
                reachable[device_name] = device_ip
            else:
                logging.warning(f"{device_name} ({device_ip}) is unreachable")
                unreachable[device_name] = device_ip

    # Process reachable devices
    interfaces_info = {}
    for device_name, device_ip in reachable.items():
        cmd_output = ssh_to_device(device_ip, device_name, username, password)
        if cmd_output:
            interfaces_info[device_name] = analyze_interface_neighbors(cmd_output)
        else:
            logging.warning(f"No output collected from {device_name}")

    # Output unreachable devices to a file
    with open('unreachable_devices.txt', 'w') as file:
        for device_name, device_ip in unreachable.items():
            file.write(f"{device_name},{device_ip}\n")

    logging.info("Script completed successfully")

if __name__ == "__main__":
    main()
