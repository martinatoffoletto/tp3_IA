'''
TP3 - Algoritmos Geneticos

Condiciones
~~~~~~~~~~~
1. Hay 5 casas.
2. El Matematico vive en la casa roja.
3. El hacker programa en Python.
4. El Brackets es utilizado en la casa verde.
5. El analista usa Atom.
6. La casa verde esta a la derecha de la casa blanca.   (interpretado como INMEDIATAMENTE a la derecha)
7. La persona que usa Redis programa en Java
8. Cassandra es utilizado en la casa amarilla
9. Notepad++ es usado en la casa del medio.
10. El Desarrollador vive en la primer casa.
11. La persona que usa HBase vive al lado de la que programa en JavaScript.
12. La persona que usa Cassandra es vecina de la que programa en C#.
13. La persona que usa Neo4J usa Sublime Text.
14. El Ingeniero usa MongoDB.
15. EL desarrollador vive en la casa azul.

Quien usa vim?

Resumen:
Colores = Rojo, Azul, Verde, Blanco, Amarillo
Profesiones = Matematico, Hacker, Ingeniero, Analista, Desarrollador
Lenguaje = Python, C#, JAVA, C++, JavaScript
BD = Cassandra, MongoDB, Neo4j, Redis, HBase
editor = Brackets, Sublime Text, Atom, Notepad++, Vim

Diseño del individuo
~~~~~~~~~~~~~~~~~~~~
Cromosoma = lista de 25 genes; cada gen es un codigo binario de 3 bits.
Orden por casa: chromosome[casa*5 + atributo], atributo = 0 color, 1 profesion,
2 lenguaje, 3 base de datos, 4 editor (el mismo orden que usa decode()).
Invariante: para cada atributo, las 5 casas tienen los 5 codigos validos sin
repetir (una permutacion). Los codigos '000', '110' y '111' no se usan.
Todos los operadores (generacion, cruce, mutacion) preservan el invariante.
'''

import argparse
import random
import time


colors =      {'001' : 'red',          '010' : 'blue',          '011' : 'green',    '100' : 'white',    '101' : 'yellow'}
prefession =  {'001' : 'Mathematician','010' : 'Hacker',        '011' : 'Engineer', '100' : 'Analyst',  '101' : 'Developer'}
languaje =    {'001' : 'Python',       '010' : 'C#',            '011' : 'Java',     '100' : 'C++',      '101' : 'JavaScript'}
database =    {'001' : 'Cassandra',    '010' : 'MongoDB',       '011' : 'HBase',    '100' : 'Neo4j',    '101' : 'Redis'}
editor =      {'001' : 'Brackets',     '010' : 'Sublime Text',  '011' : 'Vim',      '100' : 'Atom',     '101' : 'Notepad++'}

N_HOUSES = 5
ATTRIBUTES = [colors, prefession, languaje, database, editor]
ATTRIBUTE_NAMES = ['Color', 'Profesion', 'Lenguaje', 'Base de datos', 'Editor']
CODES = ['001', '010', '011', '100', '101']
COLOR, PROFESSION, LANGUAGE, DATABASE, EDITOR = range(5)

