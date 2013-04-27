from kivy.app import App
from kivy.uix.widget import Widget

class Desktop(Widget):
    pass


class DesktopApp(App):
    def build(self):
        return Desktop()


if __name__ == '__main__':
    DesktopApp().run()
