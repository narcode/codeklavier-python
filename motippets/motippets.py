import time
from threading import Thread

import sys
import os
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
from Setup import Setup
from Mapping import Mapping_Motippets
from motippets_classes import Motippets

# Start the CodeKlavier
codeK = Setup()
myPort = codeK.perform_setup()
codeK.open_port(myPort)
device_id = codeK.get_device_id()
print('your device id is: ', device_id, '\n')

# Use your favourite mapping of the keys

mapping = Mapping_Motippets()

print("\nCodeKlavier is ready and ON.")
print("You are performing: Motippets")
print("\nPress Control-C to exit.")

# main memory (i.e. listen to the whole register)
mainMem = Motippets(mapping, device_id)

# midi listening per register
pianosectons = [47, 78, 108]
memLow = Motippets(mapping, device_id)
memMid = Motippets(mapping, device_id)
memHi = Motippets(mapping, device_id)

#midi listening for tremolos
tremoloHi = Motippets(mapping, device_id)
tremoloMid = Motippets(mapping, device_id)
tremoloLow = Motippets(mapping, device_id)

#midi listening for conditionals 
conditionals1 = Motippets(mapping, device_id)
conditionals2 = Motippets(mapping, device_id)

#multiprocessing vars
notecounter = 0

#TODO: move this function to a better place?
def parallelism(debug=True, numberOfnotes=100, result_num=1):
    print('thread started')
    
    for s in range(0, 10):
        if notecounter > numberOfnotes:
            mapping.customPass('//WOW! Anne played: ', str(notecounter)+'!!!')
            if result_num == 1:
                mapping.result(1, 'code')
                mainMem._motif2_counter = 0
                
            elif result_num == 2: #this is for snippet 1 - change the names accordingly
                mapping.result(2, 'code')
                memMid._motif1_counter = 0
            break
        else:
            mapping.customPass('//notes played: ', str(notecounter))
            conditionals1._conditionalStatus = ""
            conditionals1._resultCounter = 0
            conditionals1._conditionalCounter = 0
            conditionals2._conditionalStatus = ""
            conditionals2._resultCounter = 0
            conditionals2._conditionalCounter = 0            
            
        if debug:        
            print(notecounter)
        time.sleep(1)
        
# Loop to program to keep listening for midi input
try:
    while True:
        msg = codeK.get_message()

        if msg:
            notecounter += 1
            
            ##motifs:
            mainMem.parse_midi(msg, 'full')
            memLow.parse_midi(msg, 'low')
            memMid.parse_midi(msg, 'mid')
            memHi.parse_midi(msg, 'hi')
            ##tremolos:
            tremoloHi.parse_midi(msg, 'tremoloHi')
            tremoloMid.parse_midi(msg, 'tremoloMid')
            tremoloLow.parse_midi(msg, 'tremoloLow')
            
            ##conditionals              
            #TODO: see if this belowe can be within ONLY 1 instance of the class:
            if conditionals1.parse_midi(msg, 'conditionals') == "2 on":
                notecounter = 0 # reset the counter
                p = Thread(target=parallelism, name='conditional note counter thread', args=(True, 150, 2))
                p.start()
            if conditionals2.parse_midi(msg, 'conditionals') == "1 on":
                notecounter = 0 # reset the counter
                p = Thread(target=parallelism, name='conditional note counter thread', args=(True, 150, 1))
                p.start()                  
        
        time.sleep(0.01) #check
        
except KeyboardInterrupt:
    print('')
finally:
    print("Bye-Bye :(")
    codeK.end()

