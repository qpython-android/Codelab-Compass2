from kivy.support import install_twisted_reactor
install_twisted_reactor()

import re
import hashlib
import os.path
from kivy.app import App
from kivy.uix.widget import Widget

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivy.properties import ObjectProperty, StringProperty

from twisted.internet import reactor
from twisted.internet import protocol

def read_bytes_from_file(file, chunk_size = 8100):
    """ Read bytes from a file in chunks. """
    
    with open(file, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            
            if chunk:
                yield chunk
            else:
                break

def get_file_md5_hash(file):
    """ Returns file MD5 hash"""
    
    md5_hash = hashlib.md5()
    for bytes in read_bytes_from_file(file):
        md5_hash.update(bytes)
        
    return md5_hash.hexdigest()


class EchoProtocol(protocol.Protocol):
    isFileTransfer = False
    fileSize = 0
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data)
        if response:
            if isFileTransfer:
                self.transport.write(".")
            else:
                if re.search(L_CMD_FILE_S, response):
                    isFileTransfer = True
                    self.transport.write("FILE")
                elif re.search(L_CMD_FILE_E, response):
                    isFileTransfer = False
                    self.transport.write("EOF")
                else:
                    self.transport.write(response)

class EchoFactory(protocol.Factory):
    protocol = EchoProtocol
    def __init__(self, app):
        self.app = app

G_NODES     = set([])
G_MESSAGE   = ''
G_FILE      = ''
G_ISMSG_MODE= True

G_CMD_ADD   = re.compile('^add\s+(.+:[0-9]+)')
G_CMD_DEL   = re.compile('^del\s+(.+:[0-9]+)')
G_CMD_LIST  = re.compile('^list')
G_CMD_MSG   = re.compile('^msg\s+(.*)')
G_CMD_FILE  = re.compile('^file\s+(.*)')
G_CMD_QUIT  = re.compile('^clear')
G_CMD_HELP  = re.compile('^help')

L_CMD_FILE_S= re.compile('^FILE\s+(.+)\s+(.+)\s+(.+)')
L_CMD_FILE_E= re.compile('^EOF')

G_HELP      = """Compass2 (by http://qpython.org/compass2) 
> add <host:port> : Add the server to the list
> del <host:port> : Del the server from the list 
> list : list all nodes
> msg <message> : send a message to nodes list
> file <filename> : send a file to nodes list
> clear : delete all nodes"""

G_cmdResult = Label(text=G_HELP,font_size=25)
G_cmdInput  = TextInput(text='',font_size=40)

G_cmdBtnLayout = BoxLayout(orientation='vertical',size_hint_x=None,width=200)

class EchoClient(protocol.Protocol):
    """
    @Main entrance for handling the response from server in client side
    """

    def connectionMade(self):
        if G_ISMSG_MODE:
            self.transport.write(G_MESSAGE)
            print_message("Client", 'sending message "%s"' % G_MESSAGE)
        else:
            #self.transport.write('FILE')
            file_size = os.path.getsize(G_FILE) 
            line = "FILE %s %s %s\n" % (os.path.basename(G_FILE), get_file_md5_hash(G_FILE), file_size)
            self.transport.write(line)
            print_message("Client", line)

            for bytes in read_bytes_from_file(G_FILE):
                self.transport.write(bytes)

            self.transport.write("EOF\n")

            print_message("Client", "FILE EOF")


    """
    @Main entrance for handling the response from server in client side
    """
    def dataReceived(self, data):
        print_message("Client", 'dataReceived %s' % data)

"""
class EchoClientFactory(protocol.ClientFactory):
    protocol = EchoClient
    def __init__(self, app):
        print_message("Client", "connection init")

    def clientConnectionLost(self, conn, reason):
        print_message("Client", "connection lost")

    def clientConnectionFailed(self, conn, reason):
        print_message("Client", "connection failed")
"""

