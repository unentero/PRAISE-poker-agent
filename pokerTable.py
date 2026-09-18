import pokerAgents
from pokerHandsModule import Deck, EvaluadorPoker
from statebuffer import IStateBuffer
from environments import SimulatedEnvironment
import random

class PokerTable(SimulatedEnvironment):
    def __init__(self):
        super().__init__()
        self._agents = [] #Lista de jugadores
        self.agentsAlias = {}
        self.currentStage = 0  # 0 = Repartir, 1 = PreFlop, 2 = Flop, 3 = Turn, 4 = River, 5 = Showdown
        self._statebuffers = [] #No se que hace esto pero lo dejo porlasdudas
        self.mazo = Deck().deck
        random.shuffle(self.mazo) #Este es el mazo pero lo mezcla previamente
        self.smallBlind = 5
        self.bigBlind = 2*self.smallBlind
        self.maxBet = self.bigBlind
        self.smallBlindId = 0
        self.bigBlindId = 0
        self.pot = 0
        self.playerOrder = {}
        self.foldedPlayers = []
        self.currentTurn = 0
        self.playerCards = {}
        self.playerChips = {}
        self.playerBets = {}
        self.cardsOnTable = []
        self.tableSize = 4
        self.gameWinner = ""
        
    def add(self, agent_id: int) -> None:
        playersAmmount = 0
        numberPlayer = 0 
        if not(agent_id in self._agents) and playersAmmount <= self.tableSize:   
            self._agents.append(agent_id)
            self.playerOrder[agent_id] = numberPlayer
            self.agentsAlias[agent_id] = "Player " + str(numberPlayer)
            self.playerCards[agent_id] = []
            self.playerChips[agent_id] = 0
            self.playerBets[agent_id] = 0
            numberPlayer += 1
            playersAmmount += 1     

    def remove(self, agent_id: int) -> None:
        if agent_id in self._agents:
            self._agents.remove(agent_id)

    def add_statebuffer(self, agent_id: int, statebuffer: IStateBuffer) -> None:
        super(PokerTable, self).add_statebuffer(agent_id, statebuffer)
        statebuffer.update({"name": self.agentsAlias[agent_id], "stage": self.currentStage,"player cards": self.playerCards[agent_id],
                         "table cards": self.cardsOnTable, "pot" : self.pot, "winner":self.gameWinner})

    def remove_statebuffer(self, agent_id: int,statebuffer: IStateBuffer) -> None:
        super(PokerTable, self).remove_statebuffer(agent_id, statebuffer)

    def next_turn(self):
        if self.currentTurn < 3:
            self.currentTurn += 1
        else:
            self.currentTurn = 0

    def next_stage(self):
            if self.currentStage < 4:
                self.currentStage += 1
            #else:
            #    self.currentStage = 0
    
    def repartir(self):
        for agent_id in self._agents:
            cartas_jugador = [self.mazo.pop(0),self.mazo.pop(1)]
            self.playerCards[agent_id] = cartas_jugador

    def select_blinds(self):
            self.smallBlindId = self._agents[0]
            self.bigBlindId = self._agents[1]
            self.deduct_chips(self.smallBlindId,self.smallBlind)
            self.deduct_chips(self.bigBlindId,self.bigBlind)

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

    def check_bet(self,agent_id):
        if agent_id in self._agents:
            if self.maxBet >= self.playerChips[agent_id]:
                allin_bet = self.playerChips[agent_id]
                self.deduct_chips(agent_id,allin_bet)
                self.playerBets[agent_id] = allin_bet
                self.next_turn()
            else:
                self.deduct_chips(agent_id,self.maxBet)
                self.playerBets[agent_id] = self.maxBet
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
        for agent in self._agents:
            self.playerBets[agent] = 0

    def has_called(self) -> bool:
        active_players = [agent for agent in self._agents if agent  not in self.foldedPlayers]
        if len(active_players) <= 1:
            return True
        for agent_id in active_players:
            if self.playerBets.get(agent_id, 0) < self.maxBet:
                return False
        return True
    
    def add_cards_to_table(self,amount):
        for i in range(amount):
            card = self.mazo.pop(0)
            self.cardsOnTable.append(card)

    def get_winner(self):
        all_cards = {}
        cards_table = []
        for n in range(0,4):
            cards_table.append(self.cardsOnTable[n])
        for agent_id in self._agents:
            all_cards[agent_id] = self.playerCards[agent_id] + cards_table
        winnerID , resultado = EvaluadorPoker.determinar_ganador(all_cards)
        self.gameWinner = self.agentsAlias[winnerID]
        self.add_chips(winnerID,self.pot)
        return winnerID, resultado

    def all_players_have_cards(self):
        for agent_id in self._agents:
            if agent_id not in self.playerCards or len(self.playerCards[agent_id]) == 0:
                return False
        return True

    def prepare_stage_0(self,base_chips): # Reparte las cartas a cada jugador
        self.repartir()
        for agent_id in self._agents:
            self.add_chips(agent_id, base_chips)
        self.next_stage()
    
    def prepare_stage_1(self): # Primera ronda de apuestas (PreFlop)
        self.clean_bets()
        self.currentTurn = 0
        self.select_blinds()


    def prepare_stage_2(self): # Segunda ronda de apuestas (Flop)
        self.clean_bets()
        self.select_blinds()
        self.add_cards_to_table(3)


    def prepare_stage_3(self): # Tercera ronda de apuestas (Turn)
        self.clean_bets()
        self.select_blinds()
        self.add_cards_to_table(1)


    def prepare_stage_4(self): # Cuarta ronda de apuestas (River)
        self.clean_bets()
        self.select_blinds()
        self.add_cards_to_table(1)

    def prepare_stage_5(self):  # Showdown
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
                
                # Lógica de avance de stages (usar llamadas reales a los métodos)
                if self.has_called():
                    if self.currentStage == 0:
                        self.prepare_stage_0(1000)
                    elif self.all_players_have_cards():
                        self.prepare_stage_1()
                    elif not self.all_folded() and not (self.pot == 0):
                        self.prepare_stage_2()
                    elif not self.all_folded() and len(self.cardsOnTable) == 3:
                        self.prepare_stage_3()
                    elif not self.all_folded() and len(self.cardsOnTable) == 4:
                        self.prepare_stage_4()
                    elif not self.all_folded() and len(self.cardsOnTable) == 5:
                        self.prepare_stage_5()
                    elif self.all_folded():
                        winnerID = next((a for a in self._agents if a not in self.foldedPlayers), None)
                        if winnerID is not None:
                            self.gameWinner = self.agentsAlias[winnerID]
                            self.add_chips(winnerID, self.pot)
                self._update_statebuffers(agent_id)
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

    def _update_statebuffers(self, agent_id: int) -> None:
        relevant_statebuffers = [entry["statebuffer"] for entry in self._statebuffers if entry["agent_id"] == agent_id]
        for statebuffer in relevant_statebuffers:
            statebuffer.update(self._get_state_for_agent(agent_id))
