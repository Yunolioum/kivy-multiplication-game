from random import randint
import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty

class Numpad(Widget):
    pass

class NumButton(Button):
    pass

class SuccessDependantGraphics(Widget):
    time_to_solve = StringProperty('')
    position_y_multiplier = NumericProperty(-1)
    
    start_time = 0
    end_time = 0
    
    def on_success(self):
        self.end_time = self.get_current_time()
        self.time_to_solve = "%.3f" % (self.end_time - self.start_time)
        
    def on_new_game(self):
        self.start_time = self.get_current_time()
    
    def get_current_time(self):
        return time.time()
    
    def show(self):
        self.position_y_multiplier = 1
        
    def hide(self):
        self.position_y_multiplier = -1
    
class NumericTextInput(TextInput):
    ALLOWED_KEYS = [
        'backspace',
        'numpad0',
        'numpad1',
        'numpad2',
        'numpad3',
        'numpad4',
        'numpad5',
        'numpad6',
        'numpad7',
        'numpad8',
        'numpad9',
        '0','1','2','3','4',
        '5','6','7','8','9',
    ]
    
    def __init__(self, **kwargs):
        super(NumericTextInput, self).__init__(**kwargs)
        self.register_event_type('on_enter')
    
    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        __unused_key, key_str = keycode
        if key_str in self.ALLOWED_KEYS:
            super(NumericTextInput, self)._keyboard_on_key_down(window, keycode, text, modifiers)
        elif key_str == 'enter':
            self.dispatch('on_enter')
            pass
            
    def on_enter(self):
        pass

class GameBoard(Widget):
    operand1 = NumericProperty(0)
    operand2 = NumericProperty(0)
    
    correct_answer = 0
    
    current_guess = StringProperty('')
    
    input = ObjectProperty(None)
    new_game_button = ObjectProperty(None)
    
    input_is_correct = BooleanProperty(False)
    
    success_dependant_graphics = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(GameBoard, self).__init__(**kwargs)
        self.input.bind(text=self.on_text)
        self.input.bind(on_enter=self.on_enter)
        self.success_dependant_graphics.new_game_button.bind(
                on_press=self.on_new_game_button_clicked)
    
    def on_text(self, instance, text):
        self.current_guess = text
        self.on_guess()
    
    def on_guess(self):
        if self.current_guess == str(self.correct_answer):
            self.on_success()
        else:
            self.on_fail()
    
    def on_success(self):
        self.input_is_correct = True
        
        self.success_dependant_graphics.on_success()
        self.success_dependant_graphics.show()
        
    def on_new_game_button_clicked(self, instance):
        if not self.input_is_correct:
            raise RuntimeError("Tried to start a new game")
        else:
            self.new_game()
        
    def on_fail(self):
        self.input_is_correct = False
        
    def on_enter(self, instance):
        if self.input_is_correct:
            self.new_game()
    
    def new_game(self):
        self.input_is_correct = False
        
        self.input.text = ''
        
        self.operand1 = randint(1,12)
        self.operand2 = randint(1,12)
        
        self.correct_answer = self.operand1 * self.operand2
        
        self.success_dependant_graphics.hide()
        self.success_dependant_graphics.on_new_game()

        self.input.focus = True
        
class MultiplicationGameApp(App):
    def build(self):
        game_board = GameBoard()
        game_board.new_game()
        return game_board

if __name__ == '__main__':
    MultiplicationGameApp().run()