def on_text_validate_cmd_input(instance, val):
    global G_MESSAGE 
    global G_ISMSG_MODE 
    global G_FILE 
    if val=='':
        G_cmdResult.text = G_HELP
    else:
        lines = val.split("\n")
        if lines[-1] == "":
            cmd = lines[-2]
            cmdFlag = False

            xx = re.search(G_CMD_ADD, cmd)
            if xx:
                cmdFlag = True
                G_NODES.update([str(xx.groups()[0])])

                print_message("Compass", '%s' % cmd)

            xx = re.search(G_CMD_DEL, cmd)
            if xx:
                cmdFlag = True
                G_NODES.discard(str(xx.groups()[0]))

                print_message("Compass", '%s' % cmd)

            xx = re.search(G_CMD_MSG, cmd)
            if xx:
                cmdFlag = True
                G_ISMSG_MODE = True
                G_MESSAGE = str(xx.groups()[0])
                print_message("Compass", '%s will be send to %s nodes' % (G_MESSAGE, len(G_NODES)))

                for xx in G_NODES:
                    item = xx.split(':')
                    #G_cmdResult.text = '%s %s:%s' % (G_cmdResult.text, item[0], item[1])
                    #reactor.connectTCP(item[0], int(item[1]), EchoClientFactory(self))
                    protocol.ClientCreator(reactor, EchoClient).connectTCP(item[0], int(item[1]))
                    #G_cmdResult.text = 'sendto %s' % (socket,)

            xx = re.search(G_CMD_FILE, cmd)
            if xx:
                cmdFlag = True
                G_ISMSG_MODE = False
                G_FILE = str(xx.groups()[0])
                print_message("Compass", 'File %s will be send to %s nodes' % (G_MESSAGE, len(G_NODES)))

                for xx in G_NODES:
                    item = xx.split(':')
                    #G_cmdResult.text = '%s %s:%s' % (G_cmdResult.text, item[0], item[1])
                    #reactor.connectTCP(item[0], int(item[1]), EchoClientFactory(self))
                    protocol.ClientCreator(reactor, EchoClient).connectTCP(item[0], int(item[1]))
                    #G_cmdResult.text = 'sendto %s' % (socket,)


            xx = re.search(G_CMD_LIST, cmd)
            if xx:
                cmdFlag = True
                print_message("Compass", "There are %s nodes : %s" % (len(G_NODES), str(list(G_NODES))))

            xx = re.search(G_CMD_QUIT, cmd)
            if xx:
                cmdFlag = True
                G_NODES.clear()
                print_message("Compass", 'There is no node')

            xx = re.search(G_CMD_HELP, cmd)
            if xx:
                cmdFlag = True
                G_cmdResult.text = G_HELP
            

            if not cmdFlag:
                G_cmdResult.text = 'Please input correct command'

        else:
            pass

def on_press_display_console(instance):
    G_cmdResult.text = G_HELP
    

def on_press_clear_submit(instance):
    G_cmdResult.text = ''

def on_press_cmd_submit(instance):
    cmd = G_cmdInput.text.strip()
    if cmd.find('help') == 0: # HELP
        G_cmdResult.text = '%s is executing...' % cmd
    else:
        G_cmdResult.text = G_HELP

class CompassApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        title = Label(text='Compass Console',font_size=30,size_hint_y=None,height=60)
        layout.add_widget(title)

        topLayout = GridLayout(cols=3, size_hint_y=None, height=80)
        servBtn = Button(text='Start server')
        def on_press_serve_submit(instance):
            if servBtn.text=='Start server':
                reactor.listenTCP(8000, EchoFactory(self))
                print_message("Compass", 'server started, serve on 8000')
                servBtn.text='Stop server'
            else:
                reactor.stop()
                servBtn.text='Start server'
                print_message("Compass", 'server stoped')
        topLayout.add_widget(servBtn)

        consoleBtn = Button(text='help')
        consoleBtn.bind(on_press=on_press_display_console)
        topLayout.add_widget(consoleBtn)

        clearBtn = Button(text='Clear')
        clearBtn.bind(on_press=on_press_clear_submit)
        topLayout.add_widget(clearBtn)

        layout.add_widget(topLayout)

        cmdLayout = GridLayout(cols=1)

        G_cmdInput.bind(text=on_text_validate_cmd_input)
        cmdLayout.add_widget(G_cmdInput)

        #cmdBtn = Button(text='Execute')
        #cmdBtn.bind(on_press=on_press_cmd_submit)

        servBtn.bind(on_press=on_press_serve_submit)

        #G_cmdBtnLayout.add_widget(cmdBtn) 
        #G_cmdBtnLayout.add_widget(clearBtn)
        #cmdLayout.add_widget(G_cmdBtnLayout)

        layout.add_widget(cmdLayout)

        resultLayout = BoxLayout()
        resultLayout.add_widget(G_cmdResult)
        layout.add_widget(resultLayout)

        return layout

    """
    @Main entrance for handling the msg in server side
    """
    def handle_message(self, msg):
        if msg == "ping":  msg =  "pong"
        if msg == "plop":  msg = "kivy rocks"
        print_message("Server", "responded: %s\n" % msg)
        return msg

    def on_connection(self, connection):
        print_message("Compass", "connected succesfully!")
        self.connection = connection

def print_message(cat, msg):
    if G_cmdResult.text==G_HELP:
        G_cmdResult.text = "[%s] %s" % (cat, msg)
    else:
        xx = "%s\n[%s] %s" % (G_cmdResult.text, cat, msg)
        xx = xx.strip()
        lines = xx.split("\n")

        if len(lines)>7:
            G_cmdResult.text = "\n".join(lines[len(lines)-7:])
        else:
            G_cmdResult.text = xx



if __name__ == '__main__':
    CompassApp().run()
