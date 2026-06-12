import socket
import random       #我要实现从lmax和lmin范围内的随机取数
import sys               #我要实现从终端读取HOST , PORT , lmax，lmin，seed ,文件名的值
import struct      
from datetime import datetime
def SaveMessege(Messege) :
	now = datetime.now()
	with open('client记录.txt' , 'a' , encoding = 'ascii') as f :
		f.write('[Time is]' + str(now) + '[Get Messege]' + Messege + '\n')
HOST  = sys.argv[1]
PORT  = int(sys.argv[2])
lmin = int(sys.argv[3])
lmax = int(sys.argv[4])
Seed = int(sys.argv[5])
TextName  = sys.argv[6]
clientsocket  =  socket.socket(socket.AF_INET , socket.SOCK_STREAM)
clientsocket.connect( (HOST , PORT) )

with open(TextName , 'r' ,encoding = 'ascii') as f:
	text = f.read()
NUMBER = len(text)
length = NUMBER
random.seed(Seed)
Save = []
while   length >= lmin :
	a = random.randint(lmin , lmax)
	Save.append(a)
	length -= a
Save.append(length)

times = len(Save)
Hello = struct.pack('>HI' , 1 , times)  					#步骤一，SayHello
while 1 :
	clientsocket.send(Hello)
	Agree = clientsocket.recv(2)     					#步骤二，Agree
	Types = struct.unpack('>H' , Agree)[0]
	if Types == 2 :
		print('牵手成功！！！!')
		break
	else :
		continue
Now = 0                               							 #步骤三，开始一问一答环节
End = 0
while times:
	times -= 1
	Start = End
	End = Start + Save[Now]
	A = text[Start:End]
	data = struct.pack('>HI' , 3 , Save[Now]) + A.encode('ascii')
	clientsocket.send(data)
	BackData = clientsocket.recv(6)
	Types , Length = struct.unpack('>HI' , BackData)
	if	Types != 4 or Length != Save[Now]:
		print('！！！数据有误！！！')
	BackData = clientsocket.recv(1024)
	if BackData != b'' :
		COUT = BackData.decode('ascii')
		SaveMessege(str(COUT))
		print(f'第\033[31m{Now + 1}\033[0m次\033[33m返回的反转后的信息是：\033[0m {COUT}')

	else :
		print('\033[31m连接断开了，请重连……\033[0m')
	Now += 1	
clientsocket.close()