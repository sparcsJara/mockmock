# PDG node class
class PDG:
    def __init__(self, parent=None, tf=None, bid=None, op=None, kind=None):
        # check root node or not
        if parent:
            self.is_root = False
        else:
            self.is_root = True

        # assign parent node
        self.parent = parent
        if parent:
            self.parent.add(self)

        # assign T if current node is T branch of parent, otherwise, assign F
        self.tf = tf

        # assign child CFG nodes
        self.children = []

        # for empty CFG node, it is assumed to be leaf node
        self.is_leaf = True

        # assign branch id
        self.bid = bid

        # assign compare operator
        self.op = op

        # assign conditional statement kind
        self.kind = kind

    # add child nodes to current node
    def add(self, child):
        # add child
        self.children.append(child)

        # CFG node is no more leaf node after child nodes are added
        self.is_leaf = False
    
    # NOT USED (instead, used bd function which is more simple)
    # get branch distance function
    def b_distance(self, b_executed, b_values):
        K = 0.001
        
        level = -1

        node = self
        while not node.parent.is_root:
            level += 1


            if (node.parent.parent.bid, node.parent.tf) in b_executed or node.parent.parent.is_root:
                break

            node = node.parent

        bd = None
        if node.parent.op:
            temp_op = node.parent.op
            if not node.tf:
                if temp_op == 'Lt':
                    temp_op = 'Gt'
                elif temp_op == 'Gt':
                    temp_op = 'Lt'
                elif temp_op == 'LtE':
                    temp_op = 'GtE'
                elif temp_op == 'GtE':
                    temp_op = 'LtE'
                elif temp_op == 'Eq':
                    temp_op = 'NotEq'
                elif temp_op == 'NotEq':
                    temp_op = 'Eq'
                
            # find value
            l, r = b_values[node.parent.bid]
            
            if temp_op == 'Lt' or temp_op == 'LtE':
                bd = l - r + K
            elif temp_op == 'Gt'or temp_op == 'GtE':
                bd = r - l + K
            elif temp_op == 'Eq':
                bd = abs(r - l)
            elif temp_op == 'NotEq':
                bd = -abs(r - l)

        total_bd = level
        if bd != None:
            total_bd += (1 - 1.001 ** (-bd))
        else:
            total_bd += 0.99

        return total_bd

    # simple branch distance
    def bd(self, b_executed, b_values):
        temp_op = self.parent.op
        if not self.tf:
            if temp_op == 'Lt':
                temp_op = 'Gt'
            elif temp_op == 'Gt':
                temp_op = 'Lt'
            elif temp_op == 'LtE':
                temp_op = 'GtE'
            elif temp_op == 'GtE':
                temp_op = 'LtE'
            elif temp_op == 'Eq':
                temp_op = 'NotEq'
            elif temp_op == 'NotEq':
                temp_op = 'Eq'
        
        l, r = b_values[self.parent.bid]

        bdv = 0
        if temp_op == 'Lt' or temp_op == 'LtE':
            bdv = l - r + 1
        elif temp_op == 'Gt'or temp_op == 'GtE':
            bdv = r - l + 1
        elif temp_op == 'Eq':
            bdv = abs(r - l)
        elif temp_op == 'NotEq':
            if r == l:
                bdv = 1
            else:
                bdv = 0
        
        return bdv

        

