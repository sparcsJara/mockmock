from instrumentation import instrument
from mockGenerator import mockGenerator
import random



def test_generator(target_name, test_name, mock_name):

    b_info, pdg_class, pdg_methods, method_dic = instrument(target_name, mock_name)

    gen = mockGenerator(target_name, test_name, mock_name, method_dic)
    num_methods = gen.getMethodNum()

    def run(args):
        log = gen.run(args)
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
                        # TODO : handle non-numerical values
                        branch_values[int(message[1])] = ((float(message[2])), (float(message[3])))

        return branch_executed, branch_values


    # b_info, pdg_class, pdg_methods, branch_executed, branch_values, num_methods


    for i in range(100):
        data = [random.randint(-100, 100) for i in range(num_methods)]
        branch_executed, branch_values = run(data)
        b_info.test(data, branch_executed)


    while len(b_info.remaining) != 0:
        b = b_info.remaining[0]
        node = b_info.branch_children[b[0]][0 if b[1] else 1][0]

        if node.parent.kind == 'for' or not node.parent.op or node.parent.op == 'NotEq':
            b_info.node_delete(node)
            continue

        current_data = None
        if node.parent.parent.is_root:
            current_data = [0 for i in range(num_methods)]
        else:
            current_data = b_info.test_suite[node.parent.parent.bid][0 if node.parent.tf else 1]

        b_executed, b_values = run(current_data)
        current_bd = node.bd(b_executed, b_values)

        for i in range(100):
            # copy of current data for checking local minimum
            # if new data is identical with current data, then AVM cannot make enxt step
            local_minimum_check = []
            for datum in current_data:
                local_minimum_check.append(datum)

            found = False

            for j in range(num_methods):
                # make new data which is a copy of current data
                new_data = []
                for datum in current_data:
                    new_data.append(datum)

                # try +1 to the parameter and test it
                new_data[j] += 1
                b_executed, b_values = run(new_data)
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
                b_executed, b_values = run(new_data)
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
                            b_executed, b_values = run(new_data)
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
                    b_executed, b_values = run(new_data)
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

    return b_info.test_suite[1:]


if __name__ == '__main__':
    test_generator('cat_owner.py', 'test_cat_owner.py', 'cat_database.CatDatabase')