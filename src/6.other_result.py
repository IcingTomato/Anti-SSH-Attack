import re
import csv
import os
from pathlib import Path

def main():
    # Ensure output directory exists
    Path("result").mkdir(exist_ok=True)
    
    # Open input and output files
    input_file = "target/others.txt"
    output_file = "result/others.csv"
    
    # Define CSV headers
    headers = ["PID", "Date", "Time", "IP Address", "Port", "Username", "Scenario", "Details"]
    
    # Store processed data
    processed_data = []
    
    # Define patterns to exclude
    exclude_patterns = ["Received signal", "Server listening", "Invalid user  from"]
    
    # Read input file
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines containing excluded patterns
            if any(pattern in line for pattern in exclude_patterns):
                continue
                
            # Extract basic information (date, time and PID)
            base_match = re.match(r'(\w+\s+\d+)\s+(\d+:\d+:\d+)\s+\w+\s+sshd\[(\d+)\]:\s+(.*)', line)
            if not base_match:
                continue
                
            date, time, pid, message = base_match.groups()
            
            # Initialize fields
            ip_address = "NULL"
            port = "NULL"
            username = "NULL"
            scenario = "NULL"
            details = "NULL"
            
            # Check for special "Connection closed by invalid user IP" pattern
            invalid_user_direct_ip_match = re.search(r'Connection closed by invalid user (\d+\.\d+\.\d+\.\d+) port (\d+)', message)
            if invalid_user_direct_ip_match:
                ip_address = invalid_user_direct_ip_match.group(1)
                port = invalid_user_direct_ip_match.group(2)
                scenario = "Connection closed"
                details = "invalid user"
                # Keep username as "NULL"
            else:
                # Check for authenticating user pattern
                auth_user_match = re.search(r'Connection closed by authenticating user (\S+) ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+) port (\d+)', message)
                if auth_user_match:
                    username = auth_user_match.group(1)
                    ip_address = auth_user_match.group(2)
                    port = auth_user_match.group(3)
                    scenario = "Connection closed"
                    details = "authenticating user"
                else:
                    # Extract IP address and port (standard pattern)
                    ip_port_match = re.search(r'(?:from|by)\s+(?:invalid user\s+)?([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(?:\s+port\s+(\d+))?', message)
                    if ip_port_match:
                        ip_address = ip_port_match.group(1)
                        if ip_port_match.group(2):
                            port = ip_port_match.group(2)
                    
                    # Extract username (standard pattern) - only if we didn't match the previous pattern
                    username_match = re.search(r'user\s+(\S+)\s+from', message)
                    if username_match:
                        username = username_match.group(1)
                
                # Determine scenario and details
                if "Connection closed by" in message:
                    scenario = "Connection closed"
                    if "invalid user" in message:
                        details = "invalid user"
                    else:
                        details = "IP"
                elif "Connection reset by" in message:
                    scenario = "Connection reset"
                    details = "IP"
                elif "error: kex_exchange_identification:" in message:
                    if "Connection closed by remote host" in message:
                        scenario = "Connection closed"
                        details = "remote host"
                    elif "Connection reset by peer" in message:
                        scenario = "Connection reset"
                        details = "peer"
                    elif "banner line contains invalid characters" in message:
                        scenario = "banner line contains invalid characters"
                    elif "client sent invalid protocol identifier" in message:
                        scenario = "client sent invalid protocol identifier"
                        protocol_match = re.search(r'identifier\s+"([^"]+)"', message)
                        if protocol_match:
                            details = protocol_match.group(1)
                elif "ssh_dispatch_run_fatal:" in message:
                    dh_match = re.search(r'DH GEX group out of range', message)
                    if dh_match:
                        scenario = "DH GEX group out of range"
            
            # Add to processed data
            processed_data.append([pid, date, time, ip_address, port, username, scenario, details])
    
    # Write to CSV file
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(processed_data)
    
    print(f"Processing completed, results written to {output_file}")

if __name__ == "__main__":
    main()