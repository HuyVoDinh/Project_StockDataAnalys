from enum import Enum


class Trend(Enum):
    Fomo = -4
    Weak = -3
    Strong_Down = -2
    Down = -1
    Sideway = 0
    Up = 1
    Good = 2
    Strong_Up = 3
    Recovery = 4

class MarketState(Enum):
    EARLY_TREND = 1
    MID_TREND = 2
    LATE_TREND = 3

class Momentum(Enum):
    In = 1
    Out = -1