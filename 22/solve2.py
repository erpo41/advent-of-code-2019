#!/usr/bin/python3

#inputfile = "sample1.txt"
inputfile = "myinput.txt"
decksize = 119315717514047 #prime again
repetitions = 101741582076661
endposition = 2020

instructions = []
with open(inputfile,"r") as f:
    for line in f:
        line = line.rstrip("\n")
        if line == "deal into new stack":
            instructions.append(("multiply",-1))
            instructions.append(("add",-1))
        elif line[0:4] == "cut ":
            instructions.append(("add",-1*int(line[4:])))
        elif line[0:20] == "deal with increment ":
            instructions.append(("multiply",int(line[20:])))
        else:
            print("invalid line: {}".format(line))
            exit(1)

def shuffle(startposition,instructions):
    pos = startposition
    for instruction in instructions:
        if instruction[0] == "add":
            pos += instruction[1]
        elif instruction[0] == "multiply":
            pos *= instruction[1]
        else:
            print("invalid instruction: {}".format(instruction))
        pos %= decksize
    return pos

def compact(instructions):
    multiplier = 1
    offset = 0
    for instruction in instructions:
        if instruction[0] == "add":
            offset += instruction[1]
            offset %= decksize
        elif instruction[0] == "multiply":
            multiplier *= instruction[1]
            multiplier %= decksize
            offset *= instruction[1]
            offset %=  decksize
        else:
            print("invalid instruction: {}".format(instruction))
    newinstructions = []
    newinstructions.append(("multiply",multiplier))
    newinstructions.append(("add",offset))
    return newinstructions

#from https://stackoverflow.com/questions/4798654/modular-multiplicative-inverse-function-in-python
def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m

def revinstructions(instructions):
    newinstructions = instructions.copy()
    newinstructions.reverse()
    revinstructions = []
    for instruction in newinstructions:
        if instruction[0] == "add":
            offset = (instruction[1] * -1) % decksize
            revinstructions.append(("add",offset))
        elif instruction[0] == "multiply":
            multiplier = modinv(instruction[1] % decksize ,decksize)
            revinstructions.append(("multiply",multiplier))
        else:
            print("invalid instruction: {}".format(instruction))
            exit(1)
    return revinstructions
            
instructions = compact(instructions)
undoonce = compact(revinstructions(instructions)) # compact not needed, but fun

repdigits = [int(i) for i in list(str(repetitions))]
repdigits.reverse() #first elements is in 1s place, 2nd in 10s place, etc.
undoxtimes = {1: undoonce}
for i in range(1,len(repdigits)):
    placevalue = 10 ** i
    lastplacevalue = 10 ** (i-1)
    newinstructions = undoxtimes[lastplacevalue] * 10
    newinstructions = compact(newinstructions)
    undoxtimes[placevalue] = newinstructions

repundo = []
for i in range(len(repdigits)):
    repundo.extend(undoxtimes[10**i]*repdigits[i])
    repundo = compact(repundo)

print("card ending up in position {} started in position {}".format(endposition,shuffle(endposition,repundo)))

