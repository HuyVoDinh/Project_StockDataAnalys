from Model import Company

class VolumeFilter:
    def __init__(self):
        pass

    #Filter 1 - necessary
    #Immediately eliminate low-liquidity stocks:
    def find_minimum_liquidity(self, company_data):
        if company_data.volume > 30:
            return True
        return False

    #Filter 2 - necessary
    #Volume increased compared to average.
    def find_smart_market(self, company_data):
        # < 1.2 is weak volume
        if company_data.moving_average.ma20_volume / company_data.volume < 1.2:
            return -1
        # > 2.5 is fomo volume
        elif company_data.moving_average.ma20_volume / company_data.volume > 2.5:
            return 0
        # 1.3 - 1.8 is smart money
        else: return 1

    #Filter 3 - detect
    #Gather goods before pulling
    def check_gather_goods(self, company_data_day1, company_data_day2, company_data_day3):
        #Vol(t) > Vol(t-1) > Vol(t-2)
        if company_data_day1.volume < company_data_day2.volume:
            return -1
        elif company_data_day3.volume < company_data_day2.volume:
            return 0
        else: return 1

    #Filter 4 - detect
    #Increased volume – narrow price range
    #Big money doesn't want to reveal its hand.
    def check_volume_and_price(self, company_data, volume_yesterday):
        if company_data.volume < volume_yesterday:
            return -1
        elif (company_data.price.close_price - company_data.price.open_price) / company_data.price.open_price < 0.03:
            return 1

    #Filter 5 - detect
    #Supply test
    #Volume is lower than the previous 1-2 sessions.
    #Price does not fall.
    #→ likely to rise again the next day.
    def check_supply_test(self, company_data_day_current, company_data_day_before):
        if company_data_day_current.volume < company_data_day_before.volume and company_data_day_current.price.close_price >= company_data_day_before.price.close_price:
            return 1
        return 0

    #Filter 6 - detect
    #Used to determine if money is entering before the price increases.
    #Sideways price
    #OBV creates a higher peak
    #Do not use OBV to buy at the bottom
    def check_obv(self, company_data_day_current, company_data_day_before):
        if company_data_day_current.on_balance_volume > company_data_day_before.on_balance_volume:
            return 1
        return 0

    #Filter 7 - detect
    #The money is starting to come in.
    def check_vo(self, company_data_day_current):
        if company_data_day_current.Volume_Oscillator > 0 and (company_data_day_current.price.close_price - company_data_day_current.price.open_price) / company_data_day_current.open_price < 0.03:
            return 1
        return 0

    #Filter 8 - detect
    #Distinguishing between genuine price increases and bull traps.
    def check_accumulation_and_distribution(self, company_data_day_current, company_data_day_before):
        if company_data_day_current.price.close_price >= company_data_day_before.price.close_price and (company_data_day_current.price.close_price - company_data_day_current.price.open_price) / company_data_day_current.price.open_price < 0.03 and company_data_day_current.Accumulation_Distribution < company_data_day_before.Accumulation_Distribution:
            return -1
        elif (company_data_day_current.price.close_price - company_data_day_current.price.open_price) / company_data_day_current.price.open_price < 0.015 and  company_data_day_current.Accumulation_Distribution > company_data_day_before.Accumulation_Distribution:
            return 1
