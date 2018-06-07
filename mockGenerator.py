import inspect

class mockGenerator():
    testFile
    mockTarget
    mockMethodInfo

    def recordMockMethodsInfo(self):



    def getMethods(cs):
        members = inspect.getmembers(cs, predicate=inspect.ismethod)
        methods = []
        for member in members:
            methods.append(member[0])
        return methods
