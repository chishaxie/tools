Comm Shell
=====

### ����nattchΪ0�Ĺ����ڴ�
    ipcs -m | awk '{if($6=="0")print $1}' | xargs -i ipcrm -M {}
	ipcs -m | awk '{if($6=="0")print $2}' | xargs -i ipcrm -m {}

### �����ı��ϲ���һ��
    awk 'BEGIN{pl="";n=0;}{if(NR%2!=0)pl=$0;else print pl,$0;++n;}END{if(n%2!=0)print pl;}'

### �������ڴ�ʹ�ô�С�������
    ps aux | awk '{print $5,$6,$11,$2}' | sort -n | tail -n20

### ����ȫ��C/C++Դ������Я����HexDump���ģ�������ļ�����
    ls | grep \.[ch]p*$ | xargs -i grep -H "HexDump" {}

### �ı�key����ͳ�ƴ����������ı�Ϊkey��������ظ������������־��
    cat file | sort | uniq -c | sort -r -k1 | head -n100

### �ı�key����ͳ��val�������ı�Ϊkv��������ظ�����
	cat file | awk '{t[$1]+=$2}END{for(e in t)print e,t[e]}'

### �鿴�������ļ��ķ��ű�C++����ԭ�ͣ�
    nm --demangle file

### ʮ������Hex��תtcpdump -X��ʽ
    echo '00112233445566778899aabbccddeeffABCDEF' | xxd -ps -r | xxd | sed 's#^.\{3\}##'

### �鿴GCC��Ĭ�Ϻ궨��
    gcc -dM -E - < /dev/null

### GDB�����ȡSIGSEGV�ź�ʱ���ʵĵ�ַ
    p $_siginfo._sifields._sigfault.si_addr

### ������ͨѶ������Flood ping��
    ping -f 10.130.91.219 -c10000
