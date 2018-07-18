def set_level(level):
    def set_fun(func):
        print('正在装饰中')
        def call_func(*args,**kwargs):
            if level == 1:
                print('正在进行手势安全验证。。。。')
            elif level == 2:
                print('正在进行短信安全验证。。。。')
            return func(*args,**kwargs)
        return call_func
    return set_fun


@set_level(2)
def pay():
    print('---paying---')

@set_level(1)
def login():
    print('---logining---')

login()
pay()