from otree.api import *
import random
import json

doc = """
碳交易組：受試者需要先進行碳權交易，然後決定生產量
生產量受碳權持有量限制
"""

class C(BaseConstants):
    NAME_IN_URL = 'Stage_CarbonTrading'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    INITIAL_CAPITAL = cu(300)
    MAX_PRODUCTION = 50

class Subsession(BaseSubsession):
    market_price = models.CurrencyField()

def creating_session(subsession):
    # 每輪重新設定市場價格和角色
    pass

class Group(BaseGroup):
    buy_orders = models.LongStringField(initial='[]')
    sell_orders = models.LongStringField(initial='[]')

class Player(BasePlayer):
    is_dominant = models.BooleanField()
    marginal_cost = models.CurrencyField()
    carbon_emission_per_unit = models.IntegerField()
    market_price = models.CurrencyField()
    production = models.IntegerField(min=0, max=C.MAX_PRODUCTION)
    revenue = models.CurrencyField()
    net_profit = models.CurrencyField()
    initial_capital = models.CurrencyField()
    final_cash = models.CurrencyField()
    max_production = models.IntegerField()
    current_cash = models.CurrencyField()
    current_permits = models.IntegerField()

def initialize_roles(subsession: Subsession):
    shared_price = random.choice([cu(30), cu(35), cu(40), cu(45)])
    subsession.market_price = shared_price
    for p in subsession.get_players():
        p.is_dominant = random.choice([True, False])
        p.marginal_cost = cu(random.randint(0, 30) if p.is_dominant else random.randint(15, 35))
        p.carbon_emission_per_unit = 3 if p.is_dominant else 1
        p.max_production = 20 if p.is_dominant else 8
        p.market_price = shared_price
        p.initial_capital = (C.INITIAL_CAPITAL
                             if p.round_number == 1
                             else p.in_round(p.round_number - 1).final_cash)
        p.current_cash = p.initial_capital
        p.current_permits = random.randint(0, 5)

def set_payoffs(group: BaseGroup):
    for p in group.get_players():
        if p.production is None:
            p.production = 0
        
        cost = p.production * p.marginal_cost
        revenue = p.production * p.market_price
        profit = revenue - cost
        
        p.revenue = revenue
        p.net_profit = profit
        p.final_cash = p.current_cash + profit
        p.payoff = profit

class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
        
    @staticmethod
    def vars_for_template(player):
        return dict(
            treatment='trading',
            treatment_text='碳交易',
            num_rounds=C.NUM_ROUNDS,
        )

