class Debug:
    def __init__(self, debug=True):
         self.print_true = debug
    def DEBUG_PRINTLN(self, data, number=''):
        if self.print_true:
            debug_str = 'f DEBUG {number}: '
            data_type = type(data)
            if data_type == str:
                pass
            elif data_type == list:
                data_str = ''
                for line in data:
                    data_str = line + '\n'
                data = data_str
            elif data_type in (int, float, bool):
                data = str(data)
            elif data_type == dict:
                data = str(data)
            else:
                try:
                    data = data.json()
                except:
                    data = str(data)
            for line in data.split('\n'):
                print(line)
        return