import os
import glob

def extract_sshd_logs(source_dir, target_path):
    """
    从多个日志文件中提取包含 'blog sshd' 的日志行并写入目标文件
    
    Args:
        source_dir: 源文件所在目录
        target_path: 目标文件路径
    """
    # 确保目标目录存在
    target_dir = os.path.dirname(target_path)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 查找所有匹配的日志文件
    log_files = glob.glob(os.path.join(source_dir, "auth.log*"))
    
    # 提取所有匹配的行
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
    
    # 写入目标文件
    try:
        with open(target_path, 'w', encoding='utf-8') as target_file:
            target_file.writelines(matched_lines)
        
        print(f"Sucessfully export {len(matched_lines)} to {target_path}")
        print(f"Totally process {processed_files} files")
    except Exception as e:
        print(f"Error: {e}")

# 定义源目录和目标文件的路径
source_directory = "./source"
target_file_path = "./target/target.txt"

# 执行提取操作
extract_sshd_logs(source_directory, target_file_path)