class ReadyWaitPage(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = initialize_roles

class TradingMarket(Page):
    timeout_seconds = 600
    live_method = 'live_method'
    
    form_model = 'player'
    form_fields = []

    @staticmethod
    def vars_for_template(player):
        return dict(
            cash=int(player.current_cash),
            permits=player.current_permits,
            marginal_cost=int(player.marginal_cost),
            carbon_emission_per_unit=player.carbon_emission_per_unit,
            timeout_seconds=TradingMarket.timeout_seconds,
            player_id=player.id_in_group,
            market_price=int(player.market_price),
            treatment='trading',
            treatment_text='碳交易',
        )

    @staticmethod
    def live_method(player, data):
        # [之前的live_method代碼保持不變]
        if data is None:
            print(f"初始請求，玩家：{player.id_in_group}")
            response = {player.id_in_group: TradingMarket.market_state(player)}
            print(f"初始響應數據: {response}")
            return response
            
        group = player.group
        
        print(f"玩家 {player.id_in_group} 發送請求: {data}")
        
        try:
            buy = json.loads(group.buy_orders)
            sell = json.loads(group.sell_orders)
            print(f"當前買單: {buy}, 賣單: {sell}")
        except json.JSONDecodeError as e:
            print(f"JSON 解析錯誤: {str(e)}，重置訂單列表")
            buy = []
            sell = []
            group.buy_orders = json.dumps(buy)
            group.sell_orders = json.dumps(sell)

        if data.get('type') == 'submit_offer':
            d = data.get('direction')
            pr = int(data.get('price', 0))
            qt = int(data.get('quantity', 0))
            
            print(f"提交掛單: 玩家 {player.id_in_group}, {d}, 價格: {pr}, 數量: {qt}")
            
            if d == 'buy' and player.current_cash < pr * qt:
                print(f"買單失敗：資金不足，需要 {pr*qt}，但只有 {player.current_cash}")
                return {player.id_in_group: {'type': 'fail', 'message': '資金不足'}}
            
            if d == 'sell' and player.current_permits < qt:
                print(f"賣單失敗：碳權不足，需要 {qt}，但只有 {player.current_permits}")
                return {player.id_in_group: {'type': 'fail', 'message': '碳權不足'}}
            
            # 自動撮合邏輯
            if d == 'buy':
                sell = json.loads(group.sell_orders)
                if sell and len(sell) > 0:
                    sell.sort(key=lambda x: (float(x[1]), int(x[0])))
                    lowest_sell = sell[0]
                    if float(lowest_sell[1]) <= pr:
                        seller_id, sell_price, sell_qty = lowest_sell
                        seller_id = int(seller_id)
                        sell_price = float(sell_price)
                        sell_qty = int(sell_qty)
                        trade_qty = min(qt, sell_qty)
                        try:
                            seller = group.get_player_by_id(seller_id)
                            actual_price = sell_price
                            player.current_cash -= actual_price * trade_qty
                            seller.current_cash += actual_price * trade_qty
                            player.current_permits += trade_qty
                            seller.current_permits -= trade_qty
                            
                            print(f"自動撮合成功：買家 {player.id_in_group} 從賣家 {seller_id} 買入 {trade_qty} 單位, 價格 {actual_price}")
                            
                            if trade_qty == sell_qty:
                                sell.remove(lowest_sell)
                            else:
                                for i, order in enumerate(sell):
                                    if int(order[0]) == seller_id and float(order[1]) == sell_price and int(order[2]) == sell_qty:
                                        sell[i] = [seller_id, sell_price, sell_qty - trade_qty]
                                        break
                            
                            group.sell_orders = json.dumps(sell)
                            
                            remaining_qty = qt - trade_qty
                            if remaining_qty > 0:
                                buy = json.loads(group.buy_orders)
                                buy.append([player.id_in_group, pr, remaining_qty])
                                buy.sort(key=lambda x: (-float(x[1]), int(x[0])))
                                group.buy_orders = json.dumps(buy)
                            
                            market_states = {}
                            for p in group.get_players():
                                state = TradingMarket.market_state(p)
                                if p.id_in_group == player.id_in_group:
                                    state['notification'] = {
                                        'type': 'success',
                                        'message': f'交易成功：您以價格 {actual_price} 買入了 {trade_qty} 單位碳權'
                                    }
                                elif p.id_in_group == seller_id:
                                    state['notification'] = {
                                        'type': 'success',
                                        'message': f'交易成功：您以價格 {actual_price} 賣出了 {trade_qty} 單位碳權'
                                    }
                                market_states[p.id_in_group] = state
                            
                            return market_states
                        except Exception as e:
                            print(f"自動撮合交易錯誤: {str(e)}")
                    
                buy = json.loads(group.buy_orders)
                buy.append([player.id_in_group, pr, qt])
                buy.sort(key=lambda x: (-float(x[1]), int(x[0])))
                print(f"買單添加成功，當前買單列表: {buy}")
                group.buy_orders = json.dumps(buy)
            
            else:  # 賣單邏輯
                buy = json.loads(group.buy_orders)
                if buy and len(buy) > 0:
                    buy.sort(key=lambda x: (-float(x[1]), int(x[0])))
                    highest_buy = buy[0]
                    if float(highest_buy[1]) >= pr:
                        buyer_id, buy_price, buy_qty = highest_buy
                        buyer_id = int(buyer_id)
                        buy_price = float(buy_price)
                        buy_qty = int(buy_qty)
                        trade_qty = min(qt, buy_qty)
                        try:
                            buyer = group.get_player_by_id(buyer_id)
                            actual_price = buy_price
                            buyer.current_cash -= actual_price * trade_qty
                            player.current_cash += actual_price * trade_qty
                            buyer.current_permits += trade_qty
                            player.current_permits -= trade_qty
                            
                            print(f"自動撮合成功：賣家 {player.id_in_group} 賣給買家 {buyer_id} {trade_qty} 單位, 價格 {actual_price}")
                            
                            if trade_qty == buy_qty:
                                buy.remove(highest_buy)
                            else:
                                for i, order in enumerate(buy):
                                    if int(order[0]) == buyer_id and float(order[1]) == buy_price and int(order[2]) == buy_qty:
                                        buy[i] = [buyer_id, buy_price, buy_qty - trade_qty]
                                        break
                            
                            group.buy_orders = json.dumps(buy)
                            
                            remaining_qty = qt - trade_qty
                            if remaining_qty > 0:
                                sell = json.loads(group.sell_orders)
                                sell.append([player.id_in_group, pr, remaining_qty])
                                sell.sort(key=lambda x: (float(x[1]), int(x[0])))
                                group.sell_orders = json.dumps(sell)
                            
                            market_states = {}
                            for p in group.get_players():
                                state = TradingMarket.market_state(p)
                                if p.id_in_group == player.id_in_group:
                                    state['notification'] = {
                                        'type': 'success',
                                        'message': f'交易成功：您以價格 {actual_price} 賣出了 {trade_qty} 單位碳權'
                                    }
                                elif p.id_in_group == buyer_id:
                                    state['notification'] = {
                                        'type': 'success',
                                        'message': f'交易成功：您以價格 {actual_price} 買入了 {trade_qty} 單位碳權'
                                    }
                                market_states[p.id_in_group] = state
                            
                            return market_states
                        except Exception as e:
                            print(f"自動撮合交易錯誤: {str(e)}")
                
                sell = json.loads(group.sell_orders)
                sell.append([player.id_in_group, pr, qt])
                sell.sort(key=lambda x: (float(x[1]), int(x[0])))
                print(f"賣單添加成功，當前賣單列表: {sell}")
                group.sell_orders = json.dumps(sell)
                
            response = {p.id_in_group: TradingMarket.market_state(p) for p in group.get_players()}
            print(f"發送響應到所有玩家: {response}")
            return response

        elif data.get('type') == 'accept_offer':
            ot = data.get('offer_type')
            pr = float(data.get('price', 0))
            qt = int(data.get('quantity', 0))
            tid = int(data.get('player_id', 0))
            
            print(f"接受掛單: {ot}, 價格: {pr}, 數量: {qt}, 對方ID: {tid}")
            
            if ot == 'sell' and tid != player.id_in_group:
                if player.current_cash >= pr * qt:
                    try:
                        seller = group.get_player_by_id(tid)
                        player.current_cash -= pr * qt
                        seller.current_cash += pr * qt
                        player.current_permits += qt
                        seller.current_permits -= qt
                        sell = [o for o in sell if not (int(o[0]) == tid and float(o[1]) == pr and int(o[2]) == qt)]
                        group.sell_orders = json.dumps(sell)
                        print(f"交易成功：買家 {player.id_in_group} 從賣家 {tid} 買入 {qt} 單位, 價格 {pr}")
                        
                        market_states = {}
                        for p in group.get_players():
                            state = TradingMarket.market_state(p)
                            if p.id_in_group == player.id_in_group:
                                state['notification'] = {
                                    'type': 'success',
                                    'message': f'交易成功：您以價格 {pr} 買入了 {qt} 單位碳權'
                                }
                            elif p.id_in_group == tid:
                                state['notification'] = {
                                    'type': 'success',
                                    'message': f'交易成功：您以價格 {pr} 賣出了 {qt} 單位碳權'
                                }
                            market_states[p.id_in_group] = state
                        
                        return market_states
                    except Exception as e:
                        print(f"獲取賣家失敗: {tid}, 錯誤: {str(e)}")
                        return {player.id_in_group: {'type': 'fail', 'message': '交易失敗：找不到賣家'}}
                else:
                    print(f"交易失敗：資金不足，需要 {pr*qt}，但只有 {player.current_cash}")
                    return {player.id_in_group: {'type': 'fail', 'message': '資金不足'}}
                    
            elif ot == 'buy' and tid != player.id_in_group:
                if player.current_permits >= qt:
                    try:
                        buyer = group.get_player_by_id(tid)
                        player.current_cash += pr * qt
                        buyer.current_cash -= pr * qt
                        player.current_permits -= qt
                        buyer.current_permits += qt
                        buy = [o for o in buy if not (int(o[0]) == tid and float(o[1]) == pr and int(o[2]) == qt)]
                        group.buy_orders = json.dumps(buy)
                        print(f"交易成功：賣家 {player.id_in_group} 賣給買家 {tid} {qt} 單位, 價格 {pr}")
                        
                        market_states = {}
                        for p in group.get_players():
                            state = TradingMarket.market_state(p)
                            if p.id_in_group == player.id_in_group:
                                state['notification'] = {
                                    'type': 'success',
                                    'message': f'交易成功：您以價格 {pr} 賣出了 {qt} 單位碳權'
                                }
                            elif p.id_in_group == tid:
                                state['notification'] = {
                                    'type': 'success',
                                    'message': f'交易成功：您以價格 {pr} 買入了 {qt} 單位碳權'
                                }
                            market_states[p.id_in_group] = state
                        
                        return market_states
                    except Exception as e:
                        print(f"獲取買家失敗: {tid}, 錯誤: {str(e)}")
                        return {player.id_in_group: {'type': 'fail', 'message': '交易失敗：找不到買家'}}
                else:
                    print(f"交易失敗：碳權不足，需要 {qt}，但只有 {player.current_permits}")
                    return {player.id_in_group: {'type': 'fail', 'message': '碳權不足'}}
            else:
                print(f"交易失敗：不能與自己交易")
                return {player.id_in_group: {'type': 'fail', 'message': '不能與自己交易'}}
            
            response = {p.id_in_group: TradingMarket.market_state(p) for p in group.get_players()}
            print(f"交易後發送響應: {response}")
            return response

        elif data.get('type') == 'cancel_offer':
            d = data.get('direction')
            pr = float(data.get('price', 0))
            qt = int(data.get('quantity', 0))
            
            print(f"取消掛單: 玩家 {player.id_in_group}, {d}, 價格: {pr}, 數量: {qt}")
            
            if d == 'buy':
                original_count = len(buy)
                buy = [o for o in buy if not (int(o[0]) == player.id_in_group and float(o[1]) == pr and int(o[2]) == qt)]
                if len(buy) < original_count:
                    print(f"買單取消成功")
                else:
                    print(f"買單取消失敗：未找到符合條件的訂單")
                group.buy_orders = json.dumps(buy)
            else:
                original_count = len(sell)
                sell = [o for o in sell if not (int(o[0]) == player.id_in_group and float(o[1]) == pr and int(o[2]) == qt)]
                if len(sell) < original_count:
                    print(f"賣單取消成功")
                else:
                    print(f"賣單取消失敗：未找到符合條件的訂單")
                group.sell_orders = json.dumps(sell)
                
            response = {p.id_in_group: TradingMarket.market_state(p) for p in group.get_players()}
            print(f"取消掛單後發送響應: {response}")
            return response
        
        elif data.get('type') == 'ping':
            print(f"收到ping請求，玩家 {player.id_in_group}")
            response = {player.id_in_group: TradingMarket.market_state(player)}
            print(f"Ping響應: {response}")
            return response
            
        response = {player.id_in_group: TradingMarket.market_state(player)}
        print(f"默認響應: {response}")
        return response

    @staticmethod
    def market_state(player):
        try:
            buy = json.loads(player.group.buy_orders)
            sell = json.loads(player.group.sell_orders)
            print(f"原始買賣單數據: buy={buy}, sell={sell}")
        except Exception as e:
            print(f"解析買賣單數據錯誤: {e}")
            buy = []
            sell = []
            
        try:
            buy_sorted = sorted(buy, key=lambda x: (-float(x[1]), int(x[0])))
            sell_sorted = sorted(sell, key=lambda x: (float(x[1]), int(x[0])))
            print(f"排序後買賣單: buy_sorted={buy_sorted}, sell_sorted={sell_sorted}")
        except Exception as e:
            print(f"排序買賣單錯誤: {e}")
            buy_sorted = []
            sell_sorted = []
        
        try:
            buy_offers = [{'player_id': int(pid), 'price': int(float(price)), 'quantity': int(qt)}
                        for pid, price, qt in buy_sorted]
            sell_offers = [{'player_id': int(pid), 'price': int(float(price)), 'quantity': int(qt)}
                        for pid, price, qt in sell_sorted]
            print(f"轉換後買賣單: buy_offers={buy_offers}, sell_offers={sell_offers}")
        except Exception as e:
            print(f"轉換買賣單格式錯誤: {e}")
            buy_offers = []
            sell_offers = []
        
        profit_table = []
        for i in range(1, player.max_production + 1):
            c = i * player.marginal_cost
            r = i * player.market_price
            profit_table.append({'quantity': i, 'profit': int(r - c)})
        
        result = {
            'type': 'update',
            'cash': int(player.current_cash),
            'permits': int(player.current_permits),
            'marginal_cost': int(player.marginal_cost),
            'carbon_emission_per_unit': int(player.carbon_emission_per_unit),
            'buy_offers': buy_offers,
            'sell_offers': sell_offers,
            'profit_table': profit_table,
        }
        
        print(f"返回給玩家 {player.id_in_group} 的數據: {result}")
        return result

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened and player.id_in_group == 1:
            player.group.buy_orders = '[]'
            player.group.sell_orders = '[]'
        if timeout_happened:
            player.current_cash = max(player.current_cash, 0)
            player.current_permits = max(player.current_permits, 0)

class ProductionDecision(Page):
    form_model = 'player'
    form_fields = ['production']

    @staticmethod
    def error_message(player, values):
        if values['production'] > player.current_permits:
            return '生產量不能超過持有的碳權'

    @staticmethod
    def vars_for_template(player):
        maxp = min(player.max_production, player.current_permits)
        unit_income = int(player.market_price)
        unit_cost = int(player.marginal_cost)
        unit_profit = unit_income - unit_cost

        return dict(
            max_production=player.max_production,
            max_possible_production=maxp,
            marginal_cost=player.marginal_cost,
            carbon_emission_per_unit=player.carbon_emission_per_unit,
            market_price=player.market_price,
            current_permits=player.current_permits,
            treatment='trading',
            treatment_text='碳交易',
            unit_income=unit_income,
            unit_cost=unit_cost,
            unit_profit=unit_profit,
        )

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

# 碳交易組 Results 類
class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        production_cost = int(player.production * player.marginal_cost)
        remaining_rounds = C.NUM_ROUNDS - player.round_number
        total_emissions = player.production * player.carbon_emission_per_unit
        # 計算進度條百分比
        progress_percentage = round((player.round_number / C.NUM_ROUNDS) * 100)
        
        return dict(
            market_price=player.market_price,
            revenue=player.revenue,
            net_profit=player.net_profit,
            final_cash=player.final_cash,
            treatment='trading',
            treatment_text='碳交易',
            production_cost=production_cost,
            remaining_rounds=remaining_rounds,
            total_emissions=total_emissions,
            is_last_round=(player.round_number == C.NUM_ROUNDS),
            total_rounds=C.NUM_ROUNDS,  # 新增
            progress_percentage=progress_percentage,  # 新增
        )

page_sequence = [
    Introduction,
    ReadyWaitPage,
    TradingMarket,
    ProductionDecision,
    ResultsWaitPage,
    Results
]