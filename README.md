My tools
=====

### bit.c
    按bit操作Buffer(支持快速查找Buffer中第一个bit为1的位置)

### get_exe_path.c
    获取当前可执行程序的完整路径(支持Linux和MacOS)

### strstr_sunday.c
    简单快速的字符串搜索(strstr)算法[最好O(n/m),最坏O(nm)]

### socket_flood.c
    TCP/UDP-flood工具(用于压测网络IO性能)

### vargs_count.c
    获取变长参数宏的参数个数(很巧妙)

### bitmap.cc
    Bitmap的数组化API(性能不高)

### emotion.cc
    Emotion表情转换(EmotionCode->描述)

### event_emitter.cc
    简单的事件触发器(参照JS的API,基于C++11)

### top-k.cc
    非精准top-k流式统计器(占用资源很少)

### httpNgin.js
    简单http静态文件+动态接口服务器

### shell2http.js
    shell命令转http服务，在服务器上起一个http服务，用GET的方式就可以使用命令行。（使用方式：nohup node shell2http.js &）

### tpl.js
    简单模板引擎(Javascript实现)，无任何依赖(可用于浏览器和NodeJS)，高效短小，压缩后仅800+字节

### img_resize.py
    等比例缩放图片(补黑边模式)

### imgs.py
    图片批量处理工具

### ipc_msgq.py
    基于共享内存的(进程间)定长消息队列

### jump_consistent_hash.py
    一致性Hash算法(简单、快速、省内存)

### ReadWriteLock.py
    线程读写锁(读读并发)

### tea.py
    64Bit(块)对称加密算法(秘钥长度128Bit)

### comm.sh
    日常生活中用到的各种Comm Shell命令(简短的功能性命令)

### misc
    一些杂七杂八的东西
