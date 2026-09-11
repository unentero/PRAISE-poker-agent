import pokerAgents
import pokerHandsModule
from environments import SimulatedEnvironment
import random
import threading

class PokerTable(SimulatedEnvironment):
    def __init__(self):
        self.agents = [] #Lista de jugadores
        self.stages = [0,1,2,3,4,5] # 0 = Repartir, 1 = PreFlop, 2 = Flop, 3 = Turn, 4 = River, 5 = Showdown
        self._statebuffers = [] #No se que hace esto pero lo dejo porlasdudas
        self.mazo = random.shuffle(pokerHandsModule.Deck().deck) #Este es el mazo pero lo mezcla previamente
        self.smallBlind = 5
        self.bigBlind = 2*self.smallBlind
        self.maxBet = self.bigBlind
        self.smallBlindId = 0
        self.bigBlindId = 0
        self.pot = self.smallBlind + self.bigBlind
        self.playerOrder = {}
        self.foldedPlayers = []
        self.currentTurn = 0
        self.playerCards = {}
        self.playerChips = {}
        self.playerBets = {}
        self.cardsOnTable = {}
        self.cardsOnTableAmount = 0
        self.tableSize = 4
        self.gameWinner = ""
        
    def add(self, agent_id: int) -> None:
        playersAmmount = 0
        numberPlayer = 0 
        if not(agent_id in self._agents) and playersAmmount <= self.tableSize:   
            self._agents.append(agent_id)
            self.playerOrder[agent_id] = numberPlayer
            numberPlayer += 1
            playersAmmount += 1     

    def remove(self, agent_id: int) -> None:
        if agent_id in self._agents:
            self._agents.remove(agent_id)

    def add_statebuffer(self, agent_id: int, statebuffer) -> None:
        self._agents.append(agent_id)
        self._statebuffers.append({"agent_id": agent_id, "statebuffer": statebuffer})

    def remove_statebuffer(self, agent_id: int, statebuffer) -> None:
        if agent_id in self._agents:
            self._agents.remove(agent_id)
            self._statebuffers.remove(statebuffer)

    def next_turn(self):
        if self.currentTurn < 3:
            self.currentTurn += 1
        else:
            self.currentTurn = 0

    def repartir_a(self):
        for agent_id in self.playerOrder:
            cartas_jugador = [self.mazo.pop(0),self.mazo.pop(1)]
            self.playerCards[agent_id] = cartas_jugador

    def select_blinds(self):
            self.smallBlindId = self.agents[0]
            self.bigBlindId = self.agents[1]
            self.deduct_chips(self.smallBlindId,self.smallBlind)
            self.deduct_chips(self.bigBlindId,self.bigBlind)


    def deduct_chips(self,agent_id,amount):
        currentChips = self.playerChips[agent_id]
        if currentChips > 0 and currentChips >= amount:
            self.playerChips[agent_id] -= amount
            self.pot += amount
        else:
            self.playerChips[agent_id] -= currentChips #all in / no le quedan chips
            self.pot += currentChips
        
    def is_turn(self, agent_id):
        if agent_id in self.agents and not(agent_id in self.foldedPlayers):
            return self.currentTurn == self.playerOrder[agent_id]

    def check_bet(self,agent_id):
        if agent_id in self.agents:
            self.deduct_chips(agent_id,self.maxBet)
            self.playerBets[agent_id] = self.maxBet
            self.next_turn()
        
    def raise_bet(self,agent_id,amount):
        if agent_id in self.agents:            
            if amount>self.maxBet:
                self.deduct_chips(agent_id,amount)
                self.playerBets[agent_id] = amount
                self.next_turn()
            else:
                self.check_bet(agent_id)

    def fold(self, agent_id):
        if agent_id in self.agents:
            self.foldedPlayers.append(agent_id)

    def clean_bets(self):
        for agent in self.agents:
            self.playerBets[agent] = 0

    def has_called(self):
        all_called = True
        for agent in self.agents:
            if not(agent in self.foldedPlayers) and not(self.playerBets[agent] == self.maxBet):
                all_called = False
        return all_called
                        
    def all_betted(self):
        while not(self.has_called()):
            self.has_called()
        return self.has_called()

    def round(self):
        self.currentTurn(0)
        while not(self.all_betted()):
            self.all_betted()
    

    def add_cards_to_table(self,amount):
        for i in range(0,amount-1):
            self.cardsOnTableAmount += 1
            card = self.mazo.pop(0)
            self.cardsOnTable[self.cardsOnTableAmount] = card

    def stage_0(self): # Reparte las cartas a cada jugador
        self.repartir_a()
    
    def stage_1(self): # Primera ronda de apuestas (PreFlop)
        self.clean_bets
        self.select_blinds()
        self.round()

    def stage_2(self): # Segunda ronda de apuestas (Flop)
        self.clean_bets
        self.select_blinds()
        self.add_cards_to_table(3)
        self.round

    def stage_3(self): # Tercera ronda de apuestas (Turn)
        self.clean_bets
        self.select_blinds()
        self.add_cards_to_table(1)
        self.round

    def stage_4(self): # Cuarta ronda de apuestas (River)
        self.clean_bets
        self.select_blinds
        self.add_cards_to_table(1)
        self.round

    def stage_5(self):  # Showdown
        self.get_winner()
    
    def get_property(self, agent_id: int, property_name: str) -> dict:
        if agent_id in self._agents:
            response = {"agent": agent_id}

            property_methods = {
                "turn": self.is_turn,
                "chips": self.playerChips[agent_id],
                "hand cards": self.playerCards[agent_id],
                "table cards": self.cardsOnTable,
                "maxBet": self.maxBet,
                "pot": self.pot,
            }

            property_method = property_methods.get(property_name)

            if property_method:
                response[property_name] = property_method(agent_id)
            else:
                print(f"Invalid property: {property_name}")

            return response
        else:
            return {}
    
    def take_action(self, agent_id: int, action_name: str, params: dict = {}) -> None:
        if agent_id in self._agents and self.is_turn(agent_id):
            action_methods = {
                "fold": (self.fold,[]),
                "raise": (self.raise_bet,["ammount"]),
                "check": (self.check_bet,["maxBet"])
            }
            action_method, expected_params = action_methods.get(action_name, (None, None))
            if action_method:
                args = [agent_id] + [params.get(param) for param in expected_params]
                action_method(*args)
                self._update_statebuffers(agent_id)
            else:
                print(f"Invalid action: {action_name}")
    