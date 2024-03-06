from graphviz import Digraph
a = 4
b = 0
p = 2
a,b,p = map(int, input("Введите a,b,p разделенные пробелом для функции f(x) = ax+b (mod p):").split())
print(a,b,p)
state_label = input("Введите символ обозначения состояни, например, q")
if state_label != "":
    state_label+="_"

def fx(x):
    return (a*x+b)

def calculate_value(n,k,z,p):
    return ((fx(n+z*p**k)-(fx(n)%(p**k)))//p**k)%p

def calculate_start_state(z,p):
    return fx(z)%p

def transfrom_to_base_p(n,p):
    ans = []
    while n>0:
        ans.append(n%p)
        n//=p
    return ans

def transform_to_decimal(x,p):
    ans = 0
    deg = 0
    for sym in x:
        ans+= int(sym)* (p**deg)
        deg+=1
    return ans
def search(state, visited, states):
    if state in visited:
        return
    visited.add(state)
    for _, (_, next_state_name) in states[state].items():
        search(next_state_name, visited, states)

def reachable_states(initial_state, states):
    visited = set()
    search(initial_state, visited, states)
    return visited

def create_mealy_diagram(states, final_states, initial_state, state_label, output_file='moore_diagram.gv'):
    dot = Digraph(comment='Mealy Machine Diagram', format='png')
    reachable = reachable_states(initial_state, states)

    for state_name in states: #создание узлов состояний
        if state_name not in reachable:
            continue
        if state_name == initial_state:
            style = 'filled'
            fillcolor = 'lightblue'
        else:
            style = 'filled' if state_name in final_states else ''
            fillcolor = 'grey' if state_name in final_states else 'white'
        dot.node(state_name, label=state_label+state_name, shape='circle', style=style, fillcolor=fillcolor)

    for state_name, state_rules in states.items(): #создание связей между состояними 
        if state_name not in reachable:
            continue
        for input_symbol, (output_symbol, next_state_name) in state_rules.items():
            label = f"{input_symbol}|{output_symbol}"
            dot.edge(state_name, next_state_name, label=label)
    if a!=0:
        output_file = f"f(x)={a}*x+{b}, p={p}:diagram.gv"
    else:
        output_file = f"f(x)={b}, p={p}:diagram.pv"

    dot.render(output_file, view=True)


def equivalence_classes(fsm, s):
    classes = {} 
    representatives = {}  

    for state, transitions in fsm.items():
        k = int(state.split(',')[1])  # Получаем значение k из имени состояния
        transitions_signature = tuple((input_symbol, output[0]) for input_symbol, output in transitions.items())
        representative = None
        if k < s:
            for rep_state, rep_transitions in representatives.items():
                rep_k = int(rep_state.split(',')[1])
                rep_transitions_signature = tuple((input_symbol, output[0]) for input_symbol, output in rep_transitions.items())
                if k == rep_k and transitions_signature == rep_transitions_signature:
                    representative = rep_state
                    break
            if representative is None:
                representative = state
                representatives[state] = transitions
        else:
            for rep_state, rep_transitions in representatives.items():
                rep_k = int(rep_state.split(',')[1])
                rep_transitions_signature = tuple((input_symbol, output[0]) for input_symbol, output in rep_transitions.items())
                if rep_k >=s and rep_transitions_signature == transitions_signature:
                    representative = rep_state
                    break
            if representative is None:
                representative = state
                representatives[state] = transitions
        if representative not in classes:
            classes[representative] = [state]
        else:
            classes[representative].append(state)

    return classes, representatives
def equiv_classes(fsm):
    classes = {}
    representatives = {}
    for state, transitions in fsm.items():
        signature = tuple(sorted(transitions.items()))
        representative = representatives.get(signature)
        if representative is None:

            representative = state
            representatives[signature] = representative

        if representative not in classes:
            classes[representative] = [state]
        else:
            classes[representative].append(state)
    return classes, representatives

def remove_equvalent_states(states, s):
    classes, representatives = equivalence_classes(states, s)
    
    new_states = {}
    print("Классы эквивалентности:")
    for representative, st in classes.items():
        print(f"Представитель: {representative}")
        print(f"Состояния: {st}")
        print()
    last_new_states = {}
    for key1, val1 in states.items():
        for class_name, class_representatives in classes.items():
            if key1 in class_representatives and not str(class_name) in new_states.keys():
                new_states[str(class_name)] = states[str(class_name)]
    for key, value in new_states.items():
        new_value = {}
        for inp_sym, next_state in value.items():
            new_b = next_state[1]
            for name, repr in classes.items():
                if new_b in repr:
                    new_value[inp_sym] = (next_state[0], str(name))
        last_new_states[key] = new_value        
    return last_new_states

def remove_equvalent_states2(states):
    classes, representatives = equiv_classes(states)
    
    new_states = {}
    print("Классы эквивалентности:")
    for representative, st in classes.items():
        print(f"Представитель: {representative}")
        print(f"Состояния: {st}")
        print()
    last_new_states = {}
    for key1, val1 in states.items():
        for class_name, class_representatives in classes.items():
            if key1 in class_representatives and not str(class_name) in new_states.keys():
                new_states[str(class_name)] = states[str(class_name)]
    for key, value in new_states.items():
        new_value = {}
        for inp_sym, next_state in value.items():
            new_b = next_state[1]
            for name, repr in classes.items():
                if new_b in repr:
                    new_value[inp_sym] = (next_state[0], str(name))
        last_new_states[key] = new_value        
    return last_new_states


def create_states_for_const_function(b,p):
    states = dict()
    states[f"0,0"] = {f"{sym}" : (f"{calculate_start_state(sym,p)}", f"{sym},1") for sym in range(p)}
    ending_states = set()
    lol_one_more_states = {}
    lol_one_more_states[f"0,0"] = {f"{sym}" : (f"{calculate_start_state(sym,p)}", f"{sym},1") for sym in range(p)}
    l = len(transfrom_to_base_p(b,p))
    for k in range (1,len(transfrom_to_base_p(b,p))+3):
        ending_states.clear()
        processing_states = []
        for key,state in states.items():
                pos=key.find(",")
                prev_num = int(key[:pos])
                prev_k = int(key[pos+1:])
                if k == prev_k+1:
                    processing_states.append(key)
        for state_name in processing_states:
            pos = state_name.find(",")
            prev_num = int(state_name[:pos])
            prev_k = int(state_name[pos+1:])
            
            for sym in range(p):
                    processed_number = (p**(k-1)*sym+prev_num)
                    states[f"{processed_number},{k}"] = {f"{new_sym}" : (f"{calculate_value(processed_number,k,new_sym,p)}", f"{processed_number+p**k*new_sym},{k+1}") for new_sym in range(p)} 
    return states
    
def create_states_for_linear_function(a,b,p):
    states = dict()
    states[f"0,0"] = {f"{sym}" : (f"{calculate_start_state(sym,p)}", f"{sym},1") for sym in range(p)}
    ending_states = set()
    for k in range (1,7):
        
        ending_states.clear()
        processing_states = []
        for key,state in states.items():
                pos=key.find(",")
                prev_num = int(key[:pos])
                prev_k = int(key[pos+1:])
                if k == prev_k+1:
                    processing_states.append(key)
        for state_name in processing_states:
            pos = state_name.find(",")
            prev_num = int(state_name[:pos])
            prev_k = int(state_name[pos+1:])
            for sym in range(p):
                processed_number = (p**(k-1)*sym+prev_num)

                equiv_state = []
                for state, value in states.items():
                    f = 1
                    for check_sym in range(p):
                        new_value = calculate_value(processed_number,k,check_sym,p)
                        if value[f"{check_sym}"][0] != f"{new_value}":
                            f = 0
                    if f:
                        equiv_state.append(f"{processed_number},{k}")
                        equiv_state.append(value)
                # if equiv_state!= []:
                #     states[f"{processed_number},{k}"] = equiv_state[1]
                # else:
                states[f"{processed_number},{k}"] = {f"{new_sym}" : (f"{calculate_value(processed_number,k,new_sym,p)}", f"{processed_number+p**k*new_sym},{k+1}") for new_sym in range(p)}
    return states

def simulate_fsm(fsm, x, p):
    x_seq = transfrom_to_base_p(x,p)
    print("Введенное число в системе счисления с основнием p:", transfrom_to_base_p(x,p))
    state = "0,0"
    result = list()
    for x_i in x_seq:
        print(fsm[state][str(x_i)][0])
        result.append(fsm[state][str(x_i)][0])
        state = fsm[state][str(x_i)][1]
    print("f(x)=",transform_to_decimal(result, p))


if a == 0:
    states = create_states_for_const_function(b,p)
else:
    states = create_states_for_linear_function(a,b,p)

for name, val in states.items():
    print(name, ":")
    for inp, outp in val.items():
        print(inp,":", f"output symbol={outp[0]}; next state={outp[1]}")

if a == 1 and b ==1:
    states = remove_equvalent_states2(states)
else:
    states = remove_equvalent_states(states, len(transfrom_to_base_p(b,p)))
create_mealy_diagram(states, set(states.keys()) - set("0,0"), "0,0", state_label=state_label)

start_simulation = input("Хотите запустить симуляцию работы автомата? y/n:")
if start_simulation == 'y':
    x = int(input("Введите входное число для автомата (оно будет переведено в систему счисления с основнием p):"))
    simulate_fsm(states, x, p)