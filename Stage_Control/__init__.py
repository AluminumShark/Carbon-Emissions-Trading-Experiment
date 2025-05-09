from otree.api import *
import random

doc = """
對照組：受試者直接決定生產量，不受碳排放限制，也不需繳納碳稅
"""

class C(BaseConstants):
    NAME_IN_URL = 'Stage_Control'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    INITIAL_CAPITAL = cu(300)
    MAX_PRODUCTION = 50

class Subsession(BaseSubsession):
    market_price = models.CurrencyField()

def creating_session(subsession):
    # 每輪重新設定市場價格
    pass

class Group(BaseGroup):
    pass

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

def set_payoffs(group: BaseGroup):
    for p in group.get_players():
        if p.production is None:
            p.production = 0
        
        cost = p.production * p.marginal_cost
        revenue = p.production * p.market_price
        profit = revenue - cost  # 對照組無碳稅
        
        p.revenue = revenue
        p.net_profit = profit
        p.final_cash = p.initial_capital + profit
        p.payoff = profit

class Introduction(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
        
    @staticmethod
    def vars_for_template(player):
        return dict(
            treatment='control',
            treatment_text='對照',
            num_rounds=C.NUM_ROUNDS,
        )

class ReadyWaitPage(WaitPage):
    wait_for_all_groups = True
    after_all_players_arrive = initialize_roles

class ProductionDecision(Page):
    form_model = 'player'
    form_fields = ['production']

    @staticmethod
    def vars_for_template(player):
        maxp = player.max_production  # 對照組不受碳權限制
            
        unit_income = int(player.market_price)
        unit_cost = int(player.marginal_cost)
        unit_profit = unit_income - unit_cost  # 對照組無碳稅

        return dict(
            max_production=player.max_production,
            max_possible_production=maxp,
            marginal_cost=player.marginal_cost,
            carbon_emission_per_unit=player.carbon_emission_per_unit,
            market_price=player.market_price,
            treatment='control',
            treatment_text='對照',
            unit_income=unit_income,
            unit_cost=unit_cost,
            unit_profit=unit_profit,
        )

class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

# 對照組 Results 類
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
            treatment='control',
            treatment_text='對照',
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
    ProductionDecision,
    ResultsWaitPage,
    Results
]