# Pistas 2..15 (la 1 la garantiza la estructura del cromosoma).
# p = posicion (0..4) de la casa donde aparece cada valor; todos los valores son unicos entre atributos.
# (numero, descripcion, atributos involucrados, chequeo)
CLUES = [
    (2,  'El Matematico vive en la casa roja',               (PROFESSION, COLOR),    lambda p: p['Mathematician'] == p['red']),
    (3,  'El hacker programa en Python',                     (PROFESSION, LANGUAGE), lambda p: p['Hacker'] == p['Python']),
    (4,  'Brackets se usa en la casa verde',                 (EDITOR, COLOR),        lambda p: p['Brackets'] == p['green']),
    (5,  'El analista usa Atom',                             (PROFESSION, EDITOR),   lambda p: p['Analyst'] == p['Atom']),
    (6,  'La casa verde esta inmediatamente a la derecha de la blanca', (COLOR,),    lambda p: p['green'] == p['white'] + 1),
    (7,  'Quien usa Redis programa en Java',                 (DATABASE, LANGUAGE),   lambda p: p['Redis'] == p['Java']),
    (8,  'Cassandra se usa en la casa amarilla',             (DATABASE, COLOR),      lambda p: p['Cassandra'] == p['yellow']),
    (9,  'Notepad++ se usa en la casa del medio',            (EDITOR,),              lambda p: p['Notepad++'] == 2),
    (10, 'El Desarrollador vive en la primer casa',          (PROFESSION,),          lambda p: p['Developer'] == 0),
    (11, 'HBase vive al lado de JavaScript',                 (DATABASE, LANGUAGE),   lambda p: abs(p['HBase'] - p['JavaScript']) == 1),
    (12, 'Cassandra es vecina de C#',                        (DATABASE, LANGUAGE),   lambda p: abs(p['Cassandra'] - p['C#']) == 1),
    (13, 'Quien usa Neo4j usa Sublime Text',                 (DATABASE, EDITOR),     lambda p: p['Neo4j'] == p['Sublime Text']),
    (14, 'El Ingeniero usa MongoDB',                         (PROFESSION, DATABASE), lambda p: p['Engineer'] == p['MongoDB']),
    (15, 'El desarrollador vive en la casa azul',            (PROFESSION, COLOR),    lambda p: p['Developer'] == p['blue']),
]

OK_SCORE = 1
FAIL_SCORE = -1
PUNISH_SCORE = -1
MAX_SCORE = OK_SCORE * len(CLUES)   # 14: todas las pistas cumplidas


class Phenotype:

    def __init__(self, chromosome=None):
        # crear un individuo: si no se recibe cromosoma, se genera uno aleatorio valido
        self.chromosome = list(chromosome) if chromosome is not None else self.random_chromosome()
        self.score = None
        self.failed_clues = []
        self.fitness_function()

    @staticmethod
    def random_chromosome():
        ''' una permutacion aleatoria de los 5 codigos por cada atributo '''
        columns = [random.sample(CODES, N_HOUSES) for _ in ATTRIBUTES]
        return [columns[a][h] for h in range(N_HOUSES) for a in range(len(ATTRIBUTES))]

    @classmethod
    def heuristic(cls):
        ''' individuo aleatorio "sembrado" con las pistas de posicion fija (9, 10 y 15) '''
        ind = cls()
        ind.place(PROFESSION, 'Developer', 0)
        ind.place(COLOR, 'blue', 0)
        ind.place(EDITOR, 'Notepad++', 2)
        ind.fitness_function()
        return ind

    def copy(self):
        return Phenotype(self.chromosome)

    def gene(self, house, attribute):
        return house * len(ATTRIBUTES) + attribute

    def swap(self, attribute, house_a, house_b):
        ''' intercambia el valor de un atributo entre dos casas: preserva la permutacion '''
        i, j = self.gene(house_a, attribute), self.gene(house_b, attribute)
        self.chromosome[i], self.chromosome[j] = self.chromosome[j], self.chromosome[i]

    def place(self, attribute, value, house):
        ''' mueve un valor a una casa intercambiandolo con el que estaba ahi '''
        current = next(h for h in range(N_HOUSES) if ATTRIBUTES[attribute][self.chromosome[self.gene(h, attribute)]] == value)
        self.swap(attribute, current, house)

    def decode(self):
        ''' traduce 0's y 1's (conjunto de genes: 3) en valores segun un diccionario '''
        return [[colors[self.chromosome[i*5+0]],
                 prefession[self.chromosome[i*5+1]],
                 languaje[self.chromosome[i*5+2]],
                 database[self.chromosome[i*5+3]],
                 editor[self.chromosome[i*5+4]]] for i in range(5)]

    @staticmethod
    def encode(houses):
        ''' inversa de decode: tabla de 5 casas x 5 valores -> cromosoma binario '''
        reverse = [{v: k for k, v in attr.items()} for attr in ATTRIBUTES]
        return [reverse[a][houses[h][a]] for h in range(N_HOUSES) for a in range(len(ATTRIBUTES))]

    def invalid_genes(self):
        ''' cantidad de genes con codigo inexistente o repetido dentro de su atributo '''
        invalid = 0
        for a in range(len(ATTRIBUTES)):
            column = [self.chromosome[self.gene(h, a)] for h in range(N_HOUSES)]
            valid = [c for c in column if c in ATTRIBUTES[a]]
            invalid += (len(column) - len(valid)) + (len(valid) - len(set(valid)))
        return invalid

    def mutate(self, optimized=True):
        ''' muta un fenotipo, optimizado: swap de dos casas dentro de un atributo.
            Si es optimizado, el atributo se elige entre los involucrados en pistas incumplidas. '''
        candidates = [a for _, _, attrs, _ in self.failed_clues for a in attrs]
        attribute = random.choice(candidates) if optimized and candidates else random.randrange(len(ATTRIBUTES))
        house_a, house_b = random.sample(range(N_HOUSES), 2)
        self.swap(attribute, house_a, house_b)
        self.fitness_function()

    def fitness_function(self):
        ''' calcula el valor de fitness del cromosoma segun el problema en particular '''

        self.score = 0
        self.failed_clues = []

        ok_score = OK_SCORE
        fail_score = FAIL_SCORE
        punish_score = PUNISH_SCORE

        # posicion de cada valor; ante genes invalidos/repetidos queda la ultima aparicion
        positions = {}
        for h in range(N_HOUSES):
            for a in range(len(ATTRIBUTES)):
                value = ATTRIBUTES[a].get(self.chromosome[self.gene(h, a)])
                if value is not None:
                    positions[value] = h

        for clue in CLUES:
            try:
                ok = clue[3](positions)
            except KeyError:    # falta algun valor: cromosoma invalido
                ok = False
            if ok:
                self.score += ok_score
            else:
                self.score += fail_score
                self.failed_clues.append(clue)

        self.score += punish_score * self.invalid_genes()
        return self.score

    def is_solution(self):
        return self.score == MAX_SCORE

    def who_uses(self, editor_name='Vim'):
        return next(house[PROFESSION] for house in self.decode() if house[EDITOR] == editor_name)

    def table(self):
        header = ['Casa'] + ATTRIBUTE_NAMES
        rows = [[str(i + 1)] + house for i, house in enumerate(self.decode())]
        widths = [max(len(r[c]) for r in [header] + rows) for c in range(len(header))]
        fmt = lambda r: ' | '.join(v.ljust(w) for v, w in zip(r, widths))
        return '\n'.join([fmt(header), '-+-'.join('-' * w for w in widths)] + [fmt(r) for r in rows])


