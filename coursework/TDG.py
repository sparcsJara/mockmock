import astor
import ast
from io import StringIO
import sys
import contextlib
import os.path
from PDG import PDG
from BranchInfo import BranchInfo
import random
import signal

'''
TODO
- boolop for condition (1<2 and 2<3)
- branch distance for for-loop
- branch distance for while-else
- try statement support
- support for variable number of arguments
- too much workload
- int(float())-->float()

restriction
- only global function
- need function name using comment at the beginning of file
- only support if, for, while statements, and their bodies
- simple predicate (a op b)
- not actual random
'''

# test data generation class
class TDG:
    # initialize TDG instance
    def __init__(self, filename):
        # get filename of target code
        if not os.path.isfile(filename):
            print('Error : file <' + filename + '> does not exist.')
            exit()
        self.filename = filename

    def pre_instrument(self):
        root = astor.parse_file(self.filename)

        temp_file = open(self.filename)
        first_line = temp_file.readline()
        temp_file.close()
        if first_line[:20] == '# target_function = ' and len(first_line.split()) == 4:
            self.funcname = first_line.split()[3]
        else:
            print('ERROR : specify target function name in first lien of file')
            exit()

        f = None
        for stmt in root.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == self.funcname:
                f = stmt
                break
        else:
            print('ERROR : function <' + self.funcname + '> does not exist')
            exit()

        def dfs_pre_instrument(node):
            for info in astor.iter_node(node):
                if info[1] == 'body' or info[1] == 'orelse':
                    for stmt in info[0]:
                        if isinstance(stmt, ast.For) or isinstance(stmt, ast.If) or isinstance(stmt, ast.While):
                            if len(stmt.orelse) == 0:
                                stmt.orelse.append(ast.Pass())
                        dfs_pre_instrument(stmt)

        dfs_pre_instrument(f)

        instrumented_file = open('pre_' + self.filename, 'w')
        instrumented_file.write(astor.to_source(root))
        instrumented_file.close()

    



    # instrument code and save file as instrumented_filename.py
    def instrument(self):
        # find target function name
        #temp_file = open('pre_' + self.filename)
        #first_line = temp_file.readline()
        #temp_file.close()

        #if first_line[:20] == '# target_function = ' and len(first_line.split()) == 4:
        #    self.funcname = first_line.split()[3]
        #else:
        #    print('ERROR : specify target function name in first lien of file')
        #    exit()

        # construct AST
        root = astor.parse_file('pre_' + self.filename)

        # find function definition
        f = None
        for stmt in root.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == self.funcname:
                f = stmt
                break
        else:
            print('ERROR : function <' + self.funcname + '> does not exist')
            exit()

        # find argument number
        self.funcargs = len(f.args.args)

        # instrumenting

        # DFS code and instrument
        # 1. find if, for, and while statements,
        # 2. insert print(T/F is executed)
        # 3. for if and while statements, find condition a < b (if exist),
        # 4. insert print(a, b) before conditional statement executed
        b_index = 0 # branch index counter
        def dfs_instrument(node):
            nonlocal b_index

            # find body or orelse code blocks using DFS
            for info in astor.iter_node(node):
                if info[1] == 'body' or (info[1] == 'orelse' and len(info[0]) != 0):
                    # stmts : new statements list for inserting print statements
                    stmts = []

                    # for each statements do,
                    for stmt in info[0]:
                        if isinstance(stmt, ast.For) or isinstance(stmt, ast.If) or isinstance(stmt, ast.While):
                            # branch found
                            b_index += 1
                            
                            # for if and while statements, insert printing a and b
                            if isinstance(stmt, ast.While) or isinstance(stmt, ast.If):
                                # if condition is comparing two values,
                                if isinstance(stmt.test, ast.Compare):                                    
                                    # insert values assignment
                                    stmts.append(
                                        ast.Assign(
                                            targets=[ast.Tuple(elts=[
                                                ast.Name(id='TDG_l'), 
                                                ast.Name(id='TDG_r')
                                            ])],
                                            value=ast.Tuple(elts=[
                                                stmt.test.left, 
                                                stmt.test.comparators[0]
                                            ])
                                        )
                                    )
                                    # insert values printing
                                    stmts.append(
                                        ast.Expr(
                                            value=ast.Call(
                                                func=ast.Name(id='print'), 
                                                args=[
                                                    ast.Str(s='TDG'), 
                                                    ast.Str(s='V'),
                                                    ast.Str(s=str(b_index)), 
                                                    ast.Name(id='TDG_l'),
                                                    ast.Name(id='TDG_r')
                                                ], 
                                                keywords=[]
                                            )
                                        )
                                    )
                                    # substitute left and right value to assigned value
                                    stmt.test.left = ast.Name(id='TDG_l')
                                    stmt.test.comparators[0] = ast.Name(id='TDG_r')
                            
                            # for conditional statements, insert branch executed printing
                            for info2 in astor.iter_node(stmt):
                                if info2[1] == 'body':
                                    info2[0].insert(0, ast.Expr(value=ast.Call(
                                        func=ast.Name(id='print'), 
                                        args=[
                                            ast.Str(s='TDG'), 
                                            ast.Str(s='B'),
                                            ast.Str(s=str(b_index)), 
                                            ast.Str('T')
                                        ], 
                                        keywords=[]
                                    )))
                                elif info2[1] == 'orelse' and len(info2[0]) != 0:
                                    info2[0].insert(0, ast.Expr(value=ast.Call(
                                        func=ast.Name(id='print'), 
                                        args=[
                                            ast.Str(s='TDG'),
                                            ast.Str(s='B'),
                                            ast.Str(s=str(b_index)), 
                                            ast.Str('F')
                                        ], 
                                        keywords=[]
                                    )))
                        
                        # add statement to stmts
                        stmts.append(stmt)

                    # substitute body(orelse) to stmts
                    if info[1] == 'body':
                        node.body = stmts
                    elif info[1] == 'orelse' and len(info[0]) != 0:
                        node.orelse = stmts

                    # recursively DFS 
                    for stmt in info[0]:     
                        dfs_instrument(stmt)

        # do instrumenting
        dfs_instrument(f)

        # assign number of branches value
        self.num_branches = b_index

        # write instrumented file
        instrumented_file = open('instrumented_' + self.filename, 'w')
        instrumented_file.write(astor.to_source(root))
        instrumented_file.close()

        # DFS code and construct PDG
        b_index = 0 # branch index counter
        def dfs_pdg(node, pdg):
            nonlocal b_index

            # find body or orelse code blocks using DFS
            for info in astor.iter_node(node):
                if info[1] == 'body' or (info[1] == 'orelse' and len(info[0]) != 0):

                    # lisf of new pdg child nodes
                    new_pdg_list = []
                    # list of new chf child nodes' corresponding statement
                    new_pdg_list_stmt = []

            
                    # for each statements do,
                    for stmt in info[0]:
                        if isinstance(stmt, ast.For) or isinstance(stmt, ast.If) or isinstance(stmt, ast.While):
                            # branch found
                            b_index += 1

                            # make new pdg node with parent 
                            new_pdg = PDG(parent=pdg)
                            new_pdg.tf = info[1] == 'body'

                            # branch id assignment
                            new_pdg.bid = b_index

                            # branch kind assignment
                            if isinstance(stmt, ast.For):
                                new_pdg.kind = 'for'
                            elif isinstance(stmt, ast.If):
                                new_pdg.kind = 'if'
                            else:
                                new_pdg.kind = 'while'

                            # branch distance existence assignment,
                            # branch compare operation assignment
                            if isinstance(stmt, ast.If) or isinstance(stmt, ast.While):
                                if isinstance(stmt.test, ast.Compare):
                                    if isinstance(stmt.test.ops[0], ast.Lt):
                                        new_pdg.op = 'Lt'
                                    elif isinstance(stmt.test.ops[0], ast.Gt):
                                        new_pdg.op = 'Gt'
                                    elif isinstance(stmt.test.ops[0], ast.LtE):
                                        new_pdg.op = 'LtE'
                                    elif isinstance(stmt.test.ops[0], ast.GtE):
                                        new_pdg.op = 'GtE'
                                    elif isinstance(stmt.test.ops[0], ast.Eq):
                                        new_pdg.op = 'Eq'
                                    elif isinstance(stmt.test.ops[0], ast.NotEq):
                                        new_pdg.op = 'NotEq'

                            # append to pdg, stmt lists
                            new_pdg_list.append(new_pdg)
                            new_pdg_list_stmt.append(stmt)
                        
                    # when iteration is done, check the existence of child node
                    # in body/orelse, if child conditional statement not exist, 
                    # then make empty dummy node
                    if len(new_pdg_list) == 0:
                        dummy_pdg = PDG(parent=pdg)
                        dummy_pdg.tf = info[1] == 'body'
                        new_pdg_list.append(dummy_pdg)

                    # for nodes with non-root parent, add to branches list
                    for temp_new_pdg in new_pdg_list:
                        if not pdg.is_root:
                            self.branches.append(temp_new_pdg)
                    
                    # if non-dummy pdg node exists, recursively find child nodes
                    if len(new_pdg_list_stmt) != 0:
                        for i in range(len(new_pdg_list)):
                            dfs_pdg(new_pdg_list_stmt[i], new_pdg_list[i])

        # make root PDG node
        pdg = PDG()
        
        # list of branches
        # every nodes corresponds to one branch,
        # but there can exist nodes with same source, T/F
        self.branches = []

        # find branches
        dfs_pdg(f, pdg)

        # make branch information instance for utilities
        b_info = BranchInfo(self.num_branches, self.branches)
        return b_info

    # extract integers from file
    def extract_seed_ints(self):
        seed_ints = set([]) # seed ints set
        root = astor.parse_file(self.filename) # parse file

        # auxiliary function for DFS
        def dfs_extract_seed_ints(node):
            nonlocal seed_ints

            # if node is number, then add to seed ints set
            if isinstance(node, ast.Num):
                if isinstance(node.n, int):
                    seed_ints.add(node.n)
                    seed_ints.add(-node.n)
            # recursively call itself
            for info in astor.iter_node(node):
                dfs_extract_seed_ints(info[0])

        # call auxiliary function
        dfs_extract_seed_ints(root)

        # add special values
        seed_ints.update([
            #-sys.maxsize - 1,
            #sys.maxsize,
            -1,
            0,
            1
        ])

        return list(seed_ints)
    





    # auxiliary function for capturing stdout
    # from https://stackoverflow.com/questions/3906232/python-get-the-print-output-in-an-exec-statement
    @contextlib.contextmanager
    def stdoutIO(self, stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = stdout
        yield stdout
        sys.stdout = old

    # auxiliary function for timeout exception handling
    def handler(self, signum, frame):
        raise Exception('timeout')

    # run
    def run(self, args):
        filename = 'instrumented_' + self.filename
        # check existence of instrumented file
        if not os.path.isfile(filename):
            'ERROR : instrumented file not exist'
        # import file
        exec('import ' + filename.split('.')[0])

        # run code and capture stdout
        with self.stdoutIO() as s:
            # make function call operation
            statement = 'instrumented_' + self.filename[:-3] + '.' + self.funcname + '('
            for arg in args:
                statement += str(arg) + ', '
            if len(args) != 0:
                statement = statement[:-2]
            statement += ')'

            # make signal for timeout - 1 second
            signal.signal(signal.SIGALRM, self.handler)
            signal.alarm(1)

            # run statement
            try:
                random.seed(20173076)
                eval(statement)
                random.seed(None)
            except Exception as exc:
                print()
                print(exc)

            # initialize signal
            signal.alarm(0)
        
        # get log
        log = s.getvalue()

        # if timeout happend, make log empty
        if 'timeout' in log:
            log = ''

        # get log, remove unnecessary message, and return
        log = log.split('\n')

        log = [message[4:] for message in log if message[:4] == 'TDG ']

        # list of executed branches
        branch_executed = []
        # dictionary of condition values
        branch_values = {}

        # convert log into dictionaries
        if log:
            for message in log:
                message = message.split()
                if message[0] == 'B':
                    temp = (int(message[1]), True if message[2] == 'T' else False)
                    if not temp in branch_executed:
                        branch_executed.append(temp)
                else:
                    if not int(message[1]) in branch_values:
                        branch_values[int(message[1])] = ((float(message[2])), (float(message[3])))


        # return two dictionaries
        return branch_executed, branch_values
    




# main function
def main():
    # check arguemnts
    if len(sys.argv) != 2:
        print('wrong argument')
        exit()

    # get target filename    
    target_file_name = sys.argv[1]
    
    # make TDG instance
    tdg = TDG(target_file_name)

    # do instrumentation
    tdg.pre_instrument()
    b_info = tdg.instrument()

    # extract seed integers
    seed_ints = tdg.extract_seed_ints()

    # try random sampled seed integers for 100 times
    for i in range(100):
        data = [random.choice(seed_ints) for j in range(tdg.funcargs)]
        # run and test data
        branch_executed, branch_values = tdg.run(data)
        b_info.test(data, branch_executed)

    
    # AVM algorithm

    # iterate for all remaining (not executed) branches
    while len(b_info.remaining) != 0:
        # pick first remaining branch and find corresponding node
        b = b_info.remaining[0]
        node = b_info.branch_children[b[0]][0 if b[1] else 1][0]

        # if statements is for-statement,
        # or op not exist (conditions is not simple comparing)
        # or op is NotEq (then, branch distance not works),
        # then, give up and delete branch and its all children (recursively) from remaining branches
        if node.parent.kind == 'for' or not node.parent.op or node.parent.op == 'NotEq':
            b_info.node_delete(node)
            continue

        # find parent-branch-executing data
        # if parent is root (which means, closest data does not exist),
        # then just use [0, 0, ..., 0]
        current_data = None
        if node.parent.parent.is_root:
            current_data = [0 for i in range(tdg.funcargs)]
        else:
            current_data = b_info.test_suite[node.parent.parent.bid][0 if node.parent.tf else 1]

        # test current data
        b_executed, b_values = tdg.run(current_data)
        current_bd = node.bd(b_executed, b_values)

        # do AVM step for 100 times
        for i in range(100):
            # copy of current data for checking local minimum
            # if new data is identical with current data, then AVM cannot make enxt step
            local_minimum_check = []
            for datum in current_data:
                local_minimum_check.append(datum)

            # found flag for checking solution for current branch is found or not
            found = False

            # for parameters of functions,
            for j in range(tdg.funcargs):
                # make new data which is a copy of current data
                new_data = []
                for datum in current_data:
                    new_data.append(datum)

                # try +1 to the parameter and test it
                new_data[j] += 1
                b_executed, b_values = tdg.run(new_data)
                b_info.test(new_data, b_executed)
                # if new data makes target branch executed, get out of while loop
                if (node.parent.bid, node.tf) in b_executed:
                    found = True
                    break
                # if new data stays on target branch, then calculate branch distance
                elif node.parent.parent.is_root or (node.parent.parent.bid, node.parent.tf) in b_executed:
                    plus_bd = node.bd(b_executed, b_values)
                # if new data makes branches not be executed which were executed before, then ignore
                else:
                    plus_bd = sys.maxsize

                # try -1 to the parameter and test it
                new_data[j] -= 2
                b_executed, b_values = tdg.run(new_data)
                b_info.test(new_data, b_executed)
                # same with +1 case
                if (node.parent.bid, node.tf) in b_executed:
                    found = True
                    break
                # same with +1 case
                elif node.parent.parent.is_root or (node.parent.parent.bid, node.parent.tf) in b_executed:
                    minus_bd = node.bd(b_executed, b_values)
                # same with +1 case
                else:
                    minus_bd = sys.maxsize
                
                # compare 0, +1, -1 cases, and decide direction
                # if bd is same or increased, then stays on 0
                # if bd is decreased, take better case from +1 and -1 
                direction = None
                if plus_bd < current_bd:
                    if minus_bd < plus_bd:
                        direction = -1
                        new_bd = minus_bd
                    else:
                        direction = 1
                        new_bd = plus_bd
                        new_data[j] += 2
                else:
                    if minus_bd < current_bd:
                        direction = -1  
                        new_bd = minus_bd
                
                # if staying on 0, get out of for loop
                if direction == None:

                    
                    new_direction = None
                    if current_bd == plus_bd:
                        new_direction = 1
                    elif current_bd == minus_bd:
                        new_direction = -1
                    if new_direction:
                        new_data[j] += 1
                        found = False
                        decreased = False
                        for i in range(20):
                            new_data[j] += new_direction * (2 ** i)
                            b_executed, b_values = tdg.run(new_data)
                            b_info.test(new_data, b_executed)

                            if (node.parent.bid, node.tf) in b_executed:
                                # 찾음
                                found = True
                                break
                            elif node.parent.parent.is_root or (node.parent.parent.bid, node.parent.tf) in b_executed:
                                new_bd = node.bd(b_executed, b_values)
                                if new_bd < current_bd:
                                    # 낮아짐
                                    decreased = True
                                    break
                        if found or decreased:
                            current_data = new_data
                            current_bd = new_bd
                            break


                            
                            



                    new_data[j] -= 1
                    continue
               

                # do AVM steps
                exp = 1 # make steps with 2 ** exp length
                while True:
                    # make new data and test it
                    new_data[j] += direction * (2 ** exp)
                    b_executed, b_values = tdg.run(new_data)
                    b_info.test(new_data, b_executed) 
                    
                    # if new data makes target branch executed, get out of while loop
                    if (node.parent.bid, node.tf) in b_executed:
                        found = True
                        break
                    # if there is a progress, try next step
                    # if not, undo step and stop
                    elif node.parent.parent.is_root or (node.parent.parent.bid, node.parent.tf) in b_executed:
                        new_new_bd = node.bd(b_executed, b_values)
                        if new_new_bd < new_bd:
                            new_bd = new_new_bd
                            exp += 1
                        else:
                            new_data[j] -= direction * (2 ** exp)
                            break
                    # if new data makes branches not executed which were executed before, then ignore
                    else:
                        new_data[j] -= direction * (2 ** exp)
                        break

                # change new data to current data
                current_data = new_data
                # change new bd to current bd
                current_bd = new_bd

                # if input is found, then break
                if found:
                    break

            # if input is found, then break
            if found:
                break  

            # check local minimum is reached, give up
            if local_minimum_check == current_data:
                b_info.node_delete(node)
                break

    # print test suite
    b_info.print_test_suite()


# main
if __name__ == '__main__':
    main()
