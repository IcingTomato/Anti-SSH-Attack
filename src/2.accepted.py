import re
import csv
import os

# Ensure target directory exists
target_dir = "target"
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# File paths
log_file_path = os.path.join(target_dir, "target.txt")
output_file_path = os.path.join(target_dir, "accepted.csv")

# Store extracted IP, port and PID
extracted_data = []

# Modify regex pattern to capture PID
pattern = r"sshd\[(\d+)\]: Accepted password for \S+ from (\d+\.\d+\.\d+\.\d+) port (\d+)"

try:
    # Read log file
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            # Find matching lines
            match = re.search(pattern, line)
            if match:
                # Extract PID, IP address and port
                pid = match.group(1)
                ip_address = match.group(2)
                port = match.group(3)
                extracted_data.append((ip_address, port, pid))
    
    # Write extracted data to CSV
    with open(output_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Write header row
        csv_writer.writerow(['IP Address', 'Port', 'PID'])
        # Write data rows
        for ip, port, pid in extracted_data:
            csv_writer.writerow([ip, port, pid])
    
    print(f"Done! Save to {output_file_path}")

except FileNotFoundError:
    print(f"Error: Cannot find {log_file_path}")
except Exception as e:
    print(f"Error: {e}")