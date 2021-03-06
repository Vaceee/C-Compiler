from tool import *
import time

class Grammar():
    """ LR（1）语法 """

    def __init__(self):
        self.start_symbol = ''
        self.productions = []
        self.firstSet = {}
        self.followSet = {}
        self.terminals = []
        self.nonterminals = []

    def load_grammar(self, path):
        i = 0
        for line in open(path, encoding='utf-8'):
            if '->' not in line:
                continue
            parts = line.split('->')
            left, right = parts[0].rstrip(), parts[1].strip().split(' ')
            if left[0] == '#':  # 在文件中加入的定义符号
                continue
            production = Production(left, right)
            production.index = i
            i += 1
            self.productions.append(production)
            if self.start_symbol == '':  # 第一个产生式
                self.start_symbol = left

    def setNonterminals(self):
        for p in self.productions:
            if p.left not in self.nonterminals:
                self.nonterminals.append(p.left)

    def setTerminals(self):
        for p in self.productions:
            for item in p.right:
                if item not in self.nonterminals and item not in self.terminals:
                    self.terminals.append(item)

    def isNullable(self, symbol):  # 该算法假设文法中所有可空字符都是直接可空的，不存在传递可空
        for p in self.productions:
            if p.left == symbol and '$' in p.right:
                return True
        return False

    def first(self):
        for symbol in self.terminals:
            self.firstSet[symbol] = [symbol]  # 处理终结符，因为可以推出a->a，因此做如此处理
        for symbol in self.nonterminals:
            self.firstSet[symbol] = []
        flag = True
        while flag:
            flag = False  # flag值改变说明这一遍扫描加入了新的符号
            for p in self.productions:
                # 遍历p的右部
                for part in p.right:
                    if part != '$':
                        for item in self.firstSet[part]:  # 对应于A->aB的情况
                            if item not in self.firstSet[p.left]:
                                self.firstSet[p.left].append(item)
                                flag = True
                    if part == '$':
                        if '$' not in self.firstSet[p.left]:  # 对应于epsillon包含在first集中的情况
                            self.firstSet[p.left].append('$')
                            flag = True
                    # 如果当前字符可空，first集应包含后续首字符的first，一直可空就一直往后看
                    if not self.isNullable(part):  # 对应于A->BC，但B导出空的情况
                        break

    def follow(self):
        for symbol in self.nonterminals:
            self.followSet[symbol] = []
        self.followSet[self.start_symbol].append('#')  # 开始符号的follow集应有#
        flag = True
        while flag:  # 每次都需要添加新的元素
            flag = False
            for p in self.productions:
                for i in range(len(p.right)):  # 遍历当前产生式的每个右部
                    part = p.right[i]  # 产生式p的第i个右部
                    if part not in self.nonterminals:  # 只处理非终结符
                        continue
                    allNullable = True  # part的下一元素的first集包含在part的follow集中
                    for j in range(i + 1, len(p.right)):  # 遍历第i个右部的后面的元素
                        for item in self.firstSet[p.right[j]]:  # 对应情况A->BC,把first(C)加到follow(B)中
                            if item not in self.followSet[part]:
                                self.followSet[part].append(item)
                                flag = True  # 说明这一趟有新的收获
                        if not self.isNullable(p.right[j]):
                            allNullable = False
                            break
                    if allNullable:  # 说明当前产生式右部的第i个元素后面的每一个元素都可导出空
                        for item in self.followSet[p.left]: # 对应情况A->B，把follow(A)加到follow(B)中
                            if item not in self.followSet[part]:
                                self.followSet[part].append(item)
                                flag = True

    def viewProductions(self):
        print("Productions of the grammar:")
        for p in self.productions:
            print(p.index, p.left, p.right)

    def viewFirst(self):  # 查看文法对应的first集
        f = open('./output/First.txt', 'w')
        # print("First Set of the grammar:")
        f.write("First Set of the grammar:\n")
        for k, v in self.firstSet.items():
            string = str(k) + str("\t") + str(v) + "\n"
            f.write(string)
            # print(k, v)
        f.close()

    def viewFollow(self):  # 查看文法对应的follow集
        f = open('./output/Follow.txt', 'w')
        # print("Follow Set of the grammar:")
        f.write("Follow Set of the grammar:")
        for k, v in self.followSet.items():
            string = str(k) + str("\t") + str(v) + "\n"
            f.write(string)
            # print(k, v)
        f.close()

    def configure(self, path):
        print('开始构建Follow集和First集...\n')
        t = time.time()
        self.load_grammar(path)
        self.setNonterminals()
        self.setTerminals()
        self.first()
        self.follow()
        self.viewFirst()
        self.viewFollow()
        print('First集和Follow集构建完成，结果存放在output文件夹中的First.txt和Follow.txt中，用时', '{:.4f}s\n'.format((time.time() - t)))

        # self.viewProductions()