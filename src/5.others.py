import csv
import os
import sys

def main():
    # Define file paths
    result_csv_path = 'result/result.csv'
    deny_txt_path = 'target/deny.txt'
    others_txt_path = 'target/others.txt'
    
    try:
        # Read PID column from result.csv
        pids = []
        with open(result_csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pids.append(row['PID'])
        
        # Read all lines from deny.txt
        with open(deny_txt_path, 'r') as deny_file:
            lines = deny_file.readlines()
        
        # Separate matching and non-matching lines
        matching_lines = []
        non_matching_lines = []
        for line in lines:
            matched = False
            for pid in pids:
                if f"sshd[{pid}]" in line:
                    matching_lines.append(line)
                    matched = True
                    break
            if not matched:
                non_matching_lines.append(line)
        
        # Ensure target directory exists
        os.makedirs(os.path.dirname(others_txt_path), exist_ok=True)
        
        # Write non-matching lines to others.txt
        with open(others_txt_path, 'w') as others_file:
            others_file.writelines(non_matching_lines)
        
        # Write non-matching lines back to deny.txt (i.e., delete matching lines)
        with open(deny_txt_path, 'w') as deny_file:
            deny_file.writelines(non_matching_lines)
        
        print(f"Processing complete: Deleted {len(matching_lines)} matching lines from deny.txt")
        print(f"Non-matching lines have been written to {others_txt_path}")
    
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()