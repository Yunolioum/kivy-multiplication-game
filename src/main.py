from random import randint
import time

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty, ObjectProperty, BooleanProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout

class SuccessDependantGraphics(BoxLayout):
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
    NUMPAD_KEYS = {
        'numpad0': '0',
        'numpad1': '1',
        'numpad2': '2',
        'numpad3': '3',
        'numpad4': '4',
        'numpad5': '5',
        'numpad6': '6',
        'numpad7': '7',
        'numpad8': '8',
        'numpad9': '9',
    }
    
    def __init__(self, **kwargs):
        super(NumericTextInput, self).__init__(**kwargs)
        self.register_event_type('on_enter_key')
        self.register_event_type('on_new_number')
        self.register_event_type('on_erase_number')
    
    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        __unused_key, key_str = keycode
        if key_str in self.NUMPAD_KEYS.values():
            self.dispatch('on_new_number', key_str)
        elif self.NUMPAD_KEYS.has_key(key_str):
            self.dispatch('on_new_number', self.NUMPAD_KEYS.get(key_str))
        elif key_str == 'backspace':
            self.dispatch('on_erase_number')
        elif key_str == 'enter':
            self.dispatch('on_enter_key')
            pass
            
    def on_enter_key(self):
        pass
    def on_new_number(self, number):
        pass
    def on_erase_number(self):
        pass

class GameBoard(Screen):
    equation_widget = ObjectProperty(None)
    
    _current_guess = StringProperty('')
    
    input = ObjectProperty(None)
    new_game_button = ObjectProperty(None)
    
    input_is_correct = BooleanProperty(False)
    
    success_dependant_graphics = ObjectProperty(None)
    
    numpad = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(GameBoard, self).__init__(**kwargs)
        self.register_event_type('on_numpad_new_number')
        self.register_event_type('on_numpad_erase_number')
        self.input.bind(on_new_number=self.on_new_number)
        self.input.bind(on_erase_number=self.on_erase_number)
        self.input.bind(on_enter=self.on_enter_key)
        self.bind(on_numpad_new_number=self.on_new_number)
        self.bind(on_numpad_erase_number=self.on_erase_number)
    
    def numbutton_pressed(self, instance, value):
        self.dispatch('on_numpad_new_number', int(value))
    def erase_pressed(self, instance):
        self.dispatch('on_numpad_erase_number')
    def on_numpad_new_number(self, number):
        pass
    def on_numpad_erase_number(self):
        pass
    
    @property
    def correct_answer(self):
        if self.equation_widget is None:
            return -1
        return int(self.equation_widget.operand1.text) * int(self.equation_widget.operand2.text)
        
    def on_pre_enter(self):
        self.new_game()
        
    @property
    def current_guess(self):
        return self._current_guess
    
    @current_guess.setter
    def current_guess(self, new_text):
        if len(new_text) > 0:
            int(new_text) # Make sure we only input integers
        if not self._current_guess == str(self.correct_answer):
            self._current_guess = new_text
            self.on_guess()
    def on_new_number(self, instance, number):
        self.current_guess += str(number)
    def on_erase_number(self, instance):
        if len(self.current_guess) > 0:
            self.current_guess = self.current_guess[:(len(self.current_guess) - 1)]
    
    def on_guess(self):
        if self.current_guess == str(self.correct_answer):
            self.on_success()
        else:
            self.on_fail()
    
    def on_success(self):
        self.input_is_correct = True
        
        self.success_dependant_graphics.on_success()
        self.success_dependant_graphics.show()
        
    def on_fail(self):
        self.input_is_correct = False
        
    def on_enter_key(self, instance):
        if self.input_is_correct:
            self.new_game()
    
    def new_game(self):
        self.input_is_correct = False
        
        self.success_dependant_graphics.hide()
        self.success_dependant_graphics.on_new_game()
        
        self.current_guess = ''

        self.input.focus = True
        
class MultiplicationGameApp(App):
    NUMBER_OF_GAMES = 5
    OPERAND_MAX = 12
    OPERAND_MIN = 1
    FONT_NAME = 'fonts/Scratch.ttf'
    
    def randomize_operand(self):
        return randint(self.OPERAND_MIN, self.OPERAND_MAX)
    
    def next_game(self):
        if not self.screens.current_screen.input_is_correct:
            raise RuntimeError("Tried to start a new game with an incorrect answer")
        else:
            self.screens.current = self.screens.next()
    
    @property
    def default_font_name(self):
        return self.FONT_NAME
    
    def build(self):
        self.screens = ScreenManager()
        for i in range(0, self.NUMBER_OF_GAMES):
            self.screens.add_widget(GameBoard(name='Game %d' % i))
        return self.screens

if __name__ == '__main__':
    MultiplicationGameApp().run()
