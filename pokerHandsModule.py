import itertools
from collections import Counter


class Card():
    def __init__(self):
        self.valor = None
        self.palo = None

    def __repr__(self):
        return f"{self.valor} de {self.palo}"


class Deck():
    def __init__(self):
        self._valores = ['As', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jota', 'Reina', 'Rey']
        self._palos = ['Corazon', 'Pica', 'Trebol', 'Espada']
        self.deck = self._armarMazo(self._valores, self._palos)

    def _armarMazo(self, valores, palos):  # genera un mazo desde 0
        mazo = []
        for palo in palos:
            for valor in valores:
                carta = Card()
                carta.palo = palo
                carta.valor = valor
                mazo.append(carta)
        return mazo


class EvaluadorPoker():
    # valor numérico de cada carta para poder compararlas y armar escaleras
    VALORES_ORDEN = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
        '9': 9, '10': 10, 'Jota': 11, 'Reina': 12, 'Rey': 13, 'As': 14
    }

    NOMBRES_RANKING = {
        9: "Escalera Real",
        8: "Escalera de Color",
        7: "Poker",
        6: "Full House",
        5: "Color",
        4: "Escalera",
        3: "Trio",
        2: "Doble Par",
        1: "Par",
        0: "Carta Alta"
    }

    @classmethod
    def valor_numerico(cls, valor):
        return cls.VALORES_ORDEN[valor]

    @classmethod
    def evaluar_mano(cls, cartas):
        if len(cartas) < 5:
            raise ValueError("Se necesitan al menos 5 cartas para evaluar una mano")

        mejor_resultado = None
        for combinacion in itertools.combinations(cartas, 5):
            resultado = cls._evaluar_5_cartas(combinacion)
            if mejor_resultado is None or resultado > mejor_resultado:
                mejor_resultado = resultado
        return mejor_resultado

    @classmethod
    def _evaluar_5_cartas(cls, cinco_cartas):
        valores = sorted([cls.valor_numerico(c.valor) for c in cinco_cartas], reverse=True)
        palos = [c.palo for c in cinco_cartas]

        conteo_valores = Counter(valores)
        es_color = len(set(palos)) == 1

        # Detectar escalera, incluyendo el caso especial As-2-3-4-5 ("escalera baja")
        valores_unicos = sorted(set(valores), reverse=True)
        es_escalera = False
        valor_alto_escalera = None

        if len(valores_unicos) == 5:
            if valores_unicos[0] - valores_unicos[4] == 4:
                es_escalera = True
                valor_alto_escalera = valores_unicos[0]
            elif valores_unicos == [14, 5, 4, 3, 2]:
                es_escalera = True
                valor_alto_escalera = 5  # el As juega como carta baja (1)

        # Grupos ordenados por (cantidad de repeticiones, valor), ambos descendente
        grupos = sorted(conteo_valores.items(), key=lambda x: (x[1], x[0]), reverse=True)
        cantidades = sorted(conteo_valores.values(), reverse=True)

        # Escalera Real / Escalera de Color
        if es_escalera and es_color:
            if valor_alto_escalera == 14:
                return (9, cls.NOMBRES_RANKING[9], [14])
            return (8, cls.NOMBRES_RANKING[8], [valor_alto_escalera])

        # Poker (Four of a Kind)
        if cantidades[0] == 4:
            valor_cuarteto = grupos[0][0]
            kicker = grupos[1][0]
            return (7, cls.NOMBRES_RANKING[7], [valor_cuarteto, kicker])

        # Full House
        if cantidades[0] == 3 and cantidades[1] == 2:
            valor_trio = grupos[0][0]
            valor_par = grupos[1][0]
            return (6, cls.NOMBRES_RANKING[6], [valor_trio, valor_par])

        # Color
        if es_color:
            return (5, cls.NOMBRES_RANKING[5], valores)

        # Escalera
        if es_escalera:
            return (4, cls.NOMBRES_RANKING[4], [valor_alto_escalera])

        # Trio
        if cantidades[0] == 3:
            valor_trio = grupos[0][0]
            kickers = sorted([v for v in valores if v != valor_trio], reverse=True)
            return (3, cls.NOMBRES_RANKING[3], [valor_trio] + kickers)

        # Doble Par
        if cantidades[0] == 2 and cantidades[1] == 2:
            pares = sorted([g[0] for g in grupos if g[1] == 2], reverse=True)
            kicker = [v for v in valores if v not in pares][0]
            return (2, cls.NOMBRES_RANKING[2], pares + [kicker])

        # Par
        if cantidades[0] == 2:
            valor_par = grupos[0][0]
            kickers = sorted([v for v in valores if v != valor_par], reverse=True)
            return (1, cls.NOMBRES_RANKING[1], [valor_par] + kickers)

        # Carta Alta
        return (0, cls.NOMBRES_RANKING[0], valores)

    @classmethod
    def determinar_ganador(cls, cartasJugadores):
        
        #cartasJugadores: dict {nombre_jugador: lista_de_cartas}
        #Cada lista de cartas debe incluir las cartas propias + comunitarias.
        #Retorna: (nombre_ganador, resultado_evaluado)
        #Si hay empate exacto, retorna el primero encontrado con ese resultado
        #y se puede detectar el empate comparando resultados manualmente.
        
        resultados = {
            jugador: cls.evaluar_mano(cartas)
            for jugador, cartas in cartasJugadores.items()
        }
        ganador = max(resultados, key=lambda j: resultados[j])
        return ganador, resultados[ganador], resultados


if __name__ == "__main__":
    # --- Ejemplo de uso ---
    def crear_carta(valor, palo):
        c = Card()
        c.valor = valor
        c.palo = palo
        return c

    # Jugador 1: tiene un Color (Color de Corazones)
    jugador1 = [
        crear_carta('As', 'Corazon'),
        crear_carta('Rey', 'Corazon'),
    ]
    comunitarias = [
        crear_carta('10', 'Corazon'),
        crear_carta('4', 'Corazon'),
        crear_carta('2', 'Corazon'),
        crear_carta('7', 'Pica'),
        crear_carta('9', 'Trebol'),
    ]

    # Jugador 2: tiene un Full House
    jugador2 = [
        crear_carta('9', 'Pica'),
        crear_carta('9', 'Espada'),
    ]

    resultado1 = EvaluadorPoker.evaluar_mano(jugador1 + comunitarias)
    resultado2 = EvaluadorPoker.evaluar_mano(jugador2 + comunitarias)

    print("Jugador 1:", resultado1)
    print("Jugador 2:", resultado2)

    ganador, resultado_ganador, todos = EvaluadorPoker.determinar_ganador({
        "Jugador 1": jugador1 + comunitarias,
        "Jugador 2": jugador2 + comunitarias,
    })
    print(f"\nGana: {ganador} con {resultado_ganador[1]}")