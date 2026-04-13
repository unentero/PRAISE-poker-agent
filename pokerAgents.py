from agents import Agent
from environments import SimulatedSensor, SimulatedActuator, SimulatedEnvironment
import uuid

class PokerAgent(Agent):
    def __init__(self):
        self._uuid = uuid.uuid1()
        self._cards=[]
        self._sensors = {}
        self._actuators = {}
        self.isSmallBlind = False
        self.isLargeBlind = False
        self.chips = 0 # placeholder para un valor mas adelante


class Turn(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="turn")
        return response["turn"]

class CurrentBet(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(property_name="maxBet")
        return response["maxBet"]

class PotSensor(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(property_name="pot")
        return response["pot"]

class Check(SimulatedActuator):
    def act(self, bet: CurrentBet):
        request_info = "maxBet"
        if request_info["maxBet"] == bet :
            self._env.take_action(self._agent.id,"check")
        elif request_info["maxBet"] > bet:
            self._env.take_action(self._agent.id,"check-allin")

class Raise(SimulatedActuator):
    def act(self, bet: CurrentBet):
        request_info = {"playerPot": playerChips ,"maxBet": currentMax}
        if request_info["maxBet"]<= bet and bet <= request_info["playerPot"]:
                self._env.take_action(self._agent.id,"raise")

class Fold(SimulatedActuator):
    def act(self):
        self._env.take_action(self._agent.id,"fold")

# deberia saber su cantidad de fichas, pero el entorno tambien