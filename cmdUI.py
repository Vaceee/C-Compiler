from grammar import *
from lexer import *
from Parser import *


class cmdUI():
    def __init__(self):
        self.L = Lexer()
        self.G = Grammar()
        self.P = Parser()
        self.op = ''

    def lex_analysis(self, file):
        self.L = Lexer()
        if file == '':
            file = 'Code.txt'

        try:
            self.L.configure('./grammar&code/' + file)

        except Exception as e:
            print(e)

    def grammar_analysis(self, file):
        self.G = Grammar()
        if file == '':
            file = 'Grammar.txt'

        try:
            self.G.configure('./grammar&code/' + file)
            self.P.configure(self.G)
            self.P.update_parse()

        except Exception as e:
            print(e)

    def entrance(self):
        while True:
            print('0、输入"-s"，自动读取“grammar&code”文件夹下的“Code.txt”文件和“Grammar.txt”文件进行词法分析和语法分析\n'
                  '1、输入”-lex 文件名“进行词法分析，若不加文件名，则自动读取“grammar&code”文件夹下的“Code.txt”文件\n'
                  '2、输入”-grammar 文件名“进行语法分析，若不加文件名，则自动读取“grammar&code”文件夹下的“Grammar.txt”文件\n'
                  '3、输入"-parse" 进行代码解析，输入此指令之前请确保完成了词法分析和语法分析\n'
                  '4、输入-q，退出程序')

            In = input().split()
            while not In:
                In = input().split()

            if len(In) == 1:
                op = In[0]
                file = ''
            else:
                op = In[0]
                file = In[1]

            if op == '-s':
                self.lex_analysis(file)
                self.grammar_analysis(file)
            elif op == '-lex':
                self.lex_analysis(file)
            elif op == '-grammar':
                self.grammar_analysis(file)
            elif op =='-parse':
                self.P.parse(self.L.output)
            elif op == '-q':
                break
            else:
                pass
