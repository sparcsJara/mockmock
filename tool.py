from searchBasedTestGenerator import test_generator
import sys
from mockGenerator import mockGenerator
import os

def main():
    args = sys.argv[1:]
    mock_return_values = test_generator(args[0], args[1], args[2])

    total_branches = 0
    executed_branches = 0

    for branch in mock_return_values:
        for tf in branch:
            total_branches += 1
            if tf:
                executed_branches += 1

    os.remove('instrumented_' + args[0])
    os.remove('instrumented_' + args[1])

    print('total number of branches :', total_branches)
    print('number of executed_branches :', executed_branches)
    print('coverage : {}%'.format(executed_branches / total_branches * 100))

if __name__ == '__main__':
    main()

