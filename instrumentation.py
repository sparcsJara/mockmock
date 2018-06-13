import astor
import ast
from PDG import PDG
from io import StringIO
import sys
import contextlib
import os
from BranchInfo import BranchInfo

def instrument(filename, mockname):
    root = astor.parse_file(filename)

    def pre_instrument(node):
        for info in astor.iter_node(node):
            if info[1] == 'body' or info[1] == 'orelse':
                for stmt in info[0]:
                    if isinstance(stmt, ast.For) or isinstance(stmt, ast.If) or isinstance(stmt, ast.While):
                        if len(stmt.orelse) == 0:
                            stmt.orelse.append(ast.Pass())
                    pre_instrument(stmt)

    pre_instrument(root)

    # labeling method calls
    mock_name = mockname
    method_dic = {}
    counter = 12345678
    def dfs_instrument_method(node):
        nonlocal mock_name
        nonlocal method_dic
        nonlocal counter

        if isinstance(node, ast.Call):
            if isinstance(node.func.value, ast.Attribute) and node.func.value.attr == mock_name or isinstance(node.func.value, ast.Name) and node.func.value.id == mock_name:
                node.args = [ast.Num(n=counter)]
                if node.func.attr in method_dic:
                    method_dic[node.func.attr].append(counter)
                else:
                    method_dic[node.func.attr] = []
                    method_dic[node.func.attr].append(counter)
                counter += 1
        else:
            for child in ast.iter_child_nodes(node):
                dfs_instrument_method(child)
    dfs_instrument_method(root)



    pre_instrumented_file = open('pre_instrumented_' + filename, 'w')
    pre_instrumented_file.write(astor.to_source(root))
    pre_instrumented_file.close()

    ###

    root = astor.parse_file('pre_instrumented_' + filename)

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
                                                ast.Name(id='TDG_r'),
                                                #ast.Call(func=ast.Name(id='type'), args=[ast.Name(id='TDG_l')], keywords=[]),
                                                #ast.Call(func=ast.Name(id='type'), args=[ast.Name(id='TDG_r')], keywords=[]),
                                                ast.Attribute(value=ast.Call(func=ast.Name(id='type'), args=[ast.Name(id='TDG_l')], keywords=[]), attr='__name__'),
                                                ast.Attribute(value=ast.Call(func=ast.Name(id='type'), args=[ast.Name(id='TDG_r')], keywords=[]), attr='__name__')
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
    dfs_instrument(root)

    instrumented_file = open('instrumented_' + filename, 'w')
    instrumented_file.write(astor.to_source(root))
    instrumented_file.close()
    os.remove('pre_instrumented_' + filename)

    ###

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
                        branches.append(temp_new_pdg)
                
                # if non-dummy pdg node exists, recursively find child nodes
                if len(new_pdg_list_stmt) != 0:
                    for i in range(len(new_pdg_list)):
                        dfs_pdg(new_pdg_list_stmt[i], new_pdg_list[i])

    branches = []
    num_branches = b_index
    # make root PDG node
    pdg = PDG()

    # find branches
    dfs_pdg(root, pdg)

    ###
    pdg_class = PDG()
    pdg_methods = []
    for info in astor.iter_node(root):
        for stmt in info[0]:
            if isinstance(stmt, ast.ClassDef):
                dfs_pdg(stmt, pdg_class)
        
            for info in astor.iter_node(stmt):
                if info[1] == 'body':
                    for stmt in info[0]:
                        if isinstance(stmt, ast.FunctionDef):
                            pdg_temp = PDG()
                            dfs_pdg(stmt, pdg_temp)
                            pdg_methods.append(pdg_temp)


    num_branches = b_index

    #print(pdg_methods[0].children[0].bid)
    #print(num_branches)

    #print(pdg_class.is_root, pdg_methods[0].is_root, pdg_methods[1].is_root)

    return BranchInfo(num_branches, branches), pdg_class, pdg_methods, method_dic

