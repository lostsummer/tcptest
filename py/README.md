# 文件

uvserver.py            测试服务器

uvcli.py               测试客户端

transdata.py         测试数据协议实现类，被 server.py 和 cli.py 调用

transdata.json       客户端发送数据

# 服务器启动

./uvserver.py [port]

例如：

    ./server.py 8888

ctrl + c 终止并打印出接收到的连接数（windows 上不能终止）

# 客户端发送

./uvcli.py [ip] [port] [conumber] [loopcnt]

例如：

    ./cli.py 192.168.8.211 8888 20 5

向 192.168.8.211 888 并发 20 个连接，发送一个请求并收到应答后断开连接，重复 5 轮，共计 100 个连接


./longcli.py [ip] [port] [conumber] [time]

例如：

    ./longcli.py 192.168.8.211 8888 20 5

向 192.168.8.211 888 并发 20 个长连接，持续5秒

发送结束后打印发送数，成功数，总计发送时间

发送成功的逻辑是连接成功并要验证回包包头 head_id（0x99 0x88），data_type （请求类型 + 100），data_len（包长度 - 包头长度）

# 数据包构造 transdata.json

根据张涛为拟定协议

    {
        "head": {
            "head_id": 34969,
            "data_type": 10101,
            "data_id": 1
        },
        "content": "Hello world!",
        "codec": "ascii"
    }

其中包头 data_len 和 包内容字符串长度并不给出，因为需要根据字符串 content 动态算出，codec 指定 字符串编码，同样的字符串在不同编码中长度不一定相同

# 测试环境

1. 系统最好是 linux 修改(添加)系统内核参数:/etc/sysctl.conf （避免大量timewait）

		net.ipv4.tcp_fin_timeout=2
		net.ipv4.tcp_tw_reuse=1
		net.ipv4.tcp_tw_recycle=1

2. 安装 python3.6

   pip install uvloop