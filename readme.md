# Anti-SSH-Attack 分析一波现实中的 SSH 爆破攻击

基于自己部署在阿里云的ECS中提取出的 `auth.log*` 日志进行分析。

## 目录结构

```bash
.
+---archive # 存放 auth.log* 的目录
+---font    # 词云字体文件
+---img     # 词云图片 
+---result  # 存放经过清洗筛选的文件 *.csv
+---source  # 存放解压过的 auth.log.*.gz 文件
+---src     # 源码
\---target  # 存放初次清洗过的文件 *.txt
```

## 运行环境

- [x] Debian/Ubuntu 目标服务器 *RHEL/SUSE没试过*
- [x] 自带/能装的了SSH服务和Python3环境的本地设备
- [ ] [Anaconda3](https://www.anaconda.com/download/success) *非必须，只是我用着舒服*

## 运行步骤

1. 本地设备拉取远端的 `auth.log*` 日志

    ```bash
    scp <username>@<target ip>:/var/log/auth.* ./archive
    ```

    如果有些日志因为时间久远归档了，可以先解压再拉取：

    ```bash
    gzip -d auth.log.*.gz
    scp <username>@<target ip>:/var/log/auth.log.* ./source
    ```

2. 创建 Python venv 环境

    ```bash
    conda create --name anti-attack python=3.12.7
    ```

3. 安装依赖

    ```bash
    python -m pip install pandas wordcloud matplotlib
    ```

4. 按序号执行 `src` 目录下的 Python 脚本

    ```bash
    +---src
    |       1.clean.py                  # 清洗
    |       2.accepted.py               # 统计成功登录的记录
    |       3.deny.py                   # 统计拒绝登录的记录
    |       4.analysis.py               # 统计字典爆破登录失败的记录
    |       5.others.py                 # 清洗除字典爆破以外登录失败的记录
    |       6.other_result.py           # 统计除字典爆破以外登录失败的记录
    /       7.final.py                  # 最终结果 按攻击时间递增排序
    /       8.wordcloud_ip.py           # 攻击方IP 词云
    |       9.wordcloud_username.py     # 字典爆破 用户名词云
    |       10.find_source.py           # 查找源IP
    |       11.wordcloud_source.py      # 源IP 词云
    |       12.datetime_audit.py        # 基于日期时间的统计
    |       anti_attack.sh              # /etc/hosts.deny 规则
    ```

    `anti_attack.sh` 这个脚本是用来将攻击方IP添加到 `/etc/hosts.deny` 中的，使用时需要 `sudo` 权限。脚本使用方式参见[此处](http://icing.fun/2025/05/12/server_maintain/#title2)。

## 前言

此次分析时间范围从2025年4月13日到2025年5月13日。分析样本来自自己部署在阿里云的ECS中提取出的 `auth.log*` 用户日志（`auth.log`, `auth.log.1`, `auth.log.2.gz`, `auth.log.3.gz`, `auth.log.4.gz` 共五份用户日志）。操作系统为 Ubuntu 20.04.2 LTS。

> 用户日志：保留成功或失败登录和身份验证过程的身份验证日志。存储取决于系统类型。对于 Debian/Ubuntu，请查看 /var/log/auth.log。对于 Redhat/CentOS，请转到 /var/log/secure。

### 知识

SSH（Secure Shell，安全外壳）是一种网络安全协议，通过加密和认证机制实现安全的访问和文件传输等业务。传统远程登录和文件传输方式，例如Telnet、FTP，使用明文传输数据，存在很多的安全隐患。随着人们对网络安全的重视，这些方式已经慢慢不被接受。SSH协议通过对网络数据进行加密和验证，在不安全的网络环境中提供了安全的网络服务。作为Telnet和其他不安全远程shell协议的安全替代方案，目前SSH协议已经被全世界广泛使用，大多数设备都支持SSH功能。默认情况下，SSH服务器使用端口号22。

详情参见[什么是SSH？](https://info.support.huawei.com/info-finder/encyclopedia/zh/SSH.html)

SSH 攻击有多种类型：SSH 端口扫描、SSH 暴力攻击、使用受损 SSH 服务器的攻击。使用受感染服务器的攻击可能是 DoS 攻击、网络钓鱼攻击、垃圾邮件等。本文质疑来自受感染的 SSH 服务器的攻击是否与使用网络流的其他攻击隔离开来。在这项工作中，我们将 SSH 攻击分为两种类型。第一类包括 SSH 服务器成功入侵后的所有攻击活动。我们将其命名为“严重”攻击。第二种类型包括导致成功入侵的所有攻击。它包括 SSH 端口扫描、SSH 暴力攻击和没有活动的受损 SSH 服务器。第二类被命名为“不太严重”的攻击。[^2]

### 日志审计


[^2]: [Classification of SSH Attacks Using Machine Learning Algorithms](https://ieeexplore.ieee.org/document/7740316)