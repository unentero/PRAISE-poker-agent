from agents import Agent
from environments import SimulatedSensor, SimulatedActuator, SimulatedEnvironment


class Turn(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="turn")
        return response.get("turn", False)


class CurrentBet(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="maxBet")
        return response.get("maxBet", 0)


class PotSensor(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="pot")
        return response.get("pot", 0)


class TableCards(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="table cards")
        return response.get("table cards", [])


class HandCards(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="hand cards")
        return response.get("hand cards", [])


class Chips(SimulatedSensor):
    def sense(self):
        response = self._env.get_property(self._agent.id, property_name="chips")
        return response.get("chips", 0)


class Check(SimulatedActuator):
    def act(self):
        self._env.take_action(self._agent.id, "check")


class Raise(SimulatedActuator):
    def act(self, amount=0):
        self._env.take_action(self._agent.id, "raise", {"amount": amount})


class Fold(SimulatedActuator):
    def act(self):
        self._env.take_action(self._agent.id, "fold")


class PokerAgent(Agent):
    def function(self, percept):
        if percept.get("turn", False):
            return {"name": "check", "params": {}}
        return {"name": "fold", "params": {}}

    def __init__(self, env: SimulatedEnvironment):
        super().__init__()
        env.add(self.id)

        check_actuator = Check(env)
        check_actuator.agent = self
        self.add_actuator("check", check_actuator)

        raise_actuator = Raise(env)
        raise_actuator.agent = self
        self.add_actuator("raise", raise_actuator)

        fold_actuator = Fold(env)
        fold_actuator.agent = self
        self.add_actuator("fold", fold_actuator)

        turn_sensor = Turn(env)
        turn_sensor.agent = self
        self.add_sensor("turn", turn_sensor)

        current_bet_sensor = CurrentBet(env)
        current_bet_sensor.agent = self
        self.add_sensor("maxBet", current_bet_sensor)

        pot_sensor = PotSensor(env)
        pot_sensor.agent = self
        self.add_sensor("pot", pot_sensor)

        table_cards_sensor = TableCards(env)
        table_cards_sensor.agent = self
        self.add_sensor("table cards", table_cards_sensor)

        hand_cards_sensor = HandCards(env)
        hand_cards_sensor.agent = self
        self.add_sensor("hand cards", hand_cards_sensor)

        chips_sensor = Chips(env)
        chips_sensor.agent = self
        self.add_sensor("chips", chips_sensor)

    def _perceive(self):
        percept = {}
        for sensor_name in self._sensors:
            percept[sensor_name] = self._sensors[sensor_name].sense()
        return percept

    def _act(self, percept):
        action = self.function(percept)
        action_actuators = {
            "check": (self._actuators["check"], []),
            "fold": (self._actuators["fold"], []),
            "raise": (self._actuators["raise"], ["amount"]),
        }

        actuator, expected_params = action_actuators.get(action.get("name"), (None, None))
        if actuator is None:
            return

        params = action.get("params", {})
        args = [params.get(param) for param in expected_params]
        actuator.act(*args)

    def behave(self):
        percept = self._perceive()
        self._act(percept)
