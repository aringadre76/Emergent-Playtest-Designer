import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playtest_ai import Agent
from playtest_ai.input_injector import ActionType


class CircleAgent(Agent):
    def __init__(self, window_title: str, **kwargs):
        super().__init__(window_title, **kwargs)
        self.action_sequence = [
            ('w', 0.5),
            ('d', 0.5),
            ('s', 0.5),
            ('a', 0.5),
        ]
        self.sequence_index = 0
        self.logger.set_metadata("agent_type", "circle")
    
    def decide_action(self, frame: np.ndarray, analysis: dict):
        key, duration = self.action_sequence[self.sequence_index]
        self.sequence_index = (self.sequence_index + 1) % len(self.action_sequence)
        
        return ActionType.KEY_PRESS, {'key': key, 'duration': duration}


def main():
    print("Circle Agent Example")
    print("Repeatedly presses W -> D -> S -> A in sequence")
    print()
    
    window_title = input("Enter game window title: ")
    
    agent = CircleAgent(
        window_title=window_title,
        fps=5,
        max_steps=40
    )
    
    agent.run()


if __name__ == "__main__":
    main()

