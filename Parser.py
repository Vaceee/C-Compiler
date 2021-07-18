from tool import *
import collections
import pickle
import time
from graphviz import Digraph


class Node:

    def __init__(self, item=""):
        self.value = item
        self.children = []


class Parser():
    """ LR1 分析方法 """

    def __init__(self):
        self.start_symbol = ''
        self.productions = []
        self.first_set = {}
        self.followSet = {}
        self.terminals = []
        self.nonterminals = []
        self.automata = []
        self.action_dict = collections.defaultdict(dict)
        self.goto_dict = collections.defaultdict(dict)
        self.root = ''
        self.reduce_stack = []
        self.grammar_tree = Node()

    def build_automata(self):

        start_state = [Item(self.start_symbol + "'", ['.', self.start_symbol], '#')]  # 初始状态S'->·S,#
        automata = [self.closure(start_state)]  # 自动机存储的单元是一个闭包
        flag = True
        while flag:
            flag = False
            for state in automata:
                for symbol in self.nonterminals + self.terminals:
                    new_state = self.goto(state, symbol)  # 检查是否有合法的状态转移方法
                    if len(new_state) == 0:
                        continue
                    if new_state not in automata:
                        automata.append(new_state)
                        flag = True
        self.automata = automata

    def closure(self, itemset):

        for item in itemset:
            right = item.right
            index = right.index('.')
            var = len(right) - index - 1  # ·号后面的字符串长度
            if var == 0:
                continue  # 应该归约，不需要继续运算
            symbol = right[index + 1]
            for p in self.productions:
                if p.left != symbol:
                    continue
                if var == 1:  # 如果是A->·B的形式
                    lookahead = item.lookahead
                    if type(lookahead) is not list:
                        lookahead = [lookahead]
                else:
                    lookahead = []
                    flag = True
                    for v in range(index + 2, index + var + 1):  # A->·BCD，考虑CD
                        terminal = right[v]
                        first = self.first_set[terminal]
                        for each in first:
                            if each not in lookahead and each != '$':
                                lookahead.append(each)
                        if '$' not in first:  # A->·BCD，若C可以推出空，继续考虑D
                            flag = False
                            break
                    if flag is True:  # A->·BCD，若CD都可以推出空，则加入#
                        lookahead.append('#')
                new_right = ['.'] + p.right
                for terminal in lookahead:
                    new_item = Item(p.left, new_right, terminal)
                    if new_item not in itemset:
                        itemset.append(new_item)
        return itemset

    def goto(self, itemset, symbol):

        new_state = []
        for item in itemset:
            right = item.right
            index = right.index('.')
            if index == len(right) - 1 or right[1] == '$':  # 遇到了转移到空或者应该规约的情况
                continue
            if right[index + 1] == symbol:
                new_right = right.copy()
                new_right[index], new_right[index + 1] = new_right[index + 1], new_right[index]  # A->·BC换成了A->B·C
                item = Item(item.left, new_right, item.lookahead)
                new_state.append(item)
        new_state = self.closure(new_state)
        return new_state

    def fill_table(self):
        action_dict, goto_dict = collections.defaultdict(dict), collections.defaultdict(dict)
        terms = self.terminals + ['#']
        for i in range(len(self.automata)):  # 终结符的转移表
            for symbol in terms:
                shiftable = []
                for item in self.automata[i]:
                    right = item.right
                    index = right.index('.')

                    if index == len(right) - 1:  # A->B·应该归约
                        if symbol == item.lookahead and item.left != self.start_symbol + "'":  # 找到了符合的语法
                            right = item.right.copy()
                            right.pop(right.index('.'))
                            action_dict[i][symbol] = DictEntry(action='r', left=item.left, right=right)

                        if item.left == self.start_symbol + "'":  # S'->S·此时为接受状态
                            action_dict[i]['#'] = DictEntry(action='acc')
                        continue

                    if right[index + 1] == '$' and symbol == item.lookahead:  # A->·,c的形式，即有空转移
                        right = item.right.copy()
                        right.pop(right.index('.'))
                        action_dict[i][symbol] = DictEntry(action='r', left=item.left, right=right)
                        continue

                    if right[index + 1] == symbol and right[index + 1] != '$':  # 该字符可以进行移进操作
                        shiftable.append(right[index + 1])

                if len(shiftable) != 0:  # 考察移进后的状态
                    goto_state = self.goto(self.automata[i], symbol)
                    index = self.automata.index(goto_state)
                    action_dict[i][symbol] = DictEntry(action='s', shift_state=index)

            for symbol in self.nonterminals:  # 非终结符的goto表
                goto_state = self.goto(self.automata[i], symbol)
                if goto_state in self.automata:
                    goto_index = self.automata.index(goto_state)
                    goto_dict[i][symbol] = DictEntry(goto_state=goto_index)
        self.action_dict = action_dict
        self.goto_dict = goto_dict

    def export_tables(self):

        f = open('./output/ActionTable.txt', 'w')
        for k, v in self.action_dict.items():
            for key, value in v.items():
                string = str(k) + "\t" + str(key) + "\t" + str(value.action) + "\t" + str(value.content) + "\n"
                f.write(string)

        f.close()

        f = open('./output/GotoTable.txt', 'w')
        for k, v in self.goto_dict.items():
            for key, value in v.items():
                string = str(k) + "\t" + str(key) + "\t" + str(value.content) + "\n"
                f.write(string)
        f.close()

        f = open('./output/action_dict', 'wb')
        pickle.dump(self.action_dict, f)
        f.close()

        f = open('./output/goto_dict', 'wb')
        pickle.dump(self.goto_dict, f)
        f.close()

    def load_tables(self):  # 用于提取出上次执行的程序的语法分析

        action_dict, goto_dict = collections.defaultdict(dict), collections.defaultdict(dict)

        f = open('./output/action_dict', 'rb')
        self.action_dict = pickle.load(f)
        f.close()

        f = open('./output/goto_dict', 'rb')
        self.goto_dict = pickle.load(f)
        f.close()

    def production_index(self, left, right):
        for p in self.productions:
            if p.left == left and p.right == right:
                return p.index

    def view_automata(self):  # 查看自动机的所有状态，显示其蕴含的项目
        i = 0
        f = open('./output/Automata.txt', 'w')
        for state in self.automata:
            # print(i)
            f.write(str(i) + "\t")
            for item in state:
                # print(item)
                string = str(item) + "\t"
                f.write(string)
            f.write("\n")
            i += 1
        f.close()

    def configure(self, grammar):

        self.productions = grammar.productions
        self.start_symbol = grammar.start_symbol
        self.nonterminals = grammar.nonterminals
        self.terminals = grammar.terminals
        self.first_set = grammar.firstSet
        self.followSet = grammar.followSet

    def parse(self, w):
        self.reduce_stack = []

        w.append(['#', '-', '-', 'end'])  # 在最后加一个#
        f = open('./output/Analysis_Result.txt', 'w')
        i, step, counter = 0, 0, 0
        state_stack, symbol_stack, forest, Slist, Dlist = [0], ['#'], [], [], []
        not_draw = 0
        while True:
            # Preprocess:
            # replace the identifiers with ID
            # replacet the numbers with NUM
            symbol = w[i][0]
            dtype = w[i][1]
            if dtype == 'NUM' or dtype == 'ID':
                symbol = w[i][1]
            f.write("Read symbol\t" + str(symbol) + '\n')
            top = state_stack[-1]

            if symbol not in self.action_dict[top]:
                print("Error at line", w[i][3], "no action")
                f.write("Error at line\t" + str(w[0][3]) + "\tno action\n")
                not_draw = 1
                break

            dict_entry = self.action_dict[top][symbol]
            action = dict_entry.action
            content = dict_entry.content

            if action is None:
                print("Error at line", w[i][3], "no action")
                f.write("Error at line\t" + str(w[0][3]) + "\tno action\n")
                not_draw = 1
                break

            if action == 's':  # take shift action
                state_index = content['shift_state']
                state_stack.append(state_index)
                symbol_stack.append(symbol)
                i += 1

                f.write("\t\tshift\t" + str(symbol) + "\tand push state\t" + str(state_index) + "\n")

            elif action == 'r':  # take reduce action
                left = content['left']
                right = content['right']
                self.reduce_stack.append(content)

                if right[0] == '$':  # reduce by epsilon production
                    state = self.goto_dict[state_stack[-1]][left].content['goto_state']
                    state_stack.append(state)

                    f.write("\t\treduce using the production\t" + str(left) + "->" + str(right) + "\n")
                    f.write("\t\tpush state\t" + str(state) + "\n")
                    f.write("\t\tState stack:\t" + str(state_stack) + "\n")
                    f.write("\t\tSymbol stack:\t" + str(symbol_stack) + "\n")

                    continue

                length = len(right)  # 作相对应长度的归约
                state_stack = state_stack[0:len(state_stack) - length]
                symbol_stack = symbol_stack[0:len(symbol_stack) - length]
                symbol_stack.append(left)

                state = self.goto_dict[state_stack[-1]][left].content['goto_state']
                state_stack.append(state)

                f.write("\t\treduce using the production\t" + str(left) + "->" + str(right) + "\n")
                f.write("\t\tpush state\t" + str(state) + "\n")

            elif action == 'acc':
                print("Accept")
                f.write("Accept!\n")
                break

            f.write("\t\tState stack:\t" + str(state_stack) + "\n")
            f.write("\t\tSymbol stack:\t" + str(symbol_stack) + "\n")
            step += 1

        if not_draw == 0:
            self.grammar_tree = Node(self.start_symbol)
            self.build_tree(self.grammar_tree)

            dot = Digraph(comment="GrammarTree", format="pdf", node_attr={'shape': 'box'})  # 定义绘图类对象
            dot.edge_attr.update(arrowhead='vee', arrowsize='1')
            dot.graph_attr['dpi'] = '150'
            dot.node(str(self.grammar_tree), self.grammar_tree.value)
            self.print_tree(self.grammar_tree, 1, dot)
            dot.render('./output/GrammarTree', view=True)
        else:
            raise Exception("解析错误，无法画出语法树")

        print("Finished in", step, "steps", '结果存储在output文件夹中的"Analysis_Result.txt"中')
        f.write("Finished in\t" + str(step) + "\tsteps\n")

    def build_tree(self, node):
        if node.value in self.nonterminals:
            # print("build tree",node.value,'\n')
            temp = self.reduce_stack.pop()
            action = temp['right']

            for item in action[::-1]:
                child = Node(item)
                node.children.append(child)
                self.build_tree(child)

    def print_tree(self, node, depth, dot):
        # print(" "*(depth)+"|--"+node.value)
        # for child in node.children[::-1]:
        #     self.print_tree(child,depth+1)

        for child in node.children[::-1]:
            dot.node(str(child), child.value)
            dot.edge(str(node), str(child))
            self.print_tree(child, depth + 1, dot)

    def update_parse(self):

        t = time.time()

        print('开始构建自动机...\n')
        self.build_automata()
        self.view_automata()
        print('自动机构建完成，结果保留在output文件夹中的Automata.txt'
              '用时', '{:.4f}s\n'.format((time.time() - t)))

        print('开始构建状态转移表...\n')
        t = time.time()
        self.build_automata()
        self.fill_table()
        self.export_tables()

        print('状态转移表构建完成，结果保留在output文件夹中的ActionTable.txt和GotoTable.txt中，'
              '用时', '{:.4f}s\n'.format((time.time() - t)))
