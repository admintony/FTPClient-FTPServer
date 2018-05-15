Author = "AdminTony"
Blog = "http://www.admintony.com"

"""
    功能实现：
     监听端口 -> 客户端连接  -> 打开一个线程和客户端通信
         |-------<<<<<<<<<<<<<<<<<<<<<<-------|
    
    与客户端通信的线程设计：
     接收客户端传递来的指令 -> 判断指令是否正确 -> subproess执行指令 -> 返回数据
     接收客户端指令用线程实现，用Queue来进行线程间的通讯
    
    检验帐号密码功能：
     从sqlite中查询用户名和密码，如果符合则登录，并发送欢迎语，若不符合则提示登录失败
"""

import sys,socket,threading,queue,subprocess
import base64
import platform
import re

"""
    设置FTP目录
"""

ftpPath = r'f:\ftproot'

def recvCommad(sock,addr):
    print("[+] 用户：{} 已上线".format(addr))
    while True:
        buffer = []
        try:
            data = sock.recv(1024)
        except Exception as e:
            print("[+] 用户：{}已下线".format(addr))
            return 0
        data = base64.b64decode(data)
        #print(data)
        data = data.decode()
        if data == "":
            continue
        print("[+] 接收到命令：{}".format(data))
        if "put" in data:
            #print(1)
            try:
                cmd = data.split(" ")
            except:
                sock.send(base64.b64encode(bytes("[-] 命令错误，请检查", encoding="gb2312")))
            with open(ftpPath+"\\"+cmd[1],"wb") as f:
                data = sock.recv(2048000)
                data = base64.b64decode(data)
                f.write(data)
            sock.send(base64.b64encode(bytes("[-] 文件上传成功!", encoding="gb2312")))
        else:
            execCommad(sock, data)
        if data == "bye":
            print("[+] 用户：{}已下线".format(addr))
            break

def execCommad(sock,command):
    global ftpPath
    os_ = platform.system()
    if command == "ls":
        if os_ == "Windows":
            command = "dir {}".format(ftpPath)
        else:
            command = "ls {}".format(ftpPath)
        su = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        STDOUT,STDERR = su.communicate()
        result = base64.b64encode(STDOUT)
        try:
            sock.send(result)
        except:
            pass
    elif "get" in command:
        try:
            cmd = command.split(" ")
        except:
            sock.send(base64.b64encode(bytes("[-] 命令错误，请检查",encoding="gb2312")))
            return
        try:
            with open(ftpPath+"\\"+cmd[1],"rb") as f:
                sock.send(base64.b64encode(bytes("file",encoding="gb2312")))
                d = f.read()
                sock.sendall(base64.b64encode(d))
                #sock.send(b'')
        except Exception as e:
            print(e)
            sock.send(base64.b64encode(bytes("[-] 文件不存在", encoding="gb2312")))

    elif command == "bye":
        try:
            sock.send(base64.b64encode(bytes("bye",encoding="utf-8")))
        except:
            pass
    elif command == "pwd":
        try:
            sock.send(base64.b64encode(bytes(ftpPath,encoding="utf-8")))
        except:
            pass
    elif "cd" in command:
        try:
            cmd = command.split(" ")
        except:
            sock.send(base64.b64encode(bytes("[-] 命令错误，请检查",encoding="gb2312")))
            return
        if cmd[1]!="..":
            ftpPath = ftpPath+"\\"+cmd[1]
        else:
            re_ = re.compile(r'(\w:(?:\\\w+)*)(?:\\\w+)')
            list = re_.findall(ftpPath)
            print(list)
            ftpPath = list[0]

        sock.send(base64.b64encode(bytes("[+] 目录跳转成功："+ftpPath, encoding="gb2312")))
    else:
        try:
            sock.send(base64.b64encode(bytes("命令错误，请检查",encoding="gb2312")))
        except:
            pass
def main():

    print("""$$$$$$$$\ $$$$$$$$\ $$$$$$$\   $$$$$$\                                                    
$$  _____|\__$$  __|$$  __$$\ $$  __$$\                                                   
$$ |         $$ |   $$ |  $$ |$$ /  \__| $$$$$$\   $$$$$$\ $$\    $$\  $$$$$$\   $$$$$$\  
$$$$$\       $$ |   $$$$$$$  |\$$$$$$\  $$  __$$\ $$  __$$\\$$\  $$  |$$  __$$\ $$  __$$\ 
$$  __|      $$ |   $$  ____/  \____$$\ $$$$$$$$ |$$ |  \__|\$$\$$  / $$$$$$$$ |$$ |  \__|
$$ |         $$ |   $$ |      $$\   $$ |$$   ____|$$ |       \$$$  /  $$   ____|$$ |      
$$ |         $$ |   $$ |      \$$$$$$  |\$$$$$$$\ $$ |        \$  /   \$$$$$$$\ $$ |      
\__|         \__|   \__|       \______/  \_______|\__|         \_/     \_______|\__|      
                                                                                    
    """)

    # 打开套接字
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1',21))
        s.listen(15)
    except Exception as e:
        print(e)
        sys.exit()
    print("[+] 等待客户端连接...")
    q = queue.Queue()
    while True:
        sock,addr = s.accept()
        thread = threading.Thread(target=recvCommad,args=(sock,addr))
        thread.start()


if __name__ == '__main__':
    main()