from enum import Enum


class Liquidity(Enum):
    Weak = 0
    Good = 1

class Cash_Flow(Enum):
    Weak = 0
    Smart_Money = 1
    Fomo = -1

class Volume(Enum):
    Money_In = 0
    Money_Out = 1