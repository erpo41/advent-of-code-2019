#!/usr/bin/python3

#To implement for day 9:
# * parameters in relative mode

from queue import Queue
from itertools import permutations
import threading

debug = False

class iomanager:
    def __init__(self):
        # Contains dictionaries representing VMs.
        # {"name": name of VM,
        #  "inputqueue": VM's input queue
        #  "outputqueue": VM's output queue}
        registeredVMs = []
        # Contains dictionaries representing io distributors.
        # Each distributor has one input and one or more outputs.
        # The input must be a VM's output queue. The outputs may
        # be either another VM's input queue or the special stdout
        # queue. Each time an object (normally an integer) appears
        # in an io distributor's input queue, a copy is put into
        # each output queue.
        # 
        iodistributors = []

class memorymanager:
    def __init__(self,initcontents):
        self.memdict = {}
        self.load(initcontents)
    def load(self,newmem):
        if type(newmem) != type(list()):
            print("memorymanager may only be initialized with a list")
            exit(1)
        for i in range(len(newmem)):
            self.memdict[i] = newmem[i]
    def __readsingle(self,i):
        try:
            return self.memdict[i]
        except IndexError:
            return 0
    def __getitem__(self,key):
        if type(key) == type(int()):
            return self.__readsingle(key)
        elif type(key) == type(slice(1)):
            if key.step != None:
                print("memory slicing with steps not supported")
                exit(1)
            return [self.__readsingle(i) for i in range(key.start,key.stop)]
        else:
            print("unsupported memory index type: {}".format(type(index)))
            exit(1)
    def __setitem__(self,key,value):
        self.memdict[key] = value

