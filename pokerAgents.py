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
        self.


class Turn(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="turn")
        return response["turn"]

class CurrentBet(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(property_name="maxBet")
        return response["maxBet"]
# un sensor de pozo

class Check(SimulatedActuator):
    def act(self, bet: CurrentBet):
        request_info = {"maxBet":betValue}
        if request_info["maxBet"] >= bet :
                self._env.take_action(self._agent.id,"check")
# deberia saber su cantidad de fichas, pero el entorno tambien
class Raise(SimulatedActuator):

class Fold(SimulatedActuator):
