import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, Or, And, Not, simplify

# Function to draw K-Map
def draw_kmap(numVar, minterms, dont_cares):
    kmap_size = 2 ** numVar
    kmap = np.full(kmap_size, '-')
    
    for minterm in minterms:
        kmap[minterm] = '1'
    for dont_care in dont_cares:
        kmap[dont_care] = 'X'
    
    # Create a plot for K-Map
    fig, ax = plt.subplots()
    
    ax.set_xticks(np.arange(2 ** (numVar // 2)))
    ax.set_yticks(np.arange(2 ** (numVar // 2)))
    ax.set_xticklabels(['{0:02b}'.format(i) for i in range(2 ** (numVar // 2))])
    ax.set_yticklabels(['{0:02b}'.format(i) for i in range(2 ** (numVar // 2))])
    
    for i in range(2 ** (numVar // 2)):
        for j in range(2 ** (numVar // 2)):
            minterm_value = (i << (numVar // 2)) | j
            ax.text(j, i, kmap[minterm_value], ha='center', va='center', color='black')
    
    ax.set_title(f'{numVar}-Variable K-Map')
    plt.gca().invert_yaxis()
    plt.grid(True)
    plt.show()

# Function to convert binary string to Boolean expression
def binary_to_expr(binary_str, variables):
    expr = ""
    for i, bit in enumerate(binary_str):
        if bit == '1':
            if expr:
                expr += " + "
            term = ""
            if i < len(variables):
                term += variables[i]
            else:
                term += "X"  # For indices greater than number of variables
            expr += term
        elif bit == '0':
            if expr:
                expr += " + "
            term = ""
            if i < len(variables):
                term += Not(symbols(variables[i]))
            else:
                term += Not(symbols("X"))
            expr += term
    return expr

# Function to simplify Boolean expression
def simplify_expr(expr_str):
    expr = simplify(expr_str)
    return expr

# Main minimization function
def minFunc(numVar, stringIn):
    if stringIn.find("d") + 1 < len(stringIn) and stringIn[stringIn.find("d") + 1] == " ":
        stringIn = stringIn[:stringIn.find("d") + 1] + stringIn[stringIn.find("d") + 2:]
    
    dont_care = 0
    string1 = stringIn[1:stringIn.find('d')-2]
    string2 = stringIn[stringIn.find('d')+1:]
    
    if string2[-1] != '-':
        dont_care = string2[1:len(string2)-1]
        stringIn1 = string1.split(",") + dont_care.split(",")
    else:
        stringIn1 = string1.split(",")
    
    if string1 == "":
        return "0"
    
    minterms = list(map(int, string1.split(",")))
    dont_cares = list(map(int, dont_care.split(","))) if dont_care else []
    
    # Draw the K-Map
    draw_kmap(numVar, minterms, dont_cares)
    
    sort_string = sorted(list(map(int, stringIn1)))
    stringIn1 = list(map(str, sort_string))
    b = []
    
    if numVar == 4:
        variables = ['A', 'B', 'C', 'D']
    elif numVar == 3:
        variables = ['A', 'B', 'C']
    elif numVar == 2:
        variables = ['A', 'B']
    
    for i in range(len(stringIn1)):
        int1 = int(stringIn1[i])
        str1 = ""
        if int1 == 0:
            b.append("0"*numVar)
        else:
            while int1 > 0:
                d = int1 % 2
                str1 = str(d) + str1
                int1 //= 2
            b.append(str1.zfill(numVar))
    
    minterms_expr = [binary_to_expr(binary, variables) for binary in b]
    minterms_expr = " + ".join(minterms_expr)
    
    minimized_expr = simplify_expr(minterms_expr)
    
    return minimized_expr

# Main program
kmap = int(input("Enter the number of variables (2, 3, or 4): "))
number1 = tuple(map(int, input("Enter the minterms (space separated): ").split()))
if len(number1) == 1:
    number1 = "("+str(number1[0])+")"
if len(number1) == 0:
    number1 = "()"
dontCare = input("If don't care present, enter don't care values with space in between, else enter no: ")
if dontCare.lower() == "no":
    dontCare = "-"
else:
    dontCare = tuple(map(int, dontCare.split()))
    if len(dontCare) == 1:
        dontCare = "("+str(dontCare[0])+")"
    elif len(dontCare) == 0:
        dontCare = "-"
inputString = str(number1)+" d "+str(dontCare)
print("Input String:", inputString)
print("Minimized Function:", minFunc(kmap, inputString))
