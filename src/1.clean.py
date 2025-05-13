import os
import glob

def extract_sshd_logs(source_dir, target_path):
    """
    Extract log lines containing 'blog sshd' from multiple log files and write to target file
    
    Args:
        source_dir: Source directory of log files
        target_path: Path to the target file
    """
    # Ensure target directory exists
    target_dir = os.path.dirname(target_path)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Find all matching log files
    log_files = glob.glob(os.path.join(source_dir, "auth.log*"))
    
    # Extract all matching lines
    matched_lines = []
    processed_files = 0
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as source_file:
                for line in source_file:
                    if "blog sshd" in line:
                        matched_lines.append(line)
            processed_files += 1
            print(f"Processing: {log_file}")
        except Exception as e:
            print(f"Process {log_file} error: {e}")
    
    # Write to target file
    try:
        with open(target_path, 'w', encoding='utf-8') as target_file:
            target_file.writelines(matched_lines)
        
        print(f"Successfully exported {len(matched_lines)} lines to {target_path}")
        print(f"Processed {processed_files} files in total")
    except Exception as e:
        print(f"Error: {e}")

# Define paths for source directory and target file
source_directory = "./source"
target_file_path = "./target/target.txt"

# Execute extraction operation
extract_sshd_logs(source_directory, target_file_path)