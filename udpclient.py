import struct                            #模拟SR协议，向server发送总块数 AllNumber， client分 AllNumber次发送 ， server分AllNumber次监听，这个环节结束后进行补发，这个得精确补发，降低丢包率            
import socket							  
import sys
import time
import random
import json
import pandas as pd
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
#	Types == 11:	Types(1) + Add(2)		回应8
def SentText(TEXTNAME) :
	with open(TEXTNAME  , 'r' , encoding = 'utf-8') as f :
		CONTENT = f.read()
	LENGTH = len(CONTENT)
	random.seed(SEED)
	while LENGTH >= 40 :
		Number = random.randint(40 , 80)
		Save.append(Number)
		LENGTH -= Number
	Save.append(LENGTH)
	return CONTENT
#计算丢包率
def Coculate(AllCount , LostCount) :
	return LostCount / AllCount		
HOST = sys.argv[1]
PORT = int(sys.argv[2])
SEED = int(sys.argv[3])
STUDENTID = 2201
ENCRYPTION = STUDENTID ^ 0x5A3C  				#encryption是加密的意思
TEXTNAME = 'client发送文件.txt'
Save = []
MESSEGE = SentText(TEXTNAME)
AllNumber = len(Save)
AllLength = len(MESSEGE)
clientsocket = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
clientsocket.settimeout(1.0)
TargetAddress = (HOST , PORT)
AllCount = 0
LostCount = 0
RTT = []
while True : 
	#首先将要发的文件的总大小以及Start列表发送，这个必须要得到答复   types = 1
	Hello =struct.pack('>BHH' , 1 , ENCRYPTION , AllLength) + json.dumps(Save).encode('utf-8')
	while 1:
		clientsocket.sendto(Hello , TargetAddress)
		Begin = time.perf_counter()
		AllCount += 1
		try:
			BackWords = clientsocket.recvfrom(1024)[0]
			if BackWords == b'' :
				LostCount += 1
				continue
		#在收到回答（types == 2）后开始进行正常对话
			else :
				Types , Add , Length = struct.unpack('>BHH' , BackWords[0:5])
				if Types == 2 :
					Stop = time.perf_counter()
					RTT.append(Stop - Begin)
					print('！！！已将要发送的列表段发送成功！！！')
					print('总共有' , AllNumber  , '个字段')
					break
		except Exception as e:
			LostCount += 1
			continue
	#进行正常对话 ,发送的types == 3	，报文格式是types（1） +加密(2) +  块号（1） + 发送的数据量（2）+ 数据     types == 4确认信号
	Now = 0	
	End = 0	
	while AllNumber :
		Start = End
		End = Start + Save[Now]
		Messege = struct.pack('>BHBH' , 3 , ENCRYPTION , Now + 1 , Save[Now] ) + MESSEGE[Start : End].encode('utf-8')
		clientsocket.sendto(Messege , TargetAddress)
		print(f'第\033[32m{Now + 1}\033[0m个报文段\033[32m客户端已发送\033[0m ，字节数为【{Save[Now]}】  , 范围是【{Start + 1}~{End}】')
		AllCount += 1
		Begin = time.perf_counter()
		try:
			GetMessege = clientsocket.recvfrom(1024)[0]
			if   GetMessege == b'' :
				LostCount += 1
			else :
				Types , Add , Block = struct.unpack('>BHB' , GetMessege[0:4])
				if  Types == 4 :
					Stop = time.perf_counter()
					RTT.append(Stop - Begin)
					print("RTT是：" , Stop - Begin)
		except Exception as e:	
			LostCount += 1
		AllNumber -= 1
		Now += 1
	#接下来进行补发代码，收到的补发信号是types == 5 ，返回的类型是types == 6 ，确认信号types == 7 ，关闭信号是types == 8 
	#先发送types == 9 ， 确认让server端直接发送请求，需要得到返回值types == 10
	Messege = struct.pack('>BH' , 9 , ENCRYPTION)  
	while 1:
		clientsocket.sendto(Messege , TargetAddress)
		Begin = time.perf_counter()
		AllCount += 1
		try : 
			Data , Address = clientsocket.recvfrom(1024)
			Stop = time.perf_counter()
			if Stop - Begin > 0.3 :
				LostCount += 1
			if struct.unpack('>B' , Data[0:1])[0] == 10 :
				RTT.append(Stop - Begin)
				break
		except Exception as e :
			LostCount += 1
	while True : 
		try:
			BackMessege = clientsocket.recvfrom(1024)[0]
			Types = struct.unpack('>B' , BackMessege[0:1])[0]
			if Types == 5 :    														#补发信号的报文是types（1） + Add(加密后的学号) + block（1）
				Add , Block = struct.unpack('>HB' , BackMessege[1:4])
				Start = sum(Save[0 : Block - 1])
				End = Start + Save[Block - 1]						#返回信号的报文是types(1)+Add(加密后的学号)+block(1)+ Length(2) + data
				Messege = struct.pack('>BHBH' , 6 , ENCRYPTION , Block , Save[Block - 1]) + MESSEGE[Start:End].encode('utf-8') 
				clientsocket.sendto(Messege , TargetAddress)
				AllCount += 1
				print(f'第\033[31m{Block}\033[0m个报文段\033[31m客户端已重发\033[0m ，字节数为【{Save[Block - 1]}】  , 范围是【{Start + 1}~{End}】')
				Begin = time.perf_counter()
				try:
					GetMessege = clientsocket.recvfrom(1024)[0]
					if	GetMessege == b'':
						LostCount += 1
					else :
						Types , Add , Block = struct.unpack('>BHB' , GetMessege[0:4])
						if Types == 7 :
							Stop = time.perf_counter()
							TimeSub = Stop - Begin
							if TimeSub > 0.3 :
								LostCount += 1
							else :
								RTT.append(TimeSub)
				except Exception as e:
					LostCount += 1
					continue
			elif Types == 8:
				clientsocket.sendto(struct.pack('>BH' , 11 , ENCRYPTION) , Address)
				clientsocket.sendto(struct.pack('>BH' , 11 , ENCRYPTION) , Address)
				break
		except Exception as e:
			LostCount += 1
			continue
	break
Data = pd.Series(RTT)
print(f'本次的丢包率是：\033[34m{Coculate(AllCount , LostCount):.4f}\033[0m ')
print(f'本次RTT最小值是\033[32m{Data.min():.4f}\033[0m，最大值是\033[32m{Data.max():.4f}\033[0m , 平均值是\033[32m{Data.mean():.4f}\033[0m , 标准值是\033[32m{Data.std():.4f}\033[0m')