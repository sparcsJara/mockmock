import astor,ast
import inspect
from operator import eq


class mockGenerator:
    def __init__(self, sourceCode, testFile, mockTarget):
        self.testFile = testFile
        self.mockTarget = mockTarget
        self.sourceCode = sourceCode

    def recordMockMethodInfo(self):
        targetMethods = self.getMethods()
        test_file_ast = self.getCorrectTestFileAST() # classDef
        source_code_ast = self.getCorrectSourceCodeAST() # body = functiondef

        return_list = []
        for name, isInt in targetMethods.items():
            if not isInt:
                continue
            target_name = name
            count_of_target = 0
            for node in ast.walk(test_file_ast):
                if isinstance(node, ast.Call):
                    call_node = node.__getattribute__("func")
                    if isinstance(call_node, ast.Attribute):
                        if eq(call_node.__getattribute__("attr"), target_name):
                            count_of_target = count_of_target + 1
            for node in ast.walk(source_code_ast):
                if isinstance(node, ast.Call):
                    call_node = node.__getattribute__("func")
                    if isinstance(call_node, ast.Attribute):
                        if eq(call_node.__getattribute__("attr"), target_name):
                            count_of_target = count_of_target + 1
            return_list.append((target_name, count_of_target))

        self.mockMethodInfo = return_list
        print(return_list)
        return return_list

    def injectMock(self, testFile, mockTarget, methodCalls):
        testFile = astor.parse_file(testFile)
        print(astor.dump_tree(testFile))

    def getMethods(self):
        method_dict = {}
        mock_ast = astor.parse_file(self.mockTarget)
        classdef_ast = mock_ast.__getattribute__("body")[0]
        print(astor.dump_tree(classdef_ast))
        for node in ast.walk(classdef_ast):
            if isinstance(node, ast.FunctionDef):
                return_int = False
                returns = node.__getattribute__("returns")
                if(isinstance(returns, ast.Name)):
                    name = returns.__getattribute__("id")
                    if(eq(name, "int")):
                        return_int = True
                method_dict[node.__getattribute__("name")] = return_int
        return method_dict

    def getMethodType(method, args):
        return type(method())

    def getCorrectTestFileAST(self):
        return astor.parse_file(self.testFile)

    def getCorrectSourceCodeAST(self):
        return astor.parse_file(self.sourceCode)

if __name__ == '__main__':
  gen = mockGenerator("cat_owner.py", 'test_cat_owner.py', 'cat_database.py')
  gen.recordMockMethodInfo()
  # gen.injectMock()
