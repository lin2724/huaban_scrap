import ConfigParser
import os


class CfgParse(ConfigParser.ConfigParser):
    def __init__(self, cfg_file_path):
        ConfigParser.ConfigParser.__init__(self)
        self.cfg_file_path = cfg_file_path
        if not os.path.exists(cfg_file_path):
            print 'cfg file not exist'
            self.create_default_cfg()
        self.readfp(open(cfg_file_path))
        pass

    def create_default_cfg(self):
        print 'create default configure file'
        with open(self.cfg_file_path, 'w+') as fd:
            pass
        pass

    def fill_default_cfg(self, default_cfg):
        print 'fill cfg with default set'
        with open(self.cfg_file_path, 'w+') as fd:
            fd.write(default_cfg)
        self.readfp(open(self.cfg_file_path))

    def check_cfg_empty(self):
        with open(self.cfg_file_path, 'r') as fd:
            content = fd.read(1)
        if not len(content):
            return True
        return False
        pass
    pass


class ConColor:
    def __init__(self):
        pass
    Black = '\33[30m'
    Red = '\33[31m'
    Green = '\33[32m'
    Yellow = '\33[33m'
    Blue = '\33[34m'
    Magenta = '\33[35m'
    Cyan = '\33[36m'
    LightGray = '\33[37m'
    DarkGray = '\33[90m'
    LightRed = '\33[91m'
    LightGreen = '\33[92m'
    LightYellow = '\33[93m'
    LightBlue = '\33[94m'
    LightMagenta = '\33[95m'
    LightCyan = '\33[96m'
    White = '\33[97m'

    Underline = '\33[4m'
    Blink = '\33[5m'
    Reverse = '\33[7m'
    Hidden = '\33[8m'
    Reset = '\33[0m'
    ResetUnderline = '\33[24m'
    ResetBlink = '\33[25m'
    ResetReverse = '\33[27m'
    ResetHidden = '\33[28m'

    if os.name == 'nt':
        Black = ''
        Red = ''
        Green = ''
        Yellow = ''
        Blue = ''
        Magenta = ''
        Cyan = ''
        LightGray = ''
        DarkGray = ''
        LightRed = ''
        LightGreen = ''
        LightYellow = ''
        LightBlue = ''
        LightMagenta = ''
        LightCyan = ''
        White = ''

        Underline = ''
        Blink = ''
        Reverse = ''
        Hidden = ''
        Reset = ''
        ResetUnderline = ''
        ResetBlink = ''
        ResetReverse = ''
        ResetHidden = ''


class ConColorShow(ConColor):
    def __init__(self):
        pass
    
    def warning_show(self, str_info):
        print self.Red + str_info + self.Reset
        pass

    def highlight_show(self, str_info):
        print self.LightYellow + str_info + self.Reset
        pass

    def blink_show(self, str_info):
        print self.Blink + str_info + self.Reset
        pass

    def error_show(self, str_info):
        print self.LightRed + str_info + self.Reset
        pass

    def color_show(self, str_info, color):
        print color + str_info + self.Reset
        pass

    def common_show(self, str_info):
        print str_info


class MyArgParse:
    def __init__(self):
        self.OptionList = list()
        pass

    def __str__(self):
        info_list = str()
        for option_info in self.OptionList:
            info_list += '%15s    %s' % (option_info['option_str'], option_info['help_info'])
            info_list += '\n\r'
        return info_list
        pass

    def add_option(self, option_str, arg_num, help_info):
        option_info_dict = dict()
        option_info_dict['option_str'] = option_str
        if type(arg_num) != list:
            tmp_arg_num = arg_num
            arg_num = list()
            arg_num.append(tmp_arg_num)
        option_info_dict['arg_num_list'] = arg_num
        option_info_dict['help_info'] = help_info
        option_info_dict['arg_list'] = list()
        option_info_dict['set'] = False

        self.OptionList.append(option_info_dict)

        pass

    def check_arg_num_valid(self, arg_list, arg_num_list):
        arg_count = len(arg_list)
        valid_arg_count = 0
        for i in range(arg_count):
            if arg_list[i][:1] == '-':
                break
            valid_arg_count += 1
        for arg_num in arg_num_list:
            if valid_arg_count >= arg_num:
                return True
        return False
        pass

    def parse(self, arg_list):
        arg_i = 0
        valid_option_count = 0
        for arg in arg_list:
            for option_info in self.OptionList:
                if arg == option_info['option_str']:
                    if not self.check_arg_num_valid(arg_list[arg_i+1:], option_info['arg_num_list']):
                        ConColorShow().error_show('ERROR:option %s need %s args' % (option_info['option_str'], str(option_info['arg_num_list']) ))
                        print option_info['help_info']
                        return False
                    else:
                        arg_num = self.get_real_arg_num(arg_list[arg_i+1:], option_info['arg_num_list'])
                        print '%s real arg num %d' % (arg, arg_num)
                        option_info['arg_list'] = arg_list[arg_i+1:][:arg_num + 1]
                        option_info['set'] = True
                        valid_option_count += 1
            arg_i += 1
        return valid_option_count
        pass

    def get_real_arg_num(self, arg_list, arg_num_list):
        arg_count = len(arg_list)
        valid_arg_count = 0
        for i in range(arg_count):
            if arg_list[i][:1] == '-':
                break
            valid_arg_count += 1
        max_num_arg = 0
        for arg_num in arg_num_list:
            if valid_arg_count >= arg_num > max_num_arg:
                max_num_arg = arg_num

        return max_num_arg
        pass

    def check_option(self, option_str):
        for option_info in self.OptionList:
            if option_info['option_str'] == option_str:
                return option_info['set']

    def get_option_args(self, option_str):
        for option_info in self.OptionList:
            if option_info['option_str'] == option_str:
                if not option_info['set']:
                    ConColorShow().error_show('ERROR:option %s not set!' % option_str)
                return option_info['arg_list']
        ConColorShow().error_show('ERROR:option %s not found!' % option_str)
        pass

    def init_example(self):
        arg_parse = MyArgParse()
        arg_parse.add_option('-cp', 0, 'do copy from scan list')
        arg_parse.add_option('-d', [0,1], 'specific dir to scan')
        arg_parse.add_option('-t', 1, 'min time specific')
        arg_parse.add_option('-desc', 1, 'specific destination folder to copy')
        arg_parse.add_option('-p', 0, 'print default scan folder and des folder')
        return arg_parse
        pass


def get_dir_depth(dir_path):
    depth = 0
    if 'nt' == os.name:
        depth = dir_path.count('\\')
    else:
        depth = dir_path.count('/')
    if os.path.isabs(dir_path):
        depth -= 1
    return depth
    pass
