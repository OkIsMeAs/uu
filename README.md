task1：

基本概述：本代码实现了tcp传输 ， 服务端可以多线程回答相应的客户端。

环境要求：本实验只需要下载python并将路径配置到系统就可以在终端打开

运行方法：
客户端：cmd打开终端后，输入python client.py +服务器绑定的HOST + PORT + lmin + lmax + SEED + Messege.txt
服务器：cmd打开终端，输入python server.py ,  在不ctrl+c情况下一直运行

运行概述：
客户端通过依次输入HOST,PORT,lmin,lmax,SEED,TEXTNAME来连接到服务器。
然后用户端开始按照种子分块，发送分块后的信息，终端将第几次返回的反转的内容输出到终端上。
在传输完毕后，客户端正常关闭。

服务器一直运行，倾听来自不同地址传来的数据，在每个客户端完成任务后，关闭此连接，并输出关闭状态

文件作用告知：
此文件夹下有三个txt文件，分别是server日志（UTF-8），Messege（Ascii），client记录（ASCii）
server日志：包含服务器接受的数据报告，和发送的数据报告以及出错报告等，都有相应的加粗提示，传入的数据都是str后的字节类型
client记录：包含着从服务器传来的反转数据，经过decode
Messege：从这个文件中直接读取文字

task2
基本概述：此代码实现了基于SR协议的UDP传输，服务器支持多线程应对客户端

环境要求：下一个python就可以，终端打开

如何运行：
客户端：cmd打开终端后，输入python client.py +服务器绑定的HOST和PORT + SEED
服务端：cmd打开终端，输入python server.py，在不ctrl+c的情况上一直运行

文件作用描述：
此文件夹下有两个txt文本，一个server日志，一个是client发送文件
server日志（utf-8）:记录每次服务器收报，发包，重发，超时，错误记录
在客户端运行后自动发送文件，在服务器发送重发请求后会自动重发，重发完毕后客户端直接关闭