class Riddle:

    def __init__(self, seed=None, verbose=True,
                 max_generations=1000, stagnation_limit=150,
                 crossover_prob=0.80, mutation_prob=0.80, optimized_mutation=True,
                 tournament_size=3, elite_rate=0.05, immigrant_rate=0.05,
                 init_method='random'):
        self.start_time = time.time()
        self.population = []
        self.seed = seed
        self.verbose = verbose
        self.max_generations = max_generations          # N2: condicion de corte 2
        self.stagnation_limit = stagnation_limit        # condicion de corte 3
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.optimized_mutation = optimized_mutation
        self.tournament_size = tournament_size
        self.elite_rate = elite_rate
        self.immigrant_rate = immigrant_rate
        self.init_method = init_method
        if seed is not None:
            random.seed(seed)

    def log(self, *args):
        if self.verbose:
            print(*args)

    '''
    proceso general
    '''
    def solve(self, n_population):

        self.generate(n_population, self.init_method)
        self.log(f"Población creada con {len(self.population)} individuos")
        self.log(self.population[0].chromosome)
        self.log(self.population[0].decode())

        self.log("Inicio del proceso iterativo")
        fit, indi = self.iterar()

        self.log(f"Fin del proceso ({self.stop_reason}, generación {self.generation}), mejor resultado \n - Fitness: {fit}/{MAX_SCORE} \n - Individuo {indi.chromosome} \n - Individuo {indi.decode()}")
        return fit, indi

    def iterar(self):

        counter = 0
        break_condition = False

        N = len(self.population)
        n_elite = max(1, int(N * self.elite_rate))
        n_immigrants = int(N * self.immigrant_rate)

        self.population.sort(key=lambda x: x.score, reverse=True)
        best_score = self.population[0].score
        last_improvement = 0
        self.history = []

        while not(break_condition):

            self.history.append(self.population[0].score)
            if counter % 100 == 0:
                self.log("--------------------------------")
                self.log(counter, f"mejor fitness: {self.population[0].score}")
                self.log(self.population[0].decode())

            # condicion de corte 1: se cumplen todas las pistas
            if self.population[0].is_solution():
                self.stop_reason = 'solución encontrada (cumple las 15 pistas)'
                break_condition = True
            # condicion de corte 2: maximo de generaciones
            elif counter >= self.max_generations:
                self.stop_reason = f'máximo de generaciones ({self.max_generations})'
                break_condition = True
            # condicion de corte 3: estancamiento del mejor fitness
            elif counter - last_improvement >= self.stagnation_limit:
                self.stop_reason = f'estancamiento ({self.stagnation_limit} generaciones sin mejora)'
                break_condition = True
            if break_condition:
                break

            # elitismo: los mejores pasan sin cambios
            new_population = [x.copy() for x in self.population[:n_elite]]

            # inmigrantes: individuos nuevos para mantener diversidad
            self.generate(n_immigrants, self.init_method, target=new_population)

            n_children = N - len(new_population)

            # seleccion
            parents = [self.select() for _ in range(n_children + n_children % 2)]

            # crossover
            crossed = []
            for s in range(0, len(parents), 2):
                crossed.extend(self.crossOver(parents[s], parents[s + 1], self.crossover_prob))

            # mutate
            self.mutate(crossed, self.mutation_prob)

            new_population.extend(crossed[:n_children])
            self.population = sorted(new_population, key=lambda x: x.score, reverse=True)

            counter += 1
            if self.population[0].score > best_score:
                best_score = self.population[0].score
                last_improvement = counter

        self.generation = counter
        return self.population[0].score, self.population[0]

    '''
    operacion: generar individuos y agregarlos a la poblacion
    '''
    def generate(self, i, method='random', target=None):
        target = self.population if target is None else target
        for x in range(0, i):
            newbie = Phenotype.heuristic() if method == 'heuristic' else Phenotype()
            target.append(newbie)

    '''
    operacion: seleccion por torneo. Gana el de mayor fitness entre k elegidos al azar
    '''
    def select(self):
        return max(random.sample(self.population, self.tournament_size), key=lambda x: x.score)

    '''
    operacion: mutación. Cambiar la configuración fenotipica de un individuo
    '''
    def mutate(self, crossed, prob=0.5):
        for individual in crossed:
            if random.random() < prob:
                individual.mutate(self.optimized_mutation)

    '''
    operacion: cruazamiento. Intercambio de razos fenotipicos entre individuos
    Cruce uniforme por atributo: cada hijo hereda la columna completa de cada atributo
    de uno u otro progenitor, por lo que las permutaciones se mantienen validas.
    limit = probabilidad de cruce; si no se cruza, los hijos son copias de los padres.
    '''
    def crossOver(self, progenitor_1, progenitor_2, limit):
        if random.random() >= limit:
            return [progenitor_1.copy(), progenitor_2.copy()]

        child_1, child_2 = list(progenitor_1.chromosome), list(progenitor_2.chromosome)
        for a in range(len(ATTRIBUTES)):
            if random.random() < 0.5:
                for h in range(N_HOUSES):
                    g = h * len(ATTRIBUTES) + a
                    child_1[g], child_2[g] = child_2[g], child_1[g]
        return [Phenotype(child_1), Phenotype(child_2)]


def main():
    parser = argparse.ArgumentParser(description='TP3 - Algoritmo genético: ¿quién usa Vim?')
    parser.add_argument('--poblacion', type=int, default=2000)
    parser.add_argument('--generaciones', type=int, default=1000)
    parser.add_argument('--estancamiento', type=int, default=150)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--init', choices=['random', 'heuristic'], default='random')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()

    start = time.time()

    rid = Riddle(seed=args.seed, verbose=not args.quiet, max_generations=args.generaciones,
                 stagnation_limit=args.estancamiento, init_method=args.init)
    fit, best = rid.solve(n_population=args.poblacion)

    print()
    print(best.table())
    if best.is_solution():
        print(f"\nRespuesta: el editor Vim lo usa el {best.who_uses('Vim')}.")
    else:
        print(f"\nNo se encontró solución completa (fitness {fit}/{MAX_SCORE}). Pistas incumplidas: "
              + ', '.join(str(c[0]) for c in best.failed_clues))

    end = time.time()
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Tiempo transcurrido {:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


if __name__ == '__main__':
    main()
