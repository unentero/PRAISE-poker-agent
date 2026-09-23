import pokerAgents
from pokerHandsModule import Deck, EvaluadorPoker
from statebuffer import IStateBuffer
from environments import SimulatedEnvironment
import random

class PokerTable(SimulatedEnvironment):
    def __init__(self,size,base_chips):
        super().__init__()
        # basic items
        self._agents = [] 
        self._statebuffers = [] 
        self.mazo = Deck().deck
        random.shuffle(self.mazo) 
        # player info
        self.agentsAlias = {}
        self.playerOrder = {}
        self.foldedPlayers = []
        self.playerCards = {}
        self.playerChips = {}
        self.playerBets = {}
        self.gameWinner = ""
        # table parameters
        self.smallBlind = 5
        self.bigBlind = 2*self.smallBlind
        self.maxBet = 0
        self.smallBlindId = 0
        self.bigBlindId = 0
        self.currentTurn = 0
        self.currentStage = -1  
        self.pot = 0
        self.cardsOnTable = []
        self.tableSize = size
        self.baseChips = base_chips
        
    def add(self, agent_id: int) -> None:
        if not(agent_id in self._agents) and len(self._agents) < self.tableSize:   
            self._agents.append(agent_id)
            self.playerOrder[agent_id] = len(self._agents)-1
            self.agentsAlias[agent_id] = "Player " + str(len(self._agents))
            self.playerCards[agent_id] = []
            self.playerChips[agent_id] = 0
            self.playerBets[agent_id] = 0
            self.add_chips(agent_id, self.baseChips) 

    def remove(self, agent_id: int) -> None:
        if agent_id in self._agents:
            self._agents.remove(agent_id)

    def add_statebuffer(self, agent_id: int, statebuffer: IStateBuffer) -> None:
        super(PokerTable, self).add_statebuffer(agent_id, statebuffer)
        statebuffer.update(
            {"name": self.agentsAlias[agent_id], 
            "stage": self.currentStage,
            "player cards": self.playerCards[agent_id],
            "table cards": self.cardsOnTable,
            "chips": self.playerChips[agent_id],
            "maxBet": self.maxBet,  
            "pot" : self.pot, 
            "winner":self.gameWinner
            })

    def remove_statebuffer(self, agent_id: int,statebuffer: IStateBuffer) -> None:
        super(PokerTable, self).remove_statebuffer(agent_id, statebuffer)

    def next_turn(self):
        if self.currentTurn < len(self._agents)-1:
            self.currentTurn += 1
        else:
            self.currentTurn = 0

    def has_called(self):
        active_players = [agent for agent in self._agents if agent  not in self.foldedPlayers]
        if len(active_players) <= 1:
            all_called = True
        all_called = True
        for agent_id in active_players:
            if self.playerBets.get(agent_id, 0) < self.maxBet:
                all_called = False
                break
        return all_called
    
    def repartir(self):
        for agent_id in self._agents:
            cartas_jugador = [self.mazo.pop(0),self.mazo.pop(1)]
            self.playerCards[agent_id] = cartas_jugador

    def select_blinds(self):
            self.smallBlindId = self._agents[0]
            self.bigBlindId = self._agents[1]
            self.deduct_chips(self.smallBlindId,self.smallBlind)
            self.deduct_chips(self.bigBlindId,self.bigBlind)
            self.playerBets[self.smallBlindId] += self.smallBlind
            self.playerBets[self.bigBlindId] += self.bigBlind

    def add_chips(self,agent_id,amount):
        self.playerChips[agent_id] += amount

    def deduct_chips(self,agent_id,amount):
        currentChips = self.playerChips[agent_id]
        if currentChips > 0 and currentChips >= amount:
            self.playerChips[agent_id] -= amount
            self.pot += amount
        else:
            self.playerChips[agent_id] -= currentChips #all in / no le quedan chips
            self.pot += currentChips
        
    def is_turn(self, agent_id):
        if agent_id in self._agents and not(agent_id in self.foldedPlayers):
            return self.currentTurn == self.playerOrder[agent_id]

    def check_bet(self, agent_id):
        if agent_id in self._agents:
            amount_to_call = self.maxBet - self.playerBets.get(agent_id, 0)
            if amount_to_call > 0:
                self.deduct_chips(agent_id, amount_to_call)
                self.playerBets[agent_id] += amount_to_call
            self.next_turn()
        
    def raise_bet(self,agent_id,amount):
        if agent_id in self._agents:            
            if amount>self.maxBet:
                self.deduct_chips(agent_id,amount)
                self.playerBets[agent_id] = amount
                self.next_turn()
            else:
                self.check_bet(agent_id)

    def fold(self, agent_id):
        if agent_id in self._agents:
            self.foldedPlayers.append(agent_id)

    def clean_bets(self):
        self.maxBet = 0
        for agent in self._agents:
            self.playerBets[agent] = 0
    
    def add_cards_to_table(self,amount):
        for i in range(amount):
            card = self.mazo.pop(0)
            self.cardsOnTable.append(card)

    def get_winner(self):
        all_cards = {}
        cards_table = self.cardsOnTable[:5]
        for agent_id in self._agents:
            all_cards[agent_id] = self.playerCards.get(agent_id,[]) + cards_table
        
        winnerID , resultado = EvaluadorPoker.determinar_ganador(all_cards)
        self.gameWinner = self.agentsAlias[winnerID]
        self.add_chips(winnerID,self.pot)
        return winnerID, resultado

    def all_players_have_cards(self):
        for agent_id in self._agents:
            if agent_id not in self.playerCards or len(self.playerCards[agent_id]) == 0:
                return False
        return True

    def mesa_llena(self):
        return self.tableSize == len(self._agents) 
    
    def prepare_stage_0(self): # Reparte cartas e inicializa fichas
        self.currentStage = 0
        self.maxBet = 0
        self.clean_bets()
        self.repartir()
        self.select_blinds()
            
    def prepare_stage_1(self): # PreFlop
        self.currentStage = 1
        self.clean_bets()
        self.currentTurn = 0
        self.maxBet = self.bigBlind
        

    def prepare_stage_2(self): # Flop
        self.currentStage = 2
        self.currentTurn = 0
        self.clean_bets()
        self.add_cards_to_table(3)

    def prepare_stage_3(self): # Turn
        self.currentStage = 3
        self.currentTurn = 0
        self.clean_bets()
        self.add_cards_to_table(1)

    def prepare_stage_4(self): # River
        self.currentStage = 4
        self.currentTurn = 0
        self.clean_bets()
        self.add_cards_to_table(1)

    def prepare_stage_5(self): # Showdown
        self.currentStage = 5
        self.get_winner()
    
    def all_folded(self):
        return (len(self.foldedPlayers) == self.tableSize -1)

    def get_player_chips(self, agent_id):
        if agent_id in self._agents:
            return self.playerChips[agent_id]
        else:
            return 0

    def get_player_cards(self, agent_id):
        if agent_id in self._agents:
            return self.playerCards[agent_id]
        else:
            return []
        
    def get_table_cards(self,agent_id):
        return self.cardsOnTable

    def get_maxBet(self,agent_id):
        return self.maxBet

    def get_pot(self,agent_id):
        return self.pot

    def get_property(self, agent_id: int, property_name: str) -> dict:
        if agent_id in self._agents:
            response = {"agent": agent_id}
            property_methods = {
                "turn": self.is_turn,
                "chips": self.get_player_chips,
                "hand cards": self.get_player_cards,
                "table cards": self.get_table_cards,
                "maxBet": self.get_maxBet,
                "pot": self.get_pot,
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
                "raise": (self.raise_bet,["amount"]),
                "check": (self.check_bet,[])
            }
            action_method, expected_params = action_methods.get(action_name, (None, None))
            if action_method:
                args = [agent_id] + [params.get(param) for param in expected_params]
                action_method(*args)
                if self.mesa_llena() and self.currentStage == -1:
                    self.prepare_stage_0()
                elif self.currentStage == 0:
                    self.prepare_stage_1()
                #logica has_called
                if self.all_players_have_cards:
                    if self.has_called():
                        if self.all_folded():
                            winnerID = next((a for a in self._agents if a not in self.foldedPlayers), None)
                            if winnerID is not None:
                                self.gameWinner = self.agentsAlias[winnerID]
                                self.add_chips(winnerID, self.pot)   
                        elif self.currentStage == 1:
                            self.prepare_stage_2()
                        elif len(self.cardsOnTable)==3 and self.currentStage == 2:
                            self.prepare_stage_3()
                        elif len(self.cardsOnTable)==4 and self.currentStage == 3:
                            self.prepare_stage_4()
                        elif len(self.cardsOnTable)==5 and self.currentStage == 4:
                            self.prepare_stage_5()
                self._update_statebuffers()
            else:
                print(f"Invalid action: {action_name}")
    def _get_state_for_agent(self, agent_id: int) -> dict:
        return {
            "name": self.agentsAlias.get(agent_id, f"player_{agent_id}"),
            "player cards": self.playerCards.get(agent_id, []),
            "table cards": self.cardsOnTable,
            "pot": self.pot,
            "stage": self.currentStage,
            "winner": self.gameWinner,
            "maxBet": self.maxBet,
            "chips": self.playerChips.get(agent_id, 0),
        }

    def _update_statebuffers(self) -> None:
        for entry in self._statebuffers:
            a_id = entry["agent_id"]
            sb = entry["statebuffer"]
            sb.update(self._get_state_for_agent(a_id))
