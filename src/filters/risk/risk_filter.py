# risk filter trả lời 4 câu:
#
# Lỗ tối đa bao nhiêu?
#
# Nếu sai, thoát có dễ không?
#
# Có rủi ro hệ thống không?
#
# Tỷ lệ risk : Reward có đáng đánh không?
from src.enums.risk import RiskLevel

class RiskFilter:
    def __init__(self):
        pass

    # Không có đáy → KHÔNG VÀO
    def find_stop_loss(self, company_data, entry):
        return entry - 1 * company_data.ATR_14

    # Nếu stop > 4% → loại setups
    def is_valid_stop_loss(self, stop_loss):
        if (stop_loss > 0.035):
            return RiskLevel.HIGH
        return RiskLevel.LOW

    # RR < 1.5 → bỏ

    # RR ≥ 2 → mới đáng đánh T+
    def is_valid_risk_reward(self, entry, target, stoploss):
        rr = (target - entry) / (entry - stoploss)
        if (rr < 1.5):
            return RiskLevel.HIGH
        return RiskLevel.LOW

    # A. Khoảng cách tới kháng cự
    # (Kháng cự gần – Entry) ≥ 2 × risk
    # → Không gian chạy đủ lớn
    def check_upper_gap(self, resistance, entry, stoploss):
        if (resistance - entry) / 2 >= stoploss:
            return RiskLevel.LOW
        return RiskLevel.HIGH

    # |Entry – MA20| ≤ 3%
    # Xa MA20 → stop gần → dễ quét
    def check_ma20_price(self, entry, company_data):
        if abs(entry - company_data.moving_average.ma20_price) / entry <= 0.03:
            return RiskLevel.LOW
        return RiskLevel.HIGH