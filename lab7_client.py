Author = "AdminTony"
Blog = "http://www.admintony.com"

"""
    实现FTP客户端：
     1.端口处理，如果没有写端口则按照默认端口21处理
     2.打开套接字->连接客户端->启动线程专门接收打印客户端发送的信息->接收用户输入的指令
       ->进行base64编码后发送给服务端
"""

import socket,sys,threading
import base64,time

def main():
    print("""$$$$$$$$\       $$$$$$$$\       $$$$$$$\         $$$$$$\        $$\             $$\                                         $$\     
$$  _____|      \__$$  __|      $$  __$$\       $$  __$$\       $$ |            \__|                                        $$ |    
$$ |               $$ |         $$ |  $$ |      $$ /  \__|      $$ |            $$\        $$$$$$\        $$$$$$$\        $$$$$$\   
$$$$$\             $$ |         $$$$$$$  |      $$ |            $$ |            $$ |      $$  __$$\       $$  __$$\       \_$$  _|  
$$  __|            $$ |         $$  ____/       $$ |            $$ |            $$ |      $$$$$$$$ |      $$ |  $$ |        $$ |    
$$ |               $$ |         $$ |            $$ |  $$\       $$ |            $$ |      $$   ____|      $$ |  $$ |        $$ |$$\ 
$$ |               $$ |         $$ |            \$$$$$$  |      $$$$$$$$\       $$ |      \$$$$$$$\       $$ |  $$ |        \$$$$  |
\__|               \__|         \__|             \______/       \________|      \__|       \_______|      \__|  \__|         \____/""")
    print()
    # 检测参数是否正确
    if (len(sys.argv) != 2):
        print("Useage: {} IP[:Port]".format(sys.argv[0]))
        sys.exit()
    # 处理参数
    addr = sys.argv[1].split(":")
    if(len(addr)==1):
        addr.append(21)
    else:
        addr[1] = int(addr[1])

    # 打开套接字
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except Exception as e:
        # 打印异常
        print(e)
        sys.exit()

    # 连接服务端
    try:
        s.connect((addr[0],addr[1]))
    except Exception as e :
        print(e)
        sys.exit()


    while(True):
        comand = input("[+] 请输入指令： ")
        cmdTemp = comand
        # 进行一下base64编码然后发给服务端，判断数据是否为bye
        comand = base64.b64encode(bytes(comand,encoding="utf-8"))
        #print(comand)
        s.send(comand)

        """
        put 指令
        """
        if "put" in cmdTemp:
            try:
                cmd = cmdTemp.split(" ")
            except:
                print("[-] 指令错误，请检查..")
                continue
            with open(cmd[1],"rb") as f:
                d = f.read()
                d = base64.b64encode(d)
                s.send(d)

        """
        接收信息
        """

        d = s.recv(1024)
        data = base64.b64decode(d)
        data = data.decode("gb2312")
        if data == "bye":
            break
        elif data == "file":
            cmd = cmdTemp.split(" ")
            # 接收数据:

            data = s.recv(20480000)
            data = base64.b64decode(data)
            with open(cmd[1],"wb") as f:
                f.write(data)
            print("[+] 文件 {} 下载成功！".format(cmd[1]))
        else:
            print("[+] 从服务器端接收到数据：\n{}".format(data))



        # 退出程序
        if comand == base64.b64encode(bytes("bye",encoding="utf-8")):
            sys.exit()

if __name__ == '__main__':
    main()