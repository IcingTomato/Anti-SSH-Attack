#!/bin/bash

# 脚本功能：从/var/log/auth.log和/var/log/auth.log.N提取SSH失败登录的IP地址并添加到/etc/hosts.deny

# 检查是否有root权限
if [ "$(id -u)" -ne 0 ]; then
    echo "Need root!"
    exit 1
fi

# 查找所有匹配的日志文件
log_files=(/var/log/auth.log /var/log/auth.log.*)

# 检查是否找到至少一个有效的日志文件
valid_files=0
for log_file in "${log_files[@]}"; do
    if [ -f "$log_file" ]; then
        valid_files=$((valid_files+1))
    fi
done

if [ $valid_files -eq 0 ]; then
    echo "Cannot find any auth.log files"
    exit 1
fi

# 计数器
added=0
skipped=0

# 处理每个找到的日志文件
for log_file in "${log_files[@]}"; do
    # 跳过不存在的文件
    if [ ! -f "$log_file" ]; then
        continue
    fi

    echo "Processing $log_file..."
    
    # 查找包含"port"但不包含正常连接行为的记录，提取IP地址
    grep "port" "$log_file" | grep -v -E "(Accepted password|Received disconnect|Disconnected from user)" | while read -r line; do
        # 使用正则表达式提取from和port之间的IP地址
        if [[ $line =~ from[[:space:]]+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)[[:space:]]+port ]]; then
            ip="${BASH_REMATCH[1]}"
            
            # 检查是否已经在hosts.deny文件中
            if grep -q "sshd: $ip" /etc/hosts.deny; then
                echo "Pass $ip (exist)"
                ((skipped++))
            else
                # 将IP地址追加到hosts.deny
                echo "sshd: $ip" >> /etc/hosts.deny
                echo "Block $ip"
                ((added++))
            fi
        fi
    done
done

echo "Done! Add: $added, Exist: $skipped"