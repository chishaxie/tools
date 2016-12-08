Comm Shell
=====

### 清理nattch为0的共享内存
    ipcs -m | awk '{if($6=="0")print $1}' | xargs -i ipcrm -M {}
    ipcs -m | awk '{if($6=="0")print $2}' | xargs -i ipcrm -m {}

### 两行文本合并成一行
    awk 'BEGIN{pl="";n=0;}{if(NR%2!=0)pl=$0;else print pl,$0;++n;}END{if(n%2!=0)print pl;}'

### 以虚拟内存使用大小排序进程
    ps aux | awk '{print $5,$6,$11,$2}' | sort -n | tail -n20

### 以内存使用率大小排序进程
    ps aux | awk '{print $4"%",$1,$5,$6,$2,$11,$12,$13,$14,$15,$16,$17,$18}' | sort -nr | head -n100

### 查找全部C/C++源代码中携带“HexDump”的（会输出文件名）
    ls | grep \.[ch]p*$ | xargs -i grep -H "HexDump" {}

### 文本key汇总统计次数并排序（文本为key的乱序可重复集，如访问日志）
    cat file | sort | uniq -c | sort -r -k1 | head -n100

### 文本key汇总统计val总数（文本为kv的乱序可重复集）
    cat file | awk '{t[$1]+=$2}END{for(e in t)print e,t[e]}'

### 查看二进制文件的符号表（C++函数原型）
    nm --demangle file

### 十六进制Hex串转tcpdump -X格式
    echo '00112233445566778899aabbccddeeffABCDEF' | xxd -ps -r | xxd | sed 's#^.\{3\}##'

### 查看GCC的默认宏定义
    gcc -dM -E - < /dev/null

### GDB里面获取SIGSEGV信号时访问的地址
    p $_siginfo._sifields._sigfault.si_addr

### 查网络通讯质量（Flood ping）
    ping -f 10.130.91.219 -c10000

### 按行乱序
    awk 'BEGIN{srand()}{b[rand()NR]=$0}END{for(x in b)print b[x]}'

### 将日志中的字符串时间转换为Unix时间戳
    echo "Wed Dec 07 2016 16:00:09 GMT+0800 (CST): Hello, sed!" | sed -r 's#^(.+GMT\+0800 \(CST\))(.*)$#echo -n $(date -d "\1" "+%s")"\2"#e'
