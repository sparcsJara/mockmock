import astor
import inspect


class mockGenerator:
    def __init__(self, testFile, mockTarget):
        self.testFile = testFile
        self.mockTarget = mockTarget

    def recordMockMethodInfo(self, testFile, mockTarget):
        ## TODO: 문영
        self.mockMethodInfo = {
            'method1': 2,
            'method2': 1
        }

    def injectMock(self, testFile, mockTarget, methodCalls):
        testFile = astor.parse_file(testFile)
        print(astor.dump_tree(testFile))

    def getMethods(cs):
        members = inspect.getmembers(cs, predicate=inspect.ismethod)
        methods = []
        for member in members:
            methods.append(member[0])
        return methods


if __name__ == '__main__':
  gen = mockGenerator('test_cat_owner.py', 'cat_database.py')
  gen.getMockMethodInfo()
  gen.injectMock(methods)
