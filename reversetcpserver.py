import threading
import struct
import socket
from datetime import datetime
def GetMessegeWriter(Messege,Address) :
	now = datetime.now()
	with open('server日志.txt' , 'a' , encoding  = 'utf-8') as f:
		f.write('【时间】' + str(now) + '时 ， 【收到ip地址为】' + str(Address[0]) + '【端口号为】' +  str(Address[1]) + '的【客户端】的数据' + Messege + '\n')
def SentMessegeWriter(Messege,Address) :
	now = datetime.now()
	with open('server日志.txt' , 'a' , encoding  = 'utf-8') as f:
		f.write('【时间】' + str(now) + '时 ， 【向ip地址为】' + str(Address[0]) + '【端口号为】' +  str(Address[1]) + '的【客户端】发送数据' + Messege + '\n')
def ErrorWriter(Messege , Address) :
	now = datetime.now()
	with open('server日志.txt' , 'a' , encoding = 'utf-8') as f:
		f.write('【时间】' + str(now) + '时 ， 【在和ip地址为】' + str(Address[0]) + '【端口号为】' +  str(Address[1]) + '的【客户端】接收数据时出现【错误】。    ' + Messege + '\n')
def RunningMessegeWriter(Messege) :
	now = datetime.now()
	with open('server日志.txt' , 'a' , encoding = 'utf-8') as f:
		f.write('时间' + str(now) + '时 , '  + Messege + '\n')
def SingleUser(UserSocket , UserAddress) :
	GetMessege = UserSocket.recv(6)
	GetMessegeWriter(str(GetMessege) , UserAddress)
	try :
		Types , Length = struct.unpack('>HI' ,  GetMessege)	
		if Types == 1 :
			UserSocket.send( struct.pack('>H' ,  2) )								#回应握手
			SentMessegeWriter( str(struct.pack('>H' ,  2)) ,UserAddress)
			while  1:																#进入对话
				Messege = UserSocket.recv(6)
				if Messege != b'' :
					Types , Length = struct.unpack('>HI' , Messege)
				else :
					break
				if Types == 3 :
					Communication  = UserSocket.recv(1024)
					GetMessegeWriter(str(Communication) , UserAddress)
					UserSocket.send( struct.pack('>HI' , 4 , Length ) )
					SentMessegeWriter( str(struct.pack('>HI' , 4 , Length )) , UserAddress)
					Back = Communication.decode('ascii')
					Reserve = Back[::-1]
					BackMessege = Reserve.encode('ascii')
					UserSocket.send(BackMessege)
					SentMessegeWriter(str(BackMessege) , UserAddress)
	except Exception as e :
		print(f'客户端{UserAddress}出现问题{e}')
		ErrorWriter('客户端' + str(UserAddress) + '出现问题:' + str(e) , UserAddress)
	finally :
		UserSocket.close()
		print(f'客户端{UserAddress}已关闭')
		RunningMessegeWriter('客户端' + str(UserAddress) + '已关闭')
HOST = '0.0.0.0'                     
PORT = 8888
serversocket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
serversocket.bind( (HOST , PORT) )
serversocket.listen(5)
RunningMessegeWriter('服务已开启！！！！')
while 1 : 
	UserSocket , UserAddress= serversocket.accept()
	RunningMessegeWriter('地址为' + str(UserAddress) + '的客户端加入')
	SingleConnect = threading.Thread(target = SingleUser , args = (UserSocket , UserAddress) )
	SingleConnect.daemon = True
	SingleConnect.start()