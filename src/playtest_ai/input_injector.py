import time
import random
from typing import List, Tuple, Optional
from enum import Enum


class ActionType(Enum):
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    KEY_TAP = "key_tap"
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    WAIT = "wait"


class InputInjector:
    
    def __init__(self, use_pydirectinput: bool = True):
        self.use_pydirectinput = use_pydirectinput
        
        if use_pydirectinput:
            try:
                import pydirectinput
                self.input_lib = pydirectinput
                pydirectinput.PAUSE = 0.01
            except ImportError:
                import pyautogui
                self.input_lib = pyautogui
                pyautogui.PAUSE = 0.01
        else:
            import pyautogui
            self.input_lib = pyautogui
            pyautogui.PAUSE = 0.01
    
    def press_key(self, key: str, duration: float = 0.1):
        try:
            self.input_lib.keyDown(key)
            time.sleep(duration)
            self.input_lib.keyUp(key)
        except Exception as e:
            print(f"Error pressing key {key}: {e}")
    
    def tap_key(self, key: str):
        try:
            self.input_lib.press(key)
        except Exception as e:
            print(f"Error tapping key {key}: {e}")
    
    def hold_key(self, key: str):
        try:
            self.input_lib.keyDown(key)
        except Exception as e:
            print(f"Error holding key {key}: {e}")
    
    def release_key(self, key: str):
        try:
            self.input_lib.keyUp(key)
        except Exception as e:
            print(f"Error releasing key {key}: {e}")
    
    def move_mouse(self, x: int, y: int, duration: float = 0.1):
        try:
            self.input_lib.moveTo(x, y, duration=duration)
        except Exception as e:
            print(f"Error moving mouse to ({x}, {y}): {e}")
    
    def click_mouse(self, x: Optional[int] = None, y: Optional[int] = None, button: str = 'left'):
        try:
            if x is not None and y is not None:
                self.input_lib.click(x, y, button=button)
            else:
                self.input_lib.click(button=button)
        except Exception as e:
            print(f"Error clicking mouse: {e}")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        try:
            return self.input_lib.position()
        except Exception as e:
            print(f"Error getting mouse position: {e}")
            return (0, 0)
    
    def execute_action(self, action_type: ActionType, **kwargs):
        if action_type == ActionType.KEY_PRESS:
            key = kwargs.get('key', 'space')
            duration = kwargs.get('duration', 0.1)
            self.press_key(key, duration)
        
        elif action_type == ActionType.KEY_TAP:
            key = kwargs.get('key', 'space')
            self.tap_key(key)
        
        elif action_type == ActionType.MOUSE_MOVE:
            x = kwargs.get('x', 0)
            y = kwargs.get('y', 0)
            duration = kwargs.get('duration', 0.1)
            self.move_mouse(x, y, duration)
        
        elif action_type == ActionType.MOUSE_CLICK:
            x = kwargs.get('x')
            y = kwargs.get('y')
            button = kwargs.get('button', 'left')
            self.click_mouse(x, y, button)
        
        elif action_type == ActionType.WAIT:
            duration = kwargs.get('duration', 0.5)
            time.sleep(duration)
    
    @staticmethod
    def get_common_game_keys() -> List[str]:
        return [
            'w', 'a', 's', 'd',
            'up', 'down', 'left', 'right',
            'space', 'shift', 'ctrl',
            'e', 'q', 'r', 'f',
            '1', '2', '3', '4',
            'escape', 'enter'
        ]
    
    @staticmethod
    def get_random_action() -> Tuple[ActionType, dict]:
        action_types = [
            ActionType.KEY_PRESS,
            ActionType.KEY_TAP,
            ActionType.WAIT
        ]
        
        action = random.choice(action_types)
        
        if action in [ActionType.KEY_PRESS, ActionType.KEY_TAP]:
            key = random.choice(InputInjector.get_common_game_keys())
            duration = random.uniform(0.05, 0.3)
            return action, {'key': key, 'duration': duration}
        
        elif action == ActionType.WAIT:
            duration = random.uniform(0.1, 0.5)
            return action, {'duration': duration}
        
        return ActionType.WAIT, {'duration': 0.1}

