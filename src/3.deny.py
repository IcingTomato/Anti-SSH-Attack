import csv
import os

def main():
    # Ensure target directory exists
    if not os.path.exists('target'):
        print("Error: target directory does not exist")
        return

    # Read PID list from accepted.csv
    pids = []
    try:
        with open('target/accepted.csv', 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                pids.append(row['PID'])
    except Exception as e:
        print(f"Error: Failed to read accepted.csv: {e}")
        return

    if not pids:
        print("Warning: No PIDs read from accepted.csv")

    # Read target.txt and filter matching lines
    filtered_lines = []
    try:
        with open('target/target.txt', 'r') as target_file:
            for line in target_file:
                # Check if line contains any sshd[PID]
                should_keep = True
                for pid in pids:
                    if f"sshd[{pid}]" in line:
                        should_keep = False
                        break
                
                if should_keep:
                    filtered_lines.append(line)
    except Exception as e:
        print(f"Error: Failed to read target.txt: {e}")
        return

    # Write filtered lines to deny.txt
    try:
        with open('target/deny.txt', 'w') as deny_file:
            deny_file.writelines(filtered_lines)
        print(f"Success: Filtered content written to target/deny.txt")
    except Exception as e:
        print(f"Error: Failed to write to deny.txt: {e}")

if __name__ == "__main__":
    main()