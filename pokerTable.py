import pokerAgents
from environments import SimulatedEnvironment
import random

class Card():
    def __init__(self):
        self.valor = None 
        self.palo = None

class Deck(): 
    def __init__(self):
        self._valores = ['As','2','3','4','5','6','7','8','9','10','Jota','Reina','Rey']
        self._palos = ['Corazon','Pica','Trebol','Espada']
        self.deck = self._armarMazo(self.valores,self.palos)
    def _armarMazo(self,valores,palos): #Genera un mazo desde 0    
        mazo = []
        for palo in palos:
            for valor in valores:
                carta = Card()
                carta.palo = palo
                carta.valor = valor
                mazo.append(carta)
        return mazo

class PokerTable(SimulatedEnvironment):
    def __init__(self):
        self.agents = [] #Lista de jugadores
        self.stages = [0,1,2,3,4,5] # 0 = Repartir, 1 = PreFlop, 2 = Flop, 3 = Turn, 4 = River, 5 = Showdown
        self._statebuffers = [] #No se que hace esto pero lo dejo porlasdudas
        self.mazo = random.shuffle(Deck().deck) #Este es el mazo pero lo mezcla previamente
        self.smallBlind = 5
        self.largeBlind = 2*self.smallBlind
        self.maxBet = self.largeBlind
        self.playerOrder = self.ordenJuego()

    def ordenJuego(self):
        copiaListaJugadores = self.agents.copy().shuffle()
        ordenJugadores = {}
        i=1
        for player in copiaListaJugadores:
            ordenJugadores[i] = player
            i += 1
        return ordenJugadores
        
    def add(self, agent_id: int) -> None:
        if not(agent_id in self._agents):
            self._agents.append(agent_id)

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

    def repartir_a(self, agent_id: int, action_name: str):
        cartas_jugador = (self.mazo.pop(0),self.mazo.pop(1))
        return cartas_jugador
    
    def stage_0(self): # Reparte las cartas a cada jugador
        for agent_id in self.playerOrder:
            self.repartir_a(self, agent_id,'repartir')
        self.agents
        
    
    def stage_1(self): # Primera ronda de apuestas (PreFlop)



    #def partida(self):
    #    for stages in self.stages:
    
    
    #def get_property(self, agent_id: int, property_name: str) -> dict:
    #    pass

    #def take_action(self, agent_id: int, action_name: str, params: dict = {}) -> None:
    #    pass
    
    