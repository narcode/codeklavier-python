"""Mapping.py

Contains the classes ``Mapping_HelloWorld``, ``Mapping_HelloWorld_NKK`` and
``Mapping_Motippets``. These class deal with the mapping of the (midi) keys to
chars, strings and commands.

TODO: make a single base class and subclass the different versions from that
class.
"""
import time
from pynput.keyboard import Key, Controller
import socket
from pythonosc import udp_client
import configparser
import re

display1 = 1111
display2 = 2222
display3 = 3333
display4 = 4444
display5 = 5555

class Mapping_Motippets:
    """Mapping for the Motippets prototype.

       Includes Hello World mappings for the Hybrid prototype
    """
    def __init__(self, debug=True, snippets='snippets code output'):
        if debug:
            print("## Using the Motippets mapping ##")

        self._config = configparser.ConfigParser(delimiters=(':'), comment_prefixes=('#'))
        self._config.read('default_setup.ini', encoding='utf8')

        self.__keyboard = Controller()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._osc = udp_client.SimpleUDPClient('127.0.0.1', 57120) #standard supercollider OSC listening port

    def evaluateSC(self, what, flash=True, display=5):
        """Evaluate the SuperCollider command 'what'

        :param string what: the command that should be evaluated
        :param bool flash: should eval command flash the screen
        :param int display: the display number that should flash to indicate evaluation
        """
        if flash:
            self.formatAndSend('evaluate:', display=display)
        if what == 'play':
            with self.__keyboard.pressed(Key.cmd):
                self.__keyboard.press(Key.right)
                self.__keyboard.release(Key.right)
            time.sleep(0.01)
            self.__keyboard.type('.play')
            with self.__keyboard.pressed(Key.shift):
                self.__keyboard.press(Key.enter)
                self.__keyboard.release(Key.enter)
            time.sleep(0.01)
            self.__keyboard.press(Key.enter)
            self.__keyboard.release(Key.enter)
        elif what == 'stop':
            with self.__keyboard.pressed(Key.cmd):
                self.__keyboard.press(Key.right)
                self.__keyboard.release(Key.right)
            time.sleep(0.01)
            self.__keyboard.type('.stop')
            with self.__keyboard.pressed(Key.shift):
                self.__keyboard.press(Key.enter)
                self.__keyboard.release(Key.enter)
            time.sleep(0.01)
            self.__keyboard.press(Key.enter)
            self.__keyboard.release(Key.enter)
        elif what == 'alt_eval':
            with self.__keyboard.pressed(Key.cmd):
                self.__keyboard.type('e')
                self.__keyboard.release(Key.cmd)
        elif what == 'eval':
            with self.__keyboard.pressed(Key.shift):
                self.__keyboard.press(Key.enter)
                self.__keyboard.release(Key.enter)
            time.sleep(0.2)
            self.__keyboard.press(Key.enter)
            self.__keyboard.release(Key.enter)
        elif what == 'noEnter_eval':
            with self.__keyboard.pressed(Key.shift):
                self.__keyboard.press(Key.enter)
                self.__keyboard.release(Key.enter)

    def goDown(self, display=5):
        """Press command-arrow down and enter.
        
        :param int display: the display number to which to send the udp messages
        """
        self.formatAndSend('\n', display=display, syntax_color='hello:', spacing=False)

        with self.__keyboard.pressed(Key.cmd):
            self.__keyboard.press(Key.down)
            self.__keyboard.release(Key.down)
        time.sleep(0.2)
        self.__keyboard.press(Key.enter)
        self.__keyboard.release(Key.enter)

    def enter(self):
        """Press the enter key.
        """
        self.__keyboard.press(Key.enter)
        self.__keyboard.release(Key.enter)

    def delete(self):
        """Press the backspace key.
        """
        self.__keyboard.press(Key.backspace)
        self.__keyboard.release(Key.backspace)

    def mapping(self, midinumber, prototype='Hello World', display=5, debug=False):
        """Type a letter that is coupled to this midi note.

        :param int midinumber: the midinumber that is played
        :param string prototype: the section to grab from the config.ini file. Normally related to the prototype being played
        :param int display: the display number to which to send the udp messages
        :param boolean debug: print or not debug messages in the console
        """
        try:
            midis = str(midinumber)
            if midis in self._config[prototype]:
                if debug:
                    print(midinumber, self._config[prototype].get(midis))
                mapped_string = self._config[prototype].get(midis)

                if len(mapped_string) < 2:
                    # chars and nums
                    self.__keyboard.type(mapped_string)
                    self.formatAndSend(mapped_string, display=display, syntax_color='hello:', spacing=False)
                else:
                    # strings
                    string = re.findall('^\'.*', mapped_string)
                    if len(string) > 0:
                        mapped_string = string[0].replace("\'","")
                        self.__keyboard.type(mapped_string)
                        self.formatAndSend(mapped_string, display=display, syntax_color='hello:', spacing=False)

                    # special keys
                    if mapped_string == 'space':
                        self.__keyboard.press(Key.space)
                        self.__keyboard.release(Key.space)
                        self.formatAndSend(' ', display=display, syntax_color='hello:', spacing=False)
                    elif mapped_string == 'enter':
                        self.__keyboard.press(Key.enter)
                        self.__keyboard.release(Key.enter)
                        self.formatAndSend('\n', display=display, syntax_color='hello:', spacing=False)
                    elif mapped_string == 'backspace':
                        self.__keyboard.press(Key.backspace)
                        self.__keyboard.release(Key.backspace)
                        self.formatAndSend('', display=display, syntax_color='delete:', spacing=False)
                    elif mapped_string == 'down':
                        self.goDown()
                        self.formatAndSend('\n', display=display, syntax_color='hello:', spacing=False)
                    elif mapped_string == 'sc-evaluate':
                        self.evaluateSC('noEnter_eval', flash=display==5)
                        self.formatAndSend('', display=display, syntax_color='hello:', spacing=False)
                    elif mapped_string == '.tempo':
                        self.__keyboard.type(mapped_string)
                        self.formatAndSend(mapped_string, display=display, syntax_color='hello:', spacing=False)
                    elif mapped_string == '.play':
                        self.__keyboard.type(mapped_string)
                        self.formatAndSend(mapped_string, display=display, syntax_color='hello:', spacing=False)
                    elif mapped_string == '.load' or mapped_string == '.close':
                        self.__keyboard.type(mapped_string)
                        self.formatAndSend(mapped_string, display=display, syntax_color='hello:', spacing=False)
                    elif mapped_string == 'motippetssc-evaluate':
                        self.evaluateSC('eval', flash=display==5)
        except KeyError:
            raise LookupError('Missing hello world information in the config file.')

    def formatAndSend(self, msg='', encoding='utf-8', host='localhost', display=1, syntax_color='', spacing=True):
        """format and prepare a string for sending it over UDP socket

        :param str msg: the string to be sent
        :param str encoding: the character encoding
        :param str host: the UDP server hostname
        :param int display: the UDP destination port
        :param str syntax_color: the tag to use for syntax coloring (loop, primitive, mid, low, hi, snippet)
        :param boolean spacing: wheather to put a \n (new line) before the msg
        """

        if display == 1:
            port = 1111
        elif display == 2:
            port = 2222
        elif display == 3:
            port = 3333
        elif display == 4:
            port = 4444
        elif display == 5:
            port = 5555
        else:
            port = 1111

        if spacing:
            newline = '\n'
        else:
            newline = ''

        return self.__socket.sendto(bytes(syntax_color+newline+msg, encoding), (host, port))

    def snippets(self, motif, configfile='default_setup.ini'):
        """Type code snippets

        :param str motif: the name of the motif to map
        :param str configfile: the name of the config file to parse
        """
        displays = [1,2]
        #num = re.search(r"\d", motif).group()
            
        #display = displays[(int(num)-1)%len(displays)]        
        try:
            display = self._config['motippets display settings'].getint(motif)                         
            snippet = self._config['snippets code output'].get(motif)
            self.__keyboard.type(snippet)
            self.formatAndSend(snippet, display=display, syntax_color='snippet:')
            self.evaluateSC('eval', flash=False)
        except KeyError:
            print(motif, 'does not exists in the snippets code output section of .ini file')

    def miniSnippets(self, motif, pianosection, callback=None):
        """Type a mini snippet for specific pianosections'utf-8'

        :param str motif: the name of the motif mapped to the desired snippet
        :param str pianosections: the pianosection that is used ('hi', 'mid', 'low')
        :param str motif: the name of the motif to unmap 
        """
        
        try:
            display = self._config['motippets display settings'].getint(motif)             
            snippet = self._config['snippets code output'].get(motif)
        except KeyError:
            print(motif, 'missing in snippets code output or motippets display settings')
        
        if display == None:
            display = '### no display setting for ' + motif + ' in .ini ###'
        if snippet == None:
            snippet = '### code output error with ' + motif + ' (check .ini) ###'
        
        if callback == None:
            self.__keyboard.type(snippet)
            self.evaluateSC('eval', flash=False)
            self.formatAndSend(snippet, display=display, syntax_color=pianosection+':')  
        else:           
            self.__keyboard.type(snippet)
            self.evaluateSC('eval', flash=False)
            self.formatAndSend(snippet, display=display, syntax_color=pianosection+':')

            callback_snippet = self._config['snippets code output callback'].get(callback)            
            if callback_snippet == None:
                callback_snippet = '### callback error with ' + callback + ' (check .ini) ###'
                
            self.__keyboard.type(callback_snippet)
            self.evaluateSC('eval', flash=False)
            self.formatAndSend(callback_snippet, display=display, syntax_color='low:')
            
    def tremolo(self, motif, value, syntax_color):
        """Type the tremolo command + the tremolo-value

        :param string motif: the motif name to be mapped and prependend to the tremolo value.
        :param int value: the tremolo value as distance between the notes
        """
            
        code = self._config['snippets for tremolos'].get(motif)
        display = self._config['motippets display settings'].getint(motif)
        
        if display == None:
            display = '### no display setting for ' + motif + ' in .ini ###'
        if code == None:
            print('### tremolo error with ' + motif + ' (check .ini) ###')
        
        if code != None:
            self.__keyboard.type(code + ' ' + str(value))
            self.formatAndSend(code + ' ' + str(value), display=display, syntax_color=syntax_color+':')
        
        flash = display == 5
        self.evaluateSC('eval', flash=flash)

    def conditional(self, motif):
        """Setup a conditional
        
        :param str motif: the motif name that corresponds to the code output in the .ini file

        There are three options:
        
        1. setting up a conditional if number of notes
        played is more than 100 in ...
        
        2. setting up a conditional if
        range is more than ... 
        
        3.setting up a conditional if range
        is less than ...
        
        """
        
        code = self._config['snippets code output'].get(motif)
        
        if code == None:
            code = '### code output error with ' + motif + ' (check .ini) ###'        
        
        self.__keyboard.type(code)
        self.enter()
        self.formatAndSend(code, display=3, syntax_color='primitive:')        

    def result(self, motif_name, text, mod=0, flags=None):
        """TOOD: document function

        :param str motif_name: motif name coresponding to the desired result
        :param string text: indication of the type of message
        :param int mod: a value passed from the calling function
        """
        display = 3
        syntax_color = self._config['motippets display settings'].get(motif_name)
        
        if flags in ('gomb', ):
            output = [r.strip() for r in self._config['snippets code output'].get(motif_name+'_'+text).split(',')]            
            self.__keyboard.type('GOMB countdown started!')
            self.evaluateSC('eval', flash=False)
            self.formatAndSend('boom:GOMB', display=1)
            self.formatAndSend('boom:COUNTDOWN', display=2)
            self.formatAndSend('boom:STARTED!', display=3) 
        else:
            if text == 'comment':
                output = self._config['snippets code output'].get(motif_name+'_comment')
                self.__keyboard.type(output)
                self.enter()
                self.formatAndSend(output, display=display, syntax_color='primitive:')
            elif text in ('true', 'false'):
                output = [r.strip() for r in self._config['snippets code output'].get(motif_name+'_'+text).split(',')]
                if 'osc' in output:
                    if 'grab_value' in output:
                        self._osc.send_message("/" + output[2], str(mod)) 
                    else:
                        self._osc.send_message("/" + output[2], output[3])             
                else:
                    self.__keyboard.type(output[0])
                    self.evaluateSC('eval', flash=False)
                    
                self.formatAndSend(output[0], display=display, syntax_color='snippet:')                    
                        
    def customPass(self, content, syntax_color=None, display_only=False, flash=False, display=3):
        """
        post custom string message on codespace and display

        :param string content: the message or content
        :param str syntax_color: the reference name for a display color        
        :param bool display_only: flag to only send content to display and ignore normal typing
        :param bool falsh: execute a brief flashing in the display
        """

        if not display_only:
            self.__keyboard.type(content)
            self.enter()

        if flash:
            content = 'flash:' + content
            
        if syntax_color == None:
            syntax_color = 'comment'
            
        self.formatAndSend(content, display=display, syntax_color=syntax_color+':')
        
    def gomb(self):
        """
        special function to end a coding session/perfromance with a BANG
        """
        for i in range(1, 4):
            for display_num in range(1, 6):
                self.formatAndSend('KILL:red', display=display_num)
            time.sleep(0.1)
            for display_num in range(1, 6):
                self.formatAndSend('KILL:black', display=display_num)
            time.sleep(0.1)
        
        self.__keyboard.type("")
        self.enter()
        self.__keyboard.type("  ____   ____   ____  __  __ _ ")
        self.enter()
        self.formatAndSend(" ____ ", display=5, syntax_color='primitive:')
        self.formatAndSend("  ____  ", display=1, syntax_color='primitive:')
        self.formatAndSend("  ____  ", display=2, syntax_color='primitive:')
        self.formatAndSend(" __  __  ", display=3, syntax_color='primitive:')
        self.formatAndSend(" _ ", display=4, syntax_color='primitive:')
        self.__keyboard.type(" |  _ \ / __ \ / __ \|  \/  | |")
        self.enter()
        self.formatAndSend("|  _ \ ", display=5, syntax_color='primitive:')
        self.formatAndSend(" / __ \ ", display=1, syntax_color='primitive:')
        self.formatAndSend(" / __ \ ", display=2, syntax_color='primitive:')
        self.formatAndSend("|  \/  |", display=3, syntax_color='primitive:')
        self.formatAndSend("| | ", display=4, syntax_color='primitive:')
        self.__keyboard.type(" | |_) | |  | | |  | | \  / | |")
        self.enter()
        self.formatAndSend("| |_) | ", display=5, syntax_color='primitive:')
        self.formatAndSend("| |  | |", display=1, syntax_color='primitive:')
        self.formatAndSend("| |  | |", display=2, syntax_color='primitive:')
        self.formatAndSend("| \  / |", display=3, syntax_color='primitive:')
        self.formatAndSend("| | ", display=4, syntax_color='primitive:')
        self.__keyboard.type(" |  _ <| |  | | |  | | |\/| | |")
        self.enter()
        self.formatAndSend("|  _ <| ", display=5, syntax_color='primitive:')
        self.formatAndSend("| |  | |", display=1, syntax_color='primitive:')
        self.formatAndSend("| |  | |", display=2, syntax_color='primitive:')
        self.formatAndSend("| |\/| |", display=3, syntax_color='primitive:')
        self.formatAndSend("| | ", display=4, syntax_color='primitive:')
        self.__keyboard.type(" | |_) | |__| | |__| | |  | |_|")
        self.enter()
        self.formatAndSend("| |_) | ", display=5, syntax_color='primitive:')
        self.formatAndSend("| |__| |", display=1, syntax_color='primitive:')
        self.formatAndSend("| |__| |", display=2, syntax_color='primitive:')
        self.formatAndSend("| |  | |", display=3, syntax_color='primitive:')
        self.formatAndSend("|_| ", display=4, syntax_color='primitive:')
        self.__keyboard.type(" |____/ \____/ \____/|_|  |_(_)")
        self.enter()
        self.formatAndSend("|____/", display=5, syntax_color='primitive:')
        self.formatAndSend(" \____/", display=1, syntax_color='primitive:')
        self.formatAndSend(" \____/", display=2, syntax_color='primitive:')
        self.formatAndSend("|_|  |_|", display=3, syntax_color='primitive:')
        self.formatAndSend("(_)", display=4, syntax_color='primitive:')
        self.__keyboard.type("")
        self.enter()        


