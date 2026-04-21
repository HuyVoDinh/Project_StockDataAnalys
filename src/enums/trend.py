from enum import Enum


class Trend(Enum):
    Up = 1
    Down = -1
    Sideway = 0
    Weak = -2
    Fomo = -3
    Good = 2
    Recovery = 3

class MarketState(Enum):
    EARLY_TREND = 1
    MID_TREND = 2
    LATE_TREND = 3

class Momentum(Enum):
    In = 1
    Out = -1