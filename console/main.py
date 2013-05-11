from kivy.app import App
from kivy.uix.widget import Widget

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivy.properties import ObjectProperty, StringProperty

"""class Desktop(Widget):
    cmd_input = ObjectProperty()
    cmd_output = ObjectProperty()

    def on_focus_cmd_input(self, instance, value):
        self.cmd_input.text = ''
"""

G_help      = "> Type help <cmd> to get detailed help\n1> connect <host> : connect the server\n2> quit : quite this conversation\n3> list : list all nodes\n4> msg <message> : send a message to server"
G_cmdResult = Label(text=G_help,font_size=25)
G_cmdInput  = TextInput(text='',font_size=40)

def on_text_validate_cmd_input(instance, val):
    G_cmdResult.text = val

def on_press_clear_submit(instance):
    G_cmdResult.text = ''

def on_press_serve_submit(instance):
    G_cmdResult.text = 'Serve on port 8080'

def on_press_cmd_submit(instance):
    cmd = G_cmdInput.text.strip()
    if cmd.find('help') == 0: # HELP
        G_cmdResult.text = '%s is executing...' % cmd
    else:
        G_cmdResult.text = G_help

class DesktopApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        title = Label(text='Compass Console',font_size=35,size_hint_y=None,height=80)
        layout.add_widget(title)

        cmdLayout = GridLayout(cols=2)

        G_cmdInput.bind(text=on_text_validate_cmd_input)
        cmdLayout.add_widget(G_cmdInput)

        cmdBtnLayout = BoxLayout(orientation='vertical',size_hint_x=None,width=200)
        cmdBtn = Button(text='Execute')
        cmdBtn.bind(on_press=on_press_cmd_submit)
        clearBtn = Button(text='Clear')
        clearBtn.bind(on_press=on_press_clear_submit)

        servBtn = Button(text='Serve')
        servBtn.bind(on_press=on_press_serve_submit)

        cmdBtnLayout.add_widget(cmdBtn)
        cmdBtnLayout.add_widget(clearBtn)
        cmdBtnLayout.add_widget(servBtn)
        cmdLayout.add_widget(cmdBtnLayout)

        layout.add_widget(cmdLayout)

        resultLayout = BoxLayout()
        resultLayout.add_widget(G_cmdResult)
        layout.add_widget(resultLayout)

        #dummy = Label(text="")
        #layout.add_widget(dummy)

        return layout


if __name__ == '__main__':
    DesktopApp().run()
