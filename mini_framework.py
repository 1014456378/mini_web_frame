import re
from pymysql import connect
from urllib import parse
g_path_func = {}
#定义装饰器函数
#路由器
def route(path):
    def set_dun(func):
        g_path_func[path] = func
        def call_func(*args,**kwargs):
            func(*args,**kwargs)
        return call_func
    return set_dun

@route(r'/index.html')
def index(*args,**kwargs):
    #1.打开xx.html文件充当模板
    with open('./templates/index.html',encoding='utf-8') as f:
            content = f.read()
    #2.查询mysql的数据
    conn = connect(host='localhost', user='root', password="mysql",
                 database='stock_project', port=3306,charset='utf8')
    cur = conn.cursor()
    sql = 'select * from info;'
    cur.execute(sql)
    ret = cur.fetchall()
    html_templates = """
                        <tr>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>
                                <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
                            </td>
                        </tr>
    """
    dynamic_data = ''
    for item in ret:
        i = (item[1],)
        j = item + i
        dynamic_data += html_templates % j
    print(type(item[0]))
    content = re.sub(r'{%content%}', dynamic_data, content)
    cur.close()
    conn.close()
    return content
@route(r'/center.html')
def center(*args,**kwargs):
    # 1.打开xx.html文件充当模板
    with open('./templates/center.html', encoding='utf-8') as f:
        content = f.read()
    # 2.查询mysql的数据
    conn = connect(host='localhost', user='root', password="mysql",
                   database='stock_project', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = 'select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i INNER join focus as f where i.id = f.info_id;'
    cur.execute(sql)
    ret = cur.fetchall()
    html_templates = """
                       <tr>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>%s</td>
                           <td>
                               <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
                           </td>
                           <td>
                               <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
                           </td>
                       </tr>
       """
    dynamic_data = ''
    for item in ret:
        i = (item[0],item[0])
        j = item + i
        dynamic_data += html_templates % j
    content = re.sub(r'{%content%}', dynamic_data, content)
    cur.close()
    conn.close()
    return content
@route(r'/add/([\d]{6})\.html')
def add(*args,**kwargs):
    file_path = args[0]
    pattern = args[1]
    ret = re.match(pattern,file_path)
    code = ret.group(1)
    conn = connect(host='localhost', user='root', password="mysql",
                   database='stock_project', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = 'select * from focus where info_id = (select id from info where code = %s);'
    ret = cur.execute(sql,[code])
    if ret > 0 :
        cur.close()
        conn.close()
        return '请不要重复关注'
    sql = 'insert into focus (info_id) select id from info where code = %s;'
    cur.execute(sql,[code])
    conn.commit()
    cur.close()
    conn.close()
    return '关注%s成功' %code
@route(r'/del/([\d]{6})\.html')
def delate(*args,**kwargs):
    file_path = args[0]
    pattern = args[1]
    ret = re.match(pattern, file_path)
    code = ret.group(1)
    conn = connect(host='localhost', user='root', password="mysql",
                   database='stock_project', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = 'delete from focus where info_id = (select id from info where code = %s)'
    cur.execute(sql, [code])
    conn.commit()
    cur.close()
    conn.close()
    return '取消关注%s成功' % code
@route(r'/update/([\d]{6})\.html')
def update_page(*args,**kwargs):
    file_path = args[0]
    patter = args[1]
    ret = re.match(patter,file_path)
    code = ret.group(1)
    with open('./templates/update.html',encoding='utf-8') as f:
        content = f.read()
    conn = connect(host='localhost', user='root', password="mysql",
                   database='stock_project', port=3306, charset='utf8')
    cur = conn.cursor()
    sql = 'select note_info from focus where info_id = (select id from info where code = %s)'
    cur.execute(sql,[code])
    ret = cur.fetchone()
    note_info = ret[0]
    content = re.sub(r'\{%code%\}',code,content)
    content = re.sub(r'\{%note_info%\}', note_info, content)
    cur.close()
    conn.close()
    return content
@route(r'/update/([\d]{6})/(.*)\.html')
def update_noteinfo(*args,**kwargs):
    file_path = args[0]
    patter = args[1]
    ret = re.match(patter, file_path)
    code = ret.group(1)
    note_info = ret.group(2)
    note_info = parse.unquote(note_info)
    sql = 'update focus set note_info = %s where info_id = (select id from info where code = %s)'
    conn = connect(host='localhost', user='root', password="mysql",
                   database='stock_project', port=3306, charset='utf8')
    cur = conn.cursor()
    cur.execute(sql, [note_info,code])
    conn.commit()
    cur.close()
    conn.close()
    return '更新成功'

#对外提供通用调用接口
def application(environ,start_response):
    file_path = environ['PATH_INFO']
    for pattern,func in g_path_func.items():
        ret = re.match(pattern,file_path)
        if ret:
            start_response('200 OK', [('Content_Type', 'text/html;charset=utf-8'), ('Framework-Version', 'Flask v1.1')])
            return func(file_path,pattern)
    else:
        start_response('404 Not Found', [('Content_Type', 'text/html'), ('Framework-Version', 'Flask v1.1')])
        resp_body = '<h1>404</h1>'
        return resp_body

