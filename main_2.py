from graphviz import Digraph
a = 0
b = 0
p = 2

states = dict()

def fx(x):
    return (a*x+b)

def calculate_value(n,k,z,p):
    return ((fx(n+z*p**k)-(fx(n)%(p**k)))//p**k)%p

def calculate_start_state(z,p):
    return fx(z)%p
def transfrom_to_base_p(n,p): # здесь считается последоваптельность символом n в системе счисления с основанием p
    ans = []
    while n>0:
        ans.append(n%p)
        n/=p
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

def create_mealy_diagram(states, final_states, initial_state, output_file='moore_diagram.gv'):
    dot = Digraph(comment='Mealy Machine Diagram', format='png') # png формат, чтобы сохранить диаграмму в виде изображения
    
    # Вычисление достижимых состояний
    reachable = reachable_states(initial_state, states)

    # Создание узлов-состояний
    for state_name in states:
        if state_name not in reachable:
            continue
        if state_name == initial_state:
            style = 'filled'
            fillcolor = 'lightblue'
        else:
            style = 'filled' if state_name in final_states else ''
            fillcolor = 'grey' if state_name in final_states else 'white'
        dot.node(state_name, label=state_name, shape='circle', style=style, fillcolor=fillcolor)

    # Создание связей между состояниями
    for state_name, state_rules in states.items():
        if state_name not in reachable:
            continue
        for input_symbol, (output_symbol, next_state_name) in state_rules.items():
            label = f"{input_symbol}({output_symbol})"
            dot.edge(state_name, next_state_name, label=label)
    if a!=0:
        output_file = f"f(x)={a}*x+{b}, p={p}:diagram.gv"
    else:
        output_file = f"f(x)={b}, p={p}:diagram.pv"
    # Сохранение и отображение диаграммы
    dot.render(output_file, view=True)

def equivalence_classes(fsm):
    classes = {}
    representatives = {}  # Словарь для хранения представителей классов
    for state, transitions in fsm.items():
        signature = tuple(sorted(transitions.items()))
        # Найдем представителя класса эквивалентности для текущего состояния
        representative = representatives.get(signature)
        if representative is None:
            # Если класс эквивалентности с такой подписью еще не существует,
            # то текущее состояние становится его представителем
            representative = state
            representatives[signature] = representative
        # Добавляем текущее состояние в соответствующий класс эквивалентности
        if representative not in classes:
            classes[representative] = [state]
        else:
            classes[representative].append(state)
    return classes, representatives

def remove_equvalent_states(states):
    classes, representatives = equivalence_classes(states)
    
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

                


states[f"0,0"] = {f"{sym}" : (f"{calculate_start_state(sym,p)}", f"{sym},1") for sym in range(p)}
initial_state = "0,0"
finish_state = "q_end"
accepting_states = set()
ending_states = set()
n_processed_decimal = 0
lol_one_more_states = {}
lol_one_more_states[f"0,0"] = {f"{sym}" : (f"{calculate_start_state(sym,p)}", f"{sym},1") for sym in range(p)}
for k in range (1,5):
    
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
            for new_sym in range(p):
                
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
                if equiv_state!= []:
                    states[f"{processed_number},{k}"] = equiv_state[1]
                else:
                    states[f"{processed_number},{k}"] = {f"{new_sym}" : (f"{calculate_value(processed_number,k,new_sym,p)}", f"{processed_number+p**k*new_sym},{k+1}") for new_sym in range(p)}
                lol_one_more_states[f"{processed_number},{k}"] = {f"{new_sym}" : (f"{calculate_value(processed_number,k,new_sym,p)}", f"{processed_number+p**k*new_sym},{k+1}") for new_sym in range(p)}

print("new states:")
for state_name, state_val in states.items():
    print(state_name, state_val)

final_states = remove_equvalent_states(states)
for name, value in remove_equvalent_states(states).items():
    print(name, value)

create_mealy_diagram(final_states, set(final_states.keys()) - set("0,0"), "0,0")
