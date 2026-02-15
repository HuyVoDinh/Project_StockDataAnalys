# Risk filter trả lời 4 câu:
#
# Lỗ tối đa bao nhiêu?
#
# Nếu sai, thoát có dễ không?
#
# Có rủi ro hệ thống không?
#
# Tỷ lệ Risk : Reward có đáng đánh không?

#Không có đáy → KHÔNG VÀO
def find_stop_loss(company_data, entry):
    return entry - 1 * company_data.ATR_14

# Nếu stop > 4% → loại setup
def is_valid_stop_loss(stop_loss):
    if (stop_loss > 0.035 ):
        return 0
    return 1
#RR < 1.5 → bỏ

# RR ≥ 2 → mới đáng đánh T+
def is_valid_risk_reward(entry, target, stoploss):
    rr = (target - entry) / (entry - stoploss)
    if (rr < 1.5):
        return 0
    return 1

# A. Khoảng cách tới kháng cự
# (Kháng cự gần – Entry) ≥ 2 × Risk
# → Không gian chạy đủ lớn
def check_upper_gap(resistance, entry, stoploss):
    if (resistance - entry)/ 2 >= stoploss:
        return 1
    return 0

# |Entry – MA20| ≤ 3%
# Xa MA20 → stop gần → dễ quét
def check_ma20_price(entry, company_data):
    if abs(entry - company_data.moving_average.ma20_price)/ entry <= 0.03:
        return 1
    return 0