class Mapping_Ckalculator:
    """Mapping for the Ckalculator prototype.
    """
    def __init__(self, use_display=False, debug=True):
        if debug:
            print("## Using the Ckalculator mapping ##")

        self.__keyboard = Controller()

        if use_display:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._osc = udp_client.SimpleUDPClient('127.0.0.1', 57120)


    def formatAndSend(self, msg='', encoding='utf-8', host='localhost', display=1, syntax_color=':', spacing=True, spacechar=' '):
        """format and prepare a string for sending it over UDP socket

        :param str msg: the string to be sent
        :param str encoding: the character encoding
        :param str host: the UDP server hostname
        :param int display: the UDP destination port
        :param str syntax_color: the tag to use for syntax coloring (loop, primitive, mid, low, hi, snippet)
        :param boolean spacing: wheather to put a \n (new line) before the msg
        :param boolean spacechar: the character to place in between the msgs. Can be ''
        """

        if display == 1:
            port = 1111
        elif display == 2:
            port = 2222
        elif display == 3:
            port = 3333
        elif display == 4:
            port = 4444        

        if spacing:
            newline = '\n'
        else:
            newline = spacechar

        return self.__socket.sendto(bytes(syntax_color+msg+newline, encoding), (host, port))

    def newLine(self, display=1):
        """
        send a new line to the code display
        """
        if display == 1:
            port = 1111
        elif display == 2:
            port = 2222
        elif display == 3:
            port = 3333
        elif display == 4:
            port = 4444 
            
        return self.__socket.sendto(bytes('line:\n', 'utf-8'), ('localhost', port))
