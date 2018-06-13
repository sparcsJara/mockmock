import ast
import astor
import inspect
from operator import eq
from functools import reduce

class mockGenerator:
    def __init__(self, sourceCode, testFile, mockTarget, mockMethodInfo):
        # cat_owner.py
        self.sourceCode = sourceCode

        # test_cat_owner.py
        self.testFile = testFile

        # cat_database.CatDatabase
        self.mockTarget = mockTarget

        # CatDatabase
        self.mockClassName = mockTarget.split(".")[1]

        # ast tree
        self.root = astor.parse_file(self.testFile)

        self.mockMethodInfo = mockMethodInfo

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

    def getTargetTest(self):
        tests = [node[0] for node in astor.iter_node(self.root.body)
            if type(node[0]) is ast.FunctionDef]

        # 첫번째 테스트 함수가 타겟 테스트라고 가정합니다.
        return tests[0]

    def findMockInstantiationAndRemove(self, test):
        instantiations = []
        for smst in astor.iter_node(test.body):
            if type(smst[0]) is ast.Assign:
                try:
                    if (smst[0].value.func.id == self.mockClassName):
                        instantiations.append(smst[0])
                except AttributeError:
                    pass

        # mock target을 여러번 instantiate하지 않았다고 가정합니다.
        # 즉, 첫번째 instantiation을 mock할 것입니다.
        try:
            return instantiations[0]
        except:
            print('해당 Mock을 Instantiate하고 있지 않습니다.')

    def mockResponseBuilder(self, mockName, methodName, returnName):
        return ast.Assign(
            targets=[ast.Attribute(
                value=ast.Attribute(
                    value=ast.Name(id=mockName),
                    attr=methodName
                ),
                attr='return_value'
            )],
            value=ast.Name(id=returnName)
        )

    def injectMock(self):
        ################## 분석 ##################
        test = self.getTargetTest()
        mockInstantiation = self.findMockInstantiationAndRemove(test)

        # 대입에서 왼쪽이 여러개일 가능성을 배제하고, [0]으로 첫번째 인자의 이름을 가져옵니다.
        mockName = mockInstantiation.targets[0].id

    def getMethods(self):
        method_dict = {}
        mock_ast = astor.parse_file(self.mockTarget.split(".")[0] + '.py')
        classdef_ast = mock_ast.__getattribute__("body")[0]
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

        ################## 변형 ##################
        # TODO: from unittest.mock import patch 합니다.
        self.root.body = [
            ast.ImportFrom(
                module='unittest.mock',
                names=[ast.alias(name='patch', asname=None)],
                level=0
            ),
            *self.root.body
        ]

        # @patch로 mock을 주입합니다.
        test.decorator_list = [ast.Call(
            func=ast.Name(id='patch'),
            args=[ast.Str(s=self.mockTarget)],
            keywords=[]
        )]

        # argument로 mock을 주입하므로 mockInstantiation을 제거합니다.
        newBody = []
        for node in test.body:
            try:
                if type(node) is not ast.Assign or node.value.func.id != self.mockClassName:
                    newBody.append(node)
            except AttributeError:
                pass

        test.body = newBody

        # test의 argument를 args와 (@patch가 주입하는) mock으로 지정합니다.
        numMethodCalls = reduce(lambda x, y: 1 + y, self.mockMethodInfo[1])

        test.args.args = [
            *['arg' + str(n) for n in range(numMethodCalls - 1)],
            ast.arg(arg=mockName, annotation=None)
        ]

        # mock이 return하는 값으로 args를 대입합니다.
        test.body = [
            *[self.mockResponseBuilder(mockName, method[0], 'arg' + str(index))
                for index, method in enumerate(self.mockMethodInfo)],
            *test.body
        ]

    def getCorrectTestFileAST(self):
        return astor.parse_file(self.testFile)

    def getCorrectSourceCodeAST(self):
        return astor.parse_file(self.sourceCode)

    def sideEffect(self):


if __name__ == '__main__':
    gen = mockGenerator('cat_owner.py', 'test_cat_owner.py', 'cat_database.CatDatabase', {})
    gen.recordMockMethodInfo()
    gen.injectMock()
    print(astor.to_source(gen.root))
