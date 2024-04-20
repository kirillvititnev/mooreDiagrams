from fractions import Fraction
from pyadic import PAdic
from fractions import Fraction as Q
import math
import time
from graphviz import Digraph

c = 23
d = 5
e = 5
f = 7
p = 3
FUNCTION_COMPARATION_ACCURACY_EXP = 4
FUNCTION_COMPARATION_LENGTH = 30
MINIMAL_REPRESENTATION_LENGTH = 100
# Redefining the gcd function as it seems to have been left out in the previous message
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

# Redefining the extended Euclidean algorithm to include the gcd function


def p_adic_inverse(s, p, k):
    def extended_euclidean(a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, x, y = extended_euclidean(b % a, a)
            return (g, y - (b // a) * x, x)
    
    g, inv, _ = extended_euclidean(s, p**k)
    if g != 1:
        raise ValueError("Inverse does not exist since gcd ≠ 1")
    return inv % (p**k)

def to_p_adic(r, s, p):
    common_gcd = gcd(r, s)
    if common_gcd != 1:
        r //= common_gcd
        s //= common_gcd
    if r == 0:
        return (), (0,)
    k = MINIMAL_REPRESENTATION_LENGTH  # We choose a large k for simplicity
    s_inv = p_adic_inverse(s, p, k)

    # Multiply r by s_inv to get the p-adic representation
    rp = r * s_inv % p**k

    # Get the order v
    v = 0
    while rp % p == 0 and rp != 0:
        rp //= p
        v += 1

    p_adic_digits = []

    while abs(rp) > 0:
        p_adic_digits.append(rp % p)
        rp //= p
    # print(len(p_adic_digits))
    # while len(p_adic_digits)< MINIMAL_REPRESENTATION_LENGTH:
    #         p_adic_digits.append(0)
    # if len(p_adic_digits)>50:
    #     p_adic_digits = p_adic_digits[:50]
        
    p_adic_number = tuple(p_adic_digits)
    p_adic_digits = tuple(p_adic_digits)
    is_periodic = False
    def find_minimal_period(a:tuple):
        for j in range (1, len(a)//2):
            if a[-j:] == a[-2*j:-j]:
                return a[-j:]
        return None
    p_adic_digits = p_adic_digits[:-10]
    # Identify if the p-adic representation is periodic
    for i in range(len(p_adic_digits)//2, 1, -1):
        if i == 12:
            print(p_adic_digits[-i:],"and  ", p_adic_digits[-2*i:-i], "anddd", p_adic_digits[-3*i:-2*i])
        if p_adic_digits[-i:] == p_adic_digits[-2*i:-i]:
            
            p_adic_periodic_part = p_adic_digits[-i:]
            is_periodic = True
            min_per = find_minimal_period(p_adic_periodic_part)
            if min_per == None:
                return (0,)*v + p_adic_digits[:], p_adic_periodic_part
            else:
                print("here")
                return (0,)*v + p_adic_digits[:], find_minimal_period(p_adic_periodic_part)

    print("BAD", r, s, p_adic_digits)
    time.sleep(10)
    return (0,) *v+p_adic_digits, ""


#returns p-adic array of result letters with its periods
def fx_rational(x): 
    s, period = to_p_adic(f*c*x+e*d, d*f, p)
    return s, period

#returns array of numbers that correspnds to expansion of function f_{n,k} from Anashin's article
def fnk_rational(n,k,x):
    tuple1, per1 = fx_rational(n+x*p**k)
    if len(tuple1) <=2*k:
        while len(tuple1) <= 2*k+1:
            if len(per1) > 0:
                tuple1+=per1
            else:    
                tuple1+= (0,)
    return tuple1[k:], per1


#makes a function fingerprint which looks like "f(val1)\nf(val2)...f(valp**FUNCTION_COMPARATION_ACCURACY_EXP)"
def get_function_fingerprint(n,k):
    res=""
    for x in range(50):
        digits, period = fnk_rational(n,k,x)
        periodic_length = len(period)
        if periodic_length == 0:
            while len(digits)<FUNCTION_COMPARATION_LENGTH:
                digits+=(0,)
        else:
            while len(digits)<FUNCTION_COMPARATION_LENGTH:
                digits+=period
        res+=str(digits[:FUNCTION_COMPARATION_LENGTH])
        res+='\n'
    return res

#возаращает (n,k) для которых функция с таким отпечатком уже встречалась
def compare_fingerprints(current_fingerprint, previous_fingerprints, fingerprint_states): 
    for fingerprint in previous_fingerprints:
        if fingerprint == current_fingerprint:
            return fingerprint_states[fingerprint]
    return None

#генерация состояний из текущей вершины графа (n,k)
def generate_states_from_current_vertice(current_state):
    global previous_fingerprints
    global fingerprint_states
    global states
    processing_states = set()
    n = current_state[0]
    k = current_state[1]
    processing_states.add(current_state)
    got_new_fingerprint = True
    while got_new_fingerprint == True:
        got_new_fingerprint = False
        next_processing_states = set()
        for state in processing_states:
            states[state] = dict()
            for input_symbol in range(p):
                states[state][input_symbol] = (fnk_rational(n,k,input_symbol)[0][0], (n+input_symbol*p**k, k+1))
                next_processing_states.add((n+input_symbol*p**k, k+1))

            current_fingerprint = get_function_fingerprint(n,k)
            if compare_fingerprints(current_fingerprint, previous_fingerprints, fingerprint_states) == None:
                fingerprint_states[current_fingerprint] = (n,k)
                previous_fingerprints.add(current_fingerprint)
                got_new_fingerprint = True
                for next_state in next_processing_states:
                    generate_states_from_current_vertice(next_state)
                return 
            else:
                analogical_state = fingerprint_states[current_fingerprint]
                prev_n = state[0]
                prev_k = k-1
                prev_input_symbol = prev_n//(p**(k-1))
                prev_n = int(state[0] - prev_input_symbol * p**(k-1))
                states[(prev_n, prev_k)][prev_input_symbol] = (fnk_rational(prev_n,prev_k,prev_input_symbol)[0][0], analogical_state)
        
        processing_states = next_processing_states
        k+=1



#finction that returns reachable states from current state
def search(state_n, state_k, visited, states):
    if (state_n, state_k) in visited:
        return
    visited.add((state_n, state_k))
    for _, (_, next_state) in states[(state_n, state_k)].items():
        search(next_state[0], next_state[1], visited, states)

#finds only reachable states
def reachable_states(states):
    visited = set()
    search(0,0, visited, states)
    return visited

#this function returns map from previous state names (n,k) to simngle decimal i
def change_states_numberation(states): 
    current_state_name = 0
    true_numeration = dict()
    for state in reachable_states(states):
        true_numeration[state] = current_state_name
        current_state_name+=1
    return true_numeration

def create_mealy_diagram(states, final_states, initial_state, state_label, output_file='moore_diagram.gv'):
    dot = Digraph(comment='Mealy Machine Diagram', format='png')
    reachable = reachable_states(states)
    better_state_names = change_states_numberation(states)

    for state_name in states: #создание узлов состояний
        if state_name not in reachable:
            continue
        if state_name == initial_state:
            style = 'filled'
            fillcolor = 'lightblue'
        else:
            style = 'filled' if state_name in final_states else ''
            fillcolor = 'grey' if state_name in final_states else 'white'
        dot.node(f"{state_name[0]},{state_name[1]}", label=state_label+str(better_state_names[state_name]), shape='circle', style=style, fillcolor=fillcolor)

    for state_name, state_rules in states.items(): #создание связей между состояними 
        if state_name not in reachable:
            continue
        for input_symbol, (output_symbol, next_state_name) in state_rules.items():
            label = f"{input_symbol}|{output_symbol}"
            dot.edge(f"{state_name[0]},{state_name[1]}", f"{next_state_name[0]},{next_state_name[1]}", label=label)
    results_folder = "results/"
    if c!=0:
        if e!=0:
            output_file = f"f(x)={c}x:{d}+{e}:{f}, p={p}:diagram.gv"
        else:
            output_file = f"f(x)={c}x:{d}, p={p}:diagram.gv"
    else:
        if e!=0:
            output_file = f"f(x)={e}:{f}, p={p}:diagram.pv"
        else:
            output_file = f"f(x)=0, p={p}:diagram.gv"

    dot.render(results_folder+output_file, view=True)

def simulate_transducer(states, start_state, x:int):
    true_res, period = to_p_adic(c*f*x+e*d, f*d, p)
    x_padic, period = to_p_adic(x,1,p)
    currents_state = start_state
    i=0
    for x_i in x_padic:
        print("input =",x_i, "output =",states[currents_state][x_i][0])
        if states[currents_state][x_i][0] == true_res[i]:
            print("Correct output")
        else:
            print("incorrect output! Stopping..")
            break
        currents_state = states[currents_state][x_i][1]
        
        i+=1

states = dict() 
previous_fingerprints = set()
fingerprint_states = dict()
processing_states = set()

k_prev = 0
n = 0
k = 0
start_state=(0,0)

generate_states_from_current_vertice(start_state)
create_mealy_diagram(states=states, final_states=set(states.keys()), initial_state=start_state, state_label="s")
simulate_transducer(states, start_state, 123236536626632)
