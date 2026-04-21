from enum import Enum


class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class Emplitude(Enum):
    Weak = 1
    Tight = 2
    Good = 3
    Break = 4
    Bulltrap = -1