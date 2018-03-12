#!/usr/bin/env python3

"""
CK listening server to display code from a specific piano register.

* used for Madrid INSONORA Festival 2018

TODO: Classify this

"""

import socket
import getopt
import sys

# Gui
from threading import Thread
import tkinter
ck_display = {}
f = {}

#server socket
listen = True
s = {}
codedump = {}
s['1'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s['2'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s['3'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#s.setblocking(False)

def main():
    """
    create the UDP server and display based on commandline arguments
    """
    global root, display
    
    display = 0
    
    try:
        options, args = getopt.getopt(sys.argv[1:],'hd:',['help', 'display='])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    
    for o, a in options:
        if o in ('-h', '--help'):
            showUsage()
            sys.exit(2)
        if o in ('-d', '--display'):
                try:
                    if int(a) < 4 and int(a) > 0:                    
                        display = a
                    else:
                        print('argument should be either 1, 2 or 3')
                        sys.exit(2)                        
                except ValueError:
                    print('argument should be either 1, 2 or 3')
                    sys.exit(2)
        else:
            assert False, 'unhandled option'
    
    if int(display) > 0:
        # Gui window
        root = tkinter.Tk()
        root.title('CK PARALLEL CODING DISPLAY')
        root.attributes('-topmost', True)
        root.geometry("1920x900")
        root.config(background='black')
        
        # onClose event:
        root.protocol("WM_DELETE_WINDOW", stopThreads)         
                     
    if int(display) == 1:  
        f[display] = tkinter.Frame(root, height=900, width=1920/3) 
        f[display].pack(fill=tkinter.Y, side=tkinter.LEFT)
        f[display].pack_propagate(0)        
        ck_display[display] = tkinter.Text(f[display], height=6, width=50)
        ck_display[display].pack(fill=tkinter.Y, side=tkinter.LEFT)
        ck_display[display].configure(bg='black',fg='cyan',wrap=tkinter.WORD,spacing1=0.3, font='MENLO 25')
        
        ck_display[display].insert(tkinter.END, "Snippet 1\n")        
        s[display].bind(('localhost', 1111))
        print('CK display 1 listening on port 1111')

        # display thread:
        codedump[display] = Thread(target=displayCode, args=('1'))        
        codedump[display].start() 

        tkinter.mainloop()
        
        closeDisplay(display)
                
    elif int(display) == 2:       
        print('CK displays 1 & 2 listening on port 1111 & 2222')

        for x in range(1, int(display)+1):
            
            s[str(x)].bind(('localhost', x*1111))
            
            f[str(x)] = tkinter.Frame(root, height=900, width=1920/3) 
            f[str(x)].pack(fill=tkinter.Y, side=tkinter.LEFT)
            f[str(x)].pack_propagate(0)              
            ck_display[str(x)] = tkinter.Text(f[str(x)], height=6, width=50)
            ck_display[str(x)].pack(fill=tkinter.Y, side=tkinter.LEFT)
            ck_display[str(x)].configure(bg='black',fg='cyan',wrap=tkinter.WORD,spacing1=0.3, font='MENLO 20')
            ck_display[str(x)].insert(tkinter.END, "Snippet "+str(x)+" \n")            

            codedump[str(x)] = Thread(target=displayCode, args=(str(x)))        
            codedump[str(x)].start()         

        tkinter.mainloop()
        
        closeDisplay(display)        
        
    elif int(display) == 3:
        print('CK displays 1-3 listening on ports 1111, 2222 & 3333')

        s_width = root.winfo_screenwidth()
        s_height = root.winfo_screenheight()
        
        for x in range(1, int(display)+1):
            
            s[str(x)].bind(('localhost', x*1111))
            
            f[str(x)] = tkinter.Frame(root, height=s_height, width=s_width/3) 
            f[str(x)].pack(fill=tkinter.Y, side=tkinter.LEFT)
            f[str(x)].pack_propagate(0) 
            f[str(x)].configure(bg='black', bd=3)                          
            
            ck_display[str(x)] = tkinter.Text(f[str(x)], height=6, width=50)
            ck_display[str(x)].pack(expand=True, fill=tkinter.BOTH)
            ck_display[display].tag_config('var', foreground='white')
            
            if x ==1:
                ck_display[str(x)].configure(bg='black', bd=5, fg='cyan',wrap=tkinter.WORD,spacing1=0.3, font='MENLO 20', relief=tkinter.SUNKEN)
                ck_display[str(x)].insert(tkinter.END, "Snippet "+str(x)+" \n")
            elif x == 2:
                ck_display[str(x)].configure(bg='black', bd=5, fg='magenta',wrap=tkinter.WORD,spacing1=0.3, font='MENLO 20', relief=tkinter.SUNKEN)
                ck_display[str(x)].insert(tkinter.END, "Snippet "+str(x)+" \n")
            elif x == 3:
                ck_display[str(x)].configure(bg='black', bd=5, fg='yellow',wrap=tkinter.WORD,spacing1=0.3, font='MENLO 20', relief=tkinter.SUNKEN)
                ck_display[str(x)].insert(tkinter.END, "Conditionals and other stuff \n")                
            
            
            codedump[str(x)] = Thread(target=displayCode, args=(str(x)))        
            codedump[str(x)].start()         


        tkinter.mainloop()
        
        closeDisplay(display)         
        
def stopThreads():
    """
    stop the thread handling the udp socket
    """
    global listen, root
    
    listen = False
    root.destroy()

def closeDisplay(display):  
    """
    close the GUI window
    """   
    if display == '1':
        s[display].sendto(bytes("Bye Bye CK", "utf-8"), ('localhost', 1111))    
    elif display == '2':
        s[display].sendto(bytes("Bye Bye CK", "utf-8"), ('localhost', 2222))  
        s['1'].sendto(bytes("Bye Bye CK", "utf-8"), ('localhost', 1111)) 
    elif display == '3':
        s[display].sendto(bytes("Bye Bye CK", "utf-8"), ('localhost', 3333))  
        s['1'].sendto(bytes("Bye Bye CK", "utf-8"), ('localhost', 1111))         
        s['2'].sendto(bytes("Bye Bye CK", "utf-8"), ('localhost', 2222))         
        
    print('\nBye Bye from the CodeKlavier display server...')
    sys.exit(0)
    
def showUsage():
    print('\nusage example:', 
                      'python3 CK_socket -d 3\n')    
    
def displayCode(display):     
    """
    Funtion to listen for incoming UDP stream.
    Handeld by parallel thread
    
    """
    global ck_display
    
    while listen:
        try:
            if display == '1':
                data, addr = s[display].recvfrom(1024)
                #print(str(data, 'utf-8'))
                dump = str(data, 'utf-8')
                try:
                    ck_display[display].insert(tkinter.END, dump)
                    ck_display[display].see(tkinter.END)
                except RuntimeError as err:
                    break
            elif display == '2':
                data, addr = s[display].recvfrom(1024)
                #print(str(data, 'utf-8'))
                dump = str(data, 'utf-8')
                try:
                    ck_display[display].insert(tkinter.END, dump)
                    ck_display[display].see(tkinter.END)
                except RuntimeError as err:
                    break      
            elif display == '3':
                data, addr = s[display].recvfrom(1024)
                #print(str(data, 'utf-8'))
                dump = str(data, 'utf-8')
                try:
                    ck_display[display].insert(tkinter.END, dump)
                    ck_display[display].see(tkinter.END)
                except RuntimeError as err:
                    break                   
        except OSError as err:
            print(err)
            break
        
if __name__ == '__main__':
    try: 
        main()
        
        # show usage
        if int(display) == 0:
            showUsage()
        
            
    except KeyboardInterrupt:
        stopThreads()
        closeDisplay()