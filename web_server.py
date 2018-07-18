from gevent import monkey
import gevent
import socket  # 定义一个全局变量 叫做socket, 该对象指向了socket模块
import re
import sys
# import mini_framework
#apache nginx
# 不要使用这种方式导入from socket import * 否则无法破解socket
monkey.patch_all()  # 让列举的所有的阻塞操作都变成非阻塞
# 协程会榨干cpu计算力, 如果使用协程, 是不能够有阻塞操作
class Web_Server(object):
    def __init__(self, port,app):
        # 创建服务端的套接字对象
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定信息
        self.server_socket.bind(("", port))
        # 监听, 变成被动的套接字
        self.server_socket.listen(128)
        self.application = app
    def run(self):
        # 等待新的客户端连接
        while True:
            new_socket, addr = self.server_socket.accept()
            # 创建协程对象
            j1 = gevent.spawn(self.handle_req, new_socket)
            # j1.join() # join是阻塞操作, 等所有协程都执行完毕之后 再关闭主进程
        # 不会执行
        # server_socket.close()
    def handle_req(self,new_socket):
        # 根据具体的请求, 给浏览器返回不同的数据, 根据响应的报文格式: HTTP response格式
        recv_data = new_socket.recv(4096)
        # print("------%s------" % recv_data)
        if not recv_data:
            print("客户端已经下线了")
            # 关闭套接字
            new_socket.close()
            return
        # print(recv_data)  # 请求
        recv_data = recv_data.decode()
        # 需要获取请求行中的路径, 打开对应的文件
        data_list = recv_data.splitlines()
        # print(data_list)
        # 将字符串以\r\n按行切割 --> 列表  --> 列表的第0个元素
        req_line = data_list[0]  # GET /grand.html HTTP/1.1
        # 根据正则表达式来获取路径
        ret = re.match(r".* (.*) .*", req_line)
        # print(ret.group())
        file_path = ret.group(1)
        print("请求的资源路径:", file_path)
        # 根据获取的路径打开对应的文件即可   注意路径是/grand.html 需要拼接 ./static
        # 添加一个默认的首页: 当访问ip地址或者域名的时候没有资源路径就返回这个页面
        if file_path == "/":
            file_path = "/index.html"
        if file_path.endswith('.html'):
            #动态请求，返回动态数据
            info = {'PATH_INFO': file_path}
            resp_body = self.application(info, self.start_response)
            resp_headers = ''
            for item in self.response_headers:
                resp_headers += '%s:%s\r\n' %(item[0],item[1])
            resp_headers+= 'Server:BaiduWebServer/1.1\r\n'
            resp_headers+= '\r\n'
            resp_line = 'HTTP/1.1 %s\r\n' %self.status

            resp = resp_line + resp_headers + resp_body
            new_socket.send(resp.encode())
            new_socket.close()
        else:
            #静态请求
            try:
                file = open('./static' + file_path, "rb")
            except Exception as e:
                print("哎呦,出错啦 %s" % str(e))
                resp_body = str(e).encode()
                resp_line = "HTTP/1.1 404 Not Found\r\n"
                resp_headers = "Server: BaiduWebServer/1.1\r\n"
                resp_headers += "\r\n"
                # 拼接响应报文格式
                # resp = resp_line + resp_headers + resp_body
                # new_socket.send(resp.encode())
                # close
                # new_socket.close()  # 短连接
            else:
                # 没有异常, 正常
                resp_body = file.read()  # 二进制
                file.close()
                resp_line = "HTTP/1.1 200 OK\r\n"
                resp_headers = "Server: BaiduWebServer/1.1\r\n"
                resp_headers += "\r\n"
                # 拼接响应报文格式
                # resp = resp_line + resp_headers
                # new_socket.send(resp.encode() + resp_body)
                # close
                # new_socket.close()  # 短连接
                # TODO 待验证
                return  # 此处return 不会影响finally的执行
            finally:
                # 无论有没有异常都会执行
                print("我是一定要执行的代码")
                resp = resp_line + resp_headers
                new_socket.send(resp.encode() + resp_body)
                new_socket.close()
    def start_response(self,status,response_headers):
        self.status = status
        self.response_headers = response_headers
def main():
    print(sys.argv)

    if len(sys.argv) != 4:
        print("输入出正确参数个数")
        return

    port_str = sys.argv[1]   #在命令行输入相应参数
    if not port_str.isdigit():
        print("请输入合法的端口号")
        return
    module_name = sys.argv[2]
    method_name = sys.argv[3]
    #根据模块名导入具体模块对象
    mini_fw = __import__(module_name)
    #通过模块对象和函数名获取具体的函数对象
    app = getattr(mini_fw,method_name)
    print(app)
    port = int(port_str)
    # 做主要的流程控制
    # 启动服务器, 提供服务
    web_server = Web_Server(port,app)
    web_server.run()

if __name__ == '__main__':
    main()



"""
1. 浏览器需要发送具体的请求获取对应的数据 ex: http://127.0.0.1:9090/images/005.jpg -->  /images/005.jpg就是路径
2. 服务器收到浏览器的请求, 解析请求行 获取请求路径
3. 打开路径对应的文件
4. 将文件数据安装HTTP响应的报文格式发送给浏览器
5. 如果访问的资源是HTML文件, 并且在HTML文件中包含了一些资源(png,js,css)
6. 浏览器会自动发起请求, 请求资源文件
7. 浏览器获取到了需要的数据之后, 就是进行页面的渲染
"""


