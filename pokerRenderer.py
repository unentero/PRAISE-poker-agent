from renderers import IRenderer

#{"nombre": self.agentsAlias[agent_id], "player cards": self.playerCards[agent_id],"table cards": self.cardsOnTable, "pot" : self.pot, "winner":self.gameWinner}

def show_hand_cards(cards):
    hand_cards = ['_','_']
    for i, card in enumerate(cards[:2]):
        hand_cards[i] = str(card)
    return ' '.join(hand_cards)

def show_table_cards(cards):
    table_cards = ['_', '_', '_', '_', '_']
    for i, card in enumerate(cards[:5]):
        table_cards[i] = str(card)
    return ' '.join(table_cards)


class ConsoleRenderer(IRenderer):
    def __init__(self):
        self.environment_statebuffer = {}


    def observe(self, statebuffer):
        self.environment_statebuffer = statebuffer

    def render(self):
        state = self.environment_statebuffer.get_state()
        if state:
            print(state["name"]) #nombre
            print('Hand: ' + show_hand_cards(state["player cards"])) #cartas mano
            print('Table: ' + show_table_cards(state["table cards"])) #cartas mesa
            print('Stage: ' + str(state["stage"])) #round
            #print('Chips: ') + str(state["chips"])
            #print('Max Bet: ') + str(state["maxBet"])
            print('Pot: ' + str(state["pot"])) #pot
            if not(state["winner"] == ""):
                print('Winner: ' + state["winner"]) #ganador
            print(" ")