class intcodevm:
    #instructions
    decodemap = {1: {"name":"add","parameters":3},
                 2: {"name":"multiply","parameters":3},
                 3: {"name":"input","parameters":1},
                 4: {"name":"output","parameters":1},
                 5: {"name":"jump-if-true","parameters":2},
                 6: {"name":"jump-if-false","parameters":2},
                 7: {"name":"less than","parameters":3},
                 8: {"name":"equals","parameters":3},
                 9: {"name":"adj-relbase","parameters":1},
                 99: {"name":"halt","parameters":0}}

    #parameter modes for instructions
    pmodemap = {0: "position",
                1: "immediate"}

    def __init__(self, memory, name):
        self.name = name
        self.memory = memorymanager(memory)
        self.registers = {"ip": 0,
                          "relbase": 0 }
        self.running = False
        self.inputqueue = Queue()
        self.getinput = input
        self.outputqueue = Queue()
        self.output = print

    def setinputmode(self,mode):
        if mode == "stdin":
            self.getinput = input
        elif mode == "queue":
            self.getinput = self.inputqueue.get
        else:
            print("unsupported input mode")
            exit(1)

    def queueinput(self,value):
        self.inputqueue.put(value)
            
    def setoutputfunc(self,func):
        self.output = func

    def setoutputmode(self,mode):
        if mode == "print":
            self.output = print
        elif mode == "queue":
            self.output = self.outputqueue.put

    def getoutput(self):
        return self.outputqueue.get()

    def __decode(self,ip):
        #low two digits are the instruction
        rawinstruction = self.memory[ip] % 100 
        if rawinstruction not in self.decodemap:
            print("invalid opcode {} at address {}".format(rawinstruction,ip))
            exit(1)
            
        instruction = {}
        instruction["name"] = self.decodemap[rawinstruction]["name"]
        instruction["parametercount"] = self.decodemap[rawinstruction]["parameters"]
        instruction["parameters"] = self.memory[ip+1:ip+1+instruction["parametercount"]]
        instruction["size"] = instruction["parametercount"]+1

        parametermodes = {}
        parameters = {}
        for i in range(instruction["parametercount"]):
            modebit = (self.memory[ip] // (10 ** (2+i))) % 10
            if modebit not in self.pmodemap:
                print("invalid parameter mode {} found in instruction {} at address {}".format(modebit,self.memory[ip],ip))
                exit(1)
            parametermodes[i] = self.pmodemap[modebit]
            # Fails because not all parameters are for reading.
            # Pointers must be dereferenced during execution.
            #if parametermodes[i] == "position":
            #    parameters[i] = self.memory[self.memory[ip+1+i]]
            #elif parametermodes[i] == "immediate":
            #    parameters[i] = self.memory[ip+1+i]
            #else:
            #    print("unsupported parameter mode")
            #    exit(1)
            parameters[i] =  self.memory[ip+1+i]
        instruction["parametermodes"] = parametermodes
        instruction["parameters"] = parameters
        if debug:
            print("Decoded {} to {}".format(self.memory[ip:ip+instruction["size"]],instruction))
        return instruction

    #dereferences a positional parameter if needed
    def __dereference(self,deci,paramnum):
        if deci["parametermodes"][paramnum] == "immediate":
            return deci["parameters"][paramnum]
        elif deci["parametermodes"][paramnum] == "position":
            return self.memory[deci["parameters"][paramnum]]
        else:
            print("unsupported parameter mode")
            exit(1)
    
    #executes a decoded instruction
    def __execute(self,deci):
        if deci["name"] == "add":
            summand1 = self.__dereference(deci,0)
            summand2 = self.__dereference(deci,1)
            self.memory[deci["parameters"][2]] = summand1 + summand2
            self.registers["ip"] += deci["size"]
        elif deci["name"] == "multiply":
            multiplicand1 = self.__dereference(deci,0)
            multiplicand2 = self.__dereference(deci,1)
            self.memory[deci["parameters"][2]] = multiplicand1 * multiplicand2
            self.registers["ip"] += deci["size"]
        elif deci["name"] == "input":
            self.memory[deci["parameters"][0]] = int(self.getinput())
            self.registers["ip"] += deci["size"]
        elif deci["name"] == "output":
            self.output(self.__dereference(deci,0))
            self.registers["ip"] += deci["size"]
        elif deci["name"] == "jump-if-true":
            testvalue = self.__dereference(deci,0)
            if testvalue != 0:
                self.registers["ip"] = self.__dereference(deci,1)
            else:
                self.registers["ip"] += deci["size"]
        elif deci["name"] == "jump-if-false":
            testvalue = self.__dereference(deci,0)
            if testvalue == 0:
                self.registers["ip"] = self.__dereference(deci,1)
            else:
                self.registers["ip"] += deci["size"]
        elif deci["name"] == "less than":
            if self.__dereference(deci,0) < self.__dereference(deci,1):
                self.memory[deci["parameters"][2]] = 1
            else:
                self.memory[deci["parameters"][2]] = 0
            self.registers["ip"] += deci["size"]
        elif deci["name"] == "equals":
            if self.__dereference(deci,0) == self.__dereference(deci,1):
                self.memory[deci["parameters"][2]] = 1
            else:
                self.memory[deci["parameters"][2]] = 0
            self.registers["ip"] += deci["size"]
        elif deci["name"] == "adj-relbase":
            self.registers["relbase"] += self.__dereference(deci,0)
            self.registers["ip"] += deci["size"]
        elif deci["name"] == "halt":
            self.running = False
        else:
            print("execution of instruction '{}' not supported".format(deci["name"]))
            exit(1)
    
    def run(self):
        self.running = True
        while(self.running):
            deci = self.__decode(self.registers["ip"])
            self.__execute(deci)
        
if __name__ == "__main__":
    with open('program.txt') as f:
        memory = [int(x) for x in f.readline().split(",")]
    results = []
    for permutation in permutations([5,6,7,8,9]):
        A = intcodevm(memory=memory,name="A")
        A.setinputmode("queue")
        A.queueinput(permutation[0])
        A.queueinput(0)
        B = intcodevm(memory=memory,name="B")
        B.setinputmode("queue")
        B.queueinput(permutation[1])
        C = intcodevm(memory=memory,name="C")
        C.setinputmode("queue")
        C.queueinput(permutation[2])
        D = intcodevm(memory=memory,name="D")
        D.setinputmode("queue")
        D.queueinput(permutation[3])
        E = intcodevm(memory=memory,name="E")
        E.setinputmode("queue")
        E.queueinput(permutation[4])
        A.setoutputfunc(B.queueinput)
        B.setoutputfunc(C.queueinput)
        C.setoutputfunc(D.queueinput)
        D.setoutputfunc(E.queueinput)
        E.setoutputfunc(A.queueinput)
        Athread = threading.Thread(group=None,target=A.run)
        Bthread = threading.Thread(group=None,target=B.run)
        Cthread = threading.Thread(group=None,target=C.run)
        Dthread = threading.Thread(group=None,target=D.run)
        Ethread = threading.Thread(group=None,target=E.run)
        threads = [Athread, Bthread, Cthread, Dthread, Ethread]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        #print(permutation)
        results.append({"permutation":permutation,"thrustvalue":A.getinput()})
    results.sort(key=lambda x:x["thrustvalue"],reverse=True)
    print(results[0])
