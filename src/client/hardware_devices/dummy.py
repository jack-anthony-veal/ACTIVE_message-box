class Dummy:
    def __geattr__(self, name):
        def foo(*args, **kwargs):
            print(f'{name} called with args: {args} and kwargs: {kwargs}')
            return
        return foo
    
    def __call__(self, name, *args, **kwargs):
        print(f'{name} called with args: {args} and kwargs: {kwargs}')
        return "hi"
    
    def __bool__(self):
        return True
    
    def __str__(self):
        print("str call")
        return "hi"
    
    def __int__(self):
        print("int call")
        return 1
    
    def __float__(self):
        print("float call")
        return 1.21