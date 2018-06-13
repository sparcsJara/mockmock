# Branch class for saving branches' information
class BranchInfo:
    # initialize
    def __init__(self, num_branches, branches):
        self.num_branches = num_branches
        # make branch-existence table
        self.branch_existence = [[False, False] for i in range(num_branches)]
        self.branch_existence.insert(0, None) # branch index starts with 1

        # make branch-children table
        self.branch_children = [[[], []] for i in range(num_branches)]
        self.branch_children.insert(0, None) # branch index starts with 1

        for branch in branches:
            if branch.tf:
                temp_index = 0
            else:
                temp_index = 1
            
            self.branch_existence[branch.parent.bid][temp_index] = True
            self.branch_children[branch.parent.bid][temp_index].append(branch)

        # get total number of branches
        self.total_num_branches = 0
        for branch in self.branch_existence[1:]:
            for branch_tf in branch:
                if branch_tf:
                    self.total_num_branches += 1

        # remaning branches which are not executed
        self.remaining = []
        for i in range(num_branches):
            j = i + 1
            if self.branch_existence[j][0]:
                self.remaining.append((j, True))
            if self.branch_existence[j][1]:
                self.remaining.append((j, False))
        
        # test suite
        self.test_suite = [[None, None] for i in range(num_branches)]
        self.test_suite.insert(0, None)

    # add test case to test suite
    def test(self, t_case, b_executed):
        for b in b_executed:
            # if executed branch is not executed before,
            # remove branch from remaining list,
            # and add test case to test suite
            if b in self.remaining:
                self.remaining.remove(b)
                self.test_suite[b[0]][0 if b[1] else 1] = t_case

    # return total number of branches, 
    # number of executed branches,
    # percentage of executed branches
    def statistics(self):
        total = self.total_num_branches
        executed = total - len(self.remaining)
        percentage = executed / total
        return total, executed, percentage

    # print test suite
    def print_test_suite(self):
        for i in range(len(self.branch_existence[1:])):
             j = i + 1
             for k in range(len(self.branch_existence[j])):
                 if self.branch_existence[j][k]:
                    message = ''
                    # branch number
                    message += str(j)
                    # branch T/F
                    if k == 0:
                        message += 'T'
                    else:
                        message += 'F'
                    message += ': '

                    # test case
                    if self.test_suite[j][k]:
                        for num in self.test_suite[j][k]:
                            message += str(num)
                            message += ', '
                        else:
                            message = message[:-2]
                    # test case not exist
                    else:
                        message += '-'

                    print(message)

    # delete node from remaining recursively
    def node_delete(self, node):
        self.remaining.remove((node.parent.bid, node.tf))
        if node.children:
            for child in node.children:
                self.node_delete(child)



