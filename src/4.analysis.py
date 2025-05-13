import re
import csv
import os
from datetime import datetime

def analyze_ssh_logs(input_file, output_file):
    """Analyze SSH login failure logs, extract key information grouped by PID"""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Logs grouped by PID
    log_groups = {}
    
    # Read log file
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            pid_match = re.search(r'sshd\[(\d+)\]', line)
            if pid_match:
                pid = pid_match.group(1)
                if pid not in log_groups:
                    log_groups[pid] = []
                log_groups[pid].append(line)
    
    # Process results list
    results = []
    
    # Process each PID group
    for pid, lines in log_groups.items():
        entry = {"PID": pid}
        
        # Extract date (from first line)
        date_match = re.match(r'(\w+\s+\d+)', lines[0])
        if date_match:
            entry["Date"] = date_match.group(1)
        
        # Find the earliest timestamp
        earliest_time = None
        for line in lines:
            time_match = re.match(r'\S+\s+\S+\s+(\d+:\d+:\d+)', line)
            if time_match:
                time_str = time_match.group(1)
                time_obj = datetime.strptime(time_str, "%H:%M:%S")
                if earliest_time is None or time_obj < earliest_time:
                    earliest_time = time_obj
                    entry["Time"] = time_str
        
        # Extract IP address
        for line in lines:
            ip_match = re.search(r'(?:from|rhost=)\s*(\d+\.\d+\.\d+\.\d+)', line)
            if ip_match and "IP Address" not in entry:
                entry["IP Address"] = ip_match.group(1)
        
        # Extract port
        for line in lines:
            port_match = re.search(r'port\s+(\d+)', line)
            if port_match and "Port" not in entry:
                entry["Port"] = port_match.group(1)
        
        # Extract username
        for line in lines:
            # Try multiple patterns to extract username
            user_patterns = [
                r'user=(\w+)',
                r'Failed password for (?:invalid user )?(\w+)',
                r'Invalid user (\w+)',
                r'Connection closed by (?:authenticating|invalid) user (\w+)'
            ]
            
            for pattern in user_patterns:
                user_match = re.search(pattern, line)
                if user_match and "User Name" not in entry:
                    entry["User Name"] = user_match.group(1)
                    break
        
        # Add to results list only if all required fields are extracted
        required_fields = ["PID", "Date", "Time", "IP Address", "Port", "User Name"]
        if all(field in entry for field in required_fields):
            results.append(entry)
    
    # Sort by date and time
    def sort_key(entry):
        # Combine date and time for sorting
        # Here we assume date format is "May 11", time format is "HH:MM:SS"
        month_dict = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
            'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
        }
        
        date_parts = entry["Date"].split()
        month = month_dict.get(date_parts[0], 0)
        day = int(date_parts[1])
        
        # Current year (since logs don't include year)
        year = datetime.now().year
        
        # Parse time
        time_parts = entry["Time"].split(':')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2])
        
        return datetime(year, month, day, hour, minute, second)
    
    # Sort by date and time
    results.sort(key=sort_key)
    
    # Write to CSV file
    with open(output_file, "w", newline="") as f:
        fieldnames = ["PID", "Date", "Time", "IP Address", "Port", "User Name"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    return len(results)

def main():
    input_file = "target/deny.txt"
    output_file = "result/result.csv"
    
    record_count = analyze_ssh_logs(input_file, output_file)
    print(f"Done! Save to {output_file}, Totally {record_count}.")

if __name__ == "__main__":
    main()