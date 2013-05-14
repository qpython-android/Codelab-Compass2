from kivy.support import install_twisted_reactor
install_twisted_reactor()

import re

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

class EchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data)
        if response:
            self.transport.write(response)

class EchoFactory(protocol.Factory):
    protocol = EchoProtocol
    def __init__(self, app):
        self.app = app

G_NODES     = set([])
G_MESSAGE   = ''

G_CMD_ADD   = re.compile('^add\s+(.+:[0-9]+)')
G_CMD_DEL   = re.compile('^del\s+(.+:[0-9]+)')
G_CMD_LIST  = re.compile('^list')
G_CMD_MSG   = re.compile('^msg\s+(.*)')
G_CMD_QUIT  = re.compile('^clear')
G_CMD_HELP  = re.compile('^help')

G_HELP      = """Compass2 (by http://qpython.org/compass2) 
> add <host:port> : Add the server to the list
> del <host:port> : Del the server from the list 
> list : list all nodes
> msg <message> : send a message to server list
> clear : delete all nodes"""
G_cmdResult = Label(text=G_HELP,font_size=25)
G_cmdInput  = TextInput(text='',font_size=40)

G_cmdBtnLayout = BoxLayout(orientation='vertical',size_hint_x=None,width=200)


class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.transport.write(G_MESSAGE)
        print_message("Client", 'sending message "%s"' % G_MESSAGE)

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

                print_message("Desktop", '%s' % cmd)

            xx = re.search(G_CMD_DEL, cmd)
            if xx:
                cmdFlag = True
                G_NODES.discard(str(xx.groups()[0]))

                print_message("Desktop", '%s' % cmd)

            xx = re.search(G_CMD_MSG, cmd)
            if xx:
                cmdFlag = True
                G_MESSAGE = str(xx.groups()[0])
                print_message("Desktop", '%s will be send to %s nodes' % (G_MESSAGE, len(G_NODES)))

                for xx in G_NODES:
                    item = xx.split(':')
                    #G_cmdResult.text = '%s %s:%s' % (G_cmdResult.text, item[0], item[1])
                    #reactor.connectTCP(item[0], int(item[1]), EchoClientFactory(self))
                    protocol.ClientCreator(reactor, EchoClient).connectTCP(item[0], int(item[1]))
                    #G_cmdResult.text = 'sendto %s' % (socket,)

            xx = re.search(G_CMD_LIST, cmd)
            if xx:
                cmdFlag = True
                print_message("Desktop", "There are %s nodes : %s" % (len(G_NODES), str(list(G_NODES))))

            xx = re.search(G_CMD_QUIT, cmd)
            if xx:
                cmdFlag = True
                G_NODES.clear()
                print_message("Desktop", 'There is no node')

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

class DesktopApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        title = Label(text='Compass Console',font_size=30,size_hint_y=None,height=60)
        layout.add_widget(title)

        topLayout = GridLayout(cols=3, size_hint_y=None, height=80)
        servBtn = Button(text='Start server')
        def on_press_serve_submit(instance):
            if servBtn.text=='Start server':
                reactor.listenTCP(8000, EchoFactory(self))
                print_message("Desktop", 'server started, serve on 8000')
                servBtn.text='Stop server'
            else:
                reactor.stop()
                servBtn.text='Start server'
                print_message("Desktop", 'server stoped')
        topLayout.add_widget(servBtn)

        consoleBtn = Button(text='help')
        consoleBtn.bind(on_press=on_press_display_console)
        topLayout.add_widget(consoleBtn)

        layout.add_widget(topLayout)

        cmdLayout = GridLayout(cols=2)

        G_cmdInput.bind(text=on_text_validate_cmd_input)
        cmdLayout.add_widget(G_cmdInput)

        cmdBtn = Button(text='Execute')
        cmdBtn.bind(on_press=on_press_cmd_submit)

        servBtn.bind(on_press=on_press_serve_submit)

        G_cmdBtnLayout.add_widget(cmdBtn)

        clearBtn = Button(text='Clear')
        clearBtn.bind(on_press=on_press_clear_submit)
        G_cmdBtnLayout.add_widget(clearBtn)

        cmdLayout.add_widget(G_cmdBtnLayout)

        layout.add_widget(cmdLayout)

        resultLayout = BoxLayout()
        resultLayout.add_widget(G_cmdResult)
        layout.add_widget(resultLayout)

        return layout

    def handle_message(self, msg):
        if msg == "ping":  msg =  "pong"
        if msg == "plop":  msg = "kivy rocks"
        print_message("Server", "responded: %s\n" % msg)
        return msg

    def on_connection(self, connection):
        print_message("Desktop", "connected succesfully!")
        self.connection = connection

def print_message(cat, msg):
    if G_cmdResult.text==G_HELP:
        G_cmdResult.text = "[%s] %s" % (cat, msg)
    else:
        xx = "%s\n[%s] %s" % (G_cmdResult.text, cat, msg)
        xx = xx.strip()
        lines = xx.split("\n")

        if len(lines)>5:
            G_cmdResult.text = "\n".join(lines[len(lines)-5:])
        else:
            G_cmdResult.text = xx



if __name__ == '__main__':
    DesktopApp().run()
