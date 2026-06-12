import struct
import json
import socket
import threading
from datetime import datetime
import random
#报文格式总结		
#	Types == 1： Types(1) + Add(2) + 长度 + data(列表信息)		收到
#	Types == 2:    Types(1) + Add(2) + 大小(2)			发送		和1配对
# 	Types == 3:    Types(1) + Add(2) + 段号(1) + 大小(2) + data  收到
#	Types == 4:	Types(1) + Add(2) + 段号(1)				发送		和3配对
#	Types == 5:	Types(1) + Add(2) + 需要的段号(1)			发送
#	Types == 6:    Types(1) + Add(2) + 段号(1) + 大小(2) + data	收到
#	Types == 7:	Types(1) + Add(2) + 段号(1)		发送			和6配对
#	Types == 8:	Types(1) + Add(2)				发送
#	Types == 9:	Types(1) + Add(2)				client告知可以进行补发了	收到
#	Types == 10:	Types(1) + Add(2)				server回应OK		发送 ， 和9配对
#	Types == 11:	Types(1) + Add(2)
def SendBag(Messege , Address) :  #发包记录
	now = datetime.now()
	with open(TEXTNAME , 'a' , encoding = 'utf-8') as f:
		f.write('【时间为】' + str(now) + '时 , ' +'服务器【发送信息】' +  Messege + '到【地址】' + str(Address) + '处\n')
def GetBag(Messege , Address)  :  #收包记录
	now = datetime.now()
	with open(TEXTNAME , 'a' , encoding = 'utf-8') as f:
		f.write('【时间为】' + str(now) + '时 ，' + '服务器【收到信息】' + Messege + '信息从【地址】' + str(Address) + '处\n')
def TimeOut(Address)  :  #超时记录
	now = datetime.now()
	with open(TEXTNAME , 'a' , encoding = 'utf-8') as f:
		f.write('【时间为】' + str(now) + '时 ，' + '服务器【出现超时情况】' + '向【地址】' + str(Address) + '发送信息时\n')
def SendAgain(Messege , Address) :   #重发记录
	now = datetime.now()
	with open(TEXTNAME , 'a' , encoding = 'utf-8') as f:
		f.write('【时间为】' + str(now) + '时 ，' + '服务器【重发信息】' + Messege + '到【地址】' + str(Address) + '处\n')
def ErrorWriter(Messege , Address) :    #错误记录
	now = datetime.now()
	with open(TEXTNAME , 'a' , encoding = 'utf-8') as f:
		f.write('【时间为】' + str(now) + '时 ，' + '服务器【出现错误】' + Messege + '【在向地址】' + str(Address) + '发信息时\n')

def Check(A) :
	studentid = A ^ 0x5A3C
	return studentid == STUDENTID
def SayHello(Data , Address) :
	try:
		List = Data[5 : ]
		LIST = json.loads(List.decode('utf-8'))
		Messege = struct.pack('>B' , 2) + Data[1 : 3] + struct.pack('>H' , len(LIST))
		if Address in DICT :
			serversocket.sendto(Messege , Address)
			SendBag(str(Messege) , Address)
		else :
			DICT[Address] = [0 , LIST , [None] * len(LIST)]
			serversocket.sendto(Messege , Address)
			SendBag(str(Messege) , Address)
		print('已收到来自' , Address , '的【列表】')
	except Exception as e:
		ErrorWriter(str(e) , Address)
def Get(Data , Address , ENCRYPTION) :
	try:
		print('收到来自【地址】' , Address ,'发来的第\033[32m' , struct.unpack('>B' , Data[3:4])[0] , '\033[0m段信息:' , Data[6:].decode('utf-8'))
		Block = struct.unpack('>B' , Data[3:4])[0]
		if Address in DICT :
			with LOCK :
				DICT[Address][2][Block - 1] = 1
			Messege = struct.pack('>BHB' , 4 , ENCRYPTION , Block)
			serversocket.sendto(Messege , Address)
			SendBag(str(Messege) , Address)
	except Exception as e:
		ErrorWriter(str(e) , Address)
HOST = '0.0.0.0'
PORT = 8888
STUDENTID = 2201
TEXTNAME = 'server日志.txt'
serversocket = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
serversocket.bind((HOST , PORT))
DICT = {}
LOCK = threading.Lock()
while True :
	Data , Address = serversocket.recvfrom(1024)
	try :
		Types , ENCRYPTION = struct.unpack('>BH' , Data[0:3])
		Probability = random.random()
		if	Probability < 0.3:
			TimeOut(Address)
			continue              #模拟丢包
		if Check(ENCRYPTION) :
			GetBag(str(Data) , Address)
			if Types == 1 :
				SingleUser = threading.Thread(target = SayHello , args = (Data , Address) , daemon = True)
				SingleUser.start()
			if Address in DICT :
				if DICT[Address][0] == 0 :
					if Types == 3 :
						SingleUser = threading.Thread(target = Get , args = (Data , Address , ENCRYPTION) , daemon = True)
						SingleUser.start()
				if Types == 9 :
					if DICT[Address][0] == 1:
						continue
					DICT[Address][0] = 1
					Messege = struct.pack('>BH' , 10 , ENCRYPTION)
					serversocket.sendto(Messege , Address)
					SendBag(str(Messege) , Address)
					while None in DICT[Address][2] :
						Index = DICT[Address][2].index(None)
						Messege = struct.pack('>BHB' , 5 ,ENCRYPTION , Index + 1)
						serversocket.sendto(Messege , Address)
						SendAgain(str(Messege) , Address)
						try:
							Data , Address2 = serversocket.recvfrom(1024)
							if Address2 == Address :
								GetBag(str(Data) , Address2)
								Types , ENCRYPTION = struct.unpack('>BH' , Data[0:3])
								if not Check(ENCRYPTION) :
									ErrorWriter('NO!!!!!!!!!!' , Address2)
									continue
								if Types == 6 :
									# ErrorWriter('6!!!!!!!!!!' , Address2)
									Block = struct.unpack('>B' , Data[3:4])[0]
									if DICT[Address2][2][Block - 1] is None :
										Messege = Data[6:]
										print('收到【补发】的第\033[31m' , struct.unpack('>B' , Data[3:4])[0] , '\033[0m段信息：\033[31m' , Messege.decode('utf-8') , '\033[0m')
										with LOCK:
											DICT[Address2][2][Block - 1] = 1
										BackMessege = struct.pack('>BHB' , 7 , ENCRYPTION , Block )
										serversocket.sendto(BackMessege , Address2)
										SendBag(str(BackMessege) , Address2)
								if Types == 9 :
									# ErrorWriter('9!!!!!!!!!!' , Address2)
									serversocket.sendto( struct.pack('>BH' , 10 , ENCRYPTION) , Address2)
								# ErrorWriter('YES!!!!!!!!!!' , Address2)
						except Exception as e:
							ErrorWriter(str(e) , Address)
					Messege = struct.pack('>BH' , 8 , ENCRYPTION)
					while 1:
						serversocket.sendto(Messege , Address)
						SendBag(str(Messege) , Address)
						try :
							Data , Address3 = serversocket.recvfrom(1024)
							if Address3 == Address :
								Types = struct.unpack('>B' , Data[0:1])[0]
								if Types == 11:
									break
						except Exception as e:
							ErrorWriter(str(e) , Address3)
	except Exception as e:
		ErrorWriter(str(e) , Address)