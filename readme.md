# Anti-SSH-Attack 分析一波现实中的 SSH 爆破攻击

基于自己部署在阿里云的ECS中提取出的 `auth.log*` 日志进行分析。



```bash
scp root@<target ip>:/var/log/auth.* .

conda create --name anti-attack python=3.12.7

python -m pip install pandas wordcloud matplotlib
```

*简单分析一波之后感觉 SSH 真难打，就这样爆破都能拦住，不愧是跟林神一个学校（赫尔辛基大学）的Tatu Ylonen，真的对得起 Secure Shell 这个名号*