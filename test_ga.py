import random
import unittest

from ga import CODES, MAX_SCORE, N_HOUSES, ATTRIBUTES, Phenotype, Riddle

SOLUCION = [
    ['blue',   'Developer',     'C#',         'Neo4j',     'Sublime Text'],
    ['yellow', 'Analyst',       'C++',        'Cassandra', 'Atom'],
    ['red',    'Mathematician', 'Java',       'Redis',     'Notepad++'],
    ['white',  'Hacker',        'Python',     'HBase',     'Vim'],
    ['green',  'Engineer',      'JavaScript', 'MongoDB',   'Brackets'],
]


def es_valido(ind):
    ''' cada atributo es una permutacion de los 5 codigos validos '''
    return all(sorted(ind.chromosome[h * 5 + a] for h in range(N_HOUSES)) == CODES
               for a in range(len(ATTRIBUTES)))


class TestPhenotype(unittest.TestCase):

    def setUp(self):
        random.seed(0)

    def test_encode_decode(self):
        self.assertEqual(Phenotype(Phenotype.encode(SOLUCION)).decode(), SOLUCION)

    def test_solucion_conocida_tiene_fitness_maximo(self):
        ind = Phenotype(Phenotype.encode(SOLUCION))
        self.assertEqual(ind.score, MAX_SCORE)
        self.assertTrue(ind.is_solution())
        self.assertEqual(ind.who_uses('Vim'), 'Hacker')

    def test_romper_una_pista_baja_el_fitness(self):
        roto = [row[:] for row in SOLUCION]
        roto[0][1], roto[1][1] = roto[1][1], roto[0][1]   # Developer deja la casa 1
        ind = Phenotype(Phenotype.encode(roto))
        self.assertLess(ind.score, MAX_SCORE)
        self.assertIn(10, [c[0] for c in ind.failed_clues])

    def test_pista_6_es_inmediatamente_a_la_derecha(self):
        roto = [row[:] for row in SOLUCION]
        roto[3][0], roto[2][0] = roto[2][0], roto[3][0]   # blanca en casa 3, verde en casa 5
        ind = Phenotype(Phenotype.encode(roto))
        self.assertIn(6, [c[0] for c in ind.failed_clues])

    def test_cromosoma_invalido_es_penalizado(self):
        cromosoma = Phenotype.encode(SOLUCION)
        cromosoma[0] = '000'                      # codigo inexistente
        cromosoma[5 + 1] = cromosoma[1]           # profesion repetida
        ind = Phenotype(cromosoma)
        self.assertEqual(ind.invalid_genes(), 2)  # 1 codigo inexistente + 1 repetido
        self.assertLess(ind.score, MAX_SCORE - 2)

    def test_generacion_produce_individuos_validos(self):
        for _ in range(200):
            self.assertTrue(es_valido(Phenotype()))
            self.assertTrue(es_valido(Phenotype.heuristic()))

    def test_heuristica_fija_pistas_de_posicion(self):
        for _ in range(50):
            casas = Phenotype.heuristic().decode()
            self.assertEqual(casas[0][1], 'Developer')
            self.assertEqual(casas[0][0], 'blue')
            self.assertEqual(casas[2][4], 'Notepad++')

    def test_mutacion_preserva_validez(self):
        ind = Phenotype()
        for _ in range(500):
            ind.mutate(optimized=random.random() < 0.5)
            self.assertTrue(es_valido(ind))


class TestRiddle(unittest.TestCase):

    def test_cruce_preserva_validez(self):
        random.seed(0)
        rid = Riddle(verbose=False)
        for _ in range(500):
            for hijo in rid.crossOver(Phenotype(), Phenotype(), 1.0):
                self.assertTrue(es_valido(hijo))

    def test_cruce_hereda_columnas_de_los_padres(self):
        random.seed(0)
        p1, p2 = Phenotype(), Phenotype()
        for hijo in Riddle(verbose=False).crossOver(p1, p2, 1.0):
            for a in range(len(ATTRIBUTES)):
                col = [hijo.chromosome[h * 5 + a] for h in range(N_HOUSES)]
                self.assertIn(col, ([p1.chromosome[h * 5 + a] for h in range(N_HOUSES)],
                                    [p2.chromosome[h * 5 + a] for h in range(N_HOUSES)]))

    def test_seleccion_por_torneo_devuelve_el_mejor_del_torneo(self):
        random.seed(0)
        rid = Riddle(verbose=False, tournament_size=3)
        rid.generate(50)
        for _ in range(100):
            elegido = rid.select()
            self.assertGreaterEqual(elegido.score, min(x.score for x in rid.population))

    def test_converge_con_semilla_fija(self):
        rid = Riddle(seed=1, verbose=False)
        fit, best = rid.solve(n_population=1000)
        self.assertEqual(fit, MAX_SCORE)
        self.assertTrue(es_valido(best))

    def test_corte_por_maximo_de_generaciones(self):
        rid = Riddle(seed=3, verbose=False, max_generations=2)
        rid.solve(n_population=10)
        self.assertLessEqual(rid.generation, 2)
        self.assertIn(rid.stop_reason.split(' ')[0], ('máximo', 'solución'))

    def test_corte_por_estancamiento(self):
        rid = Riddle(seed=3, verbose=False, stagnation_limit=1, mutation_prob=0, crossover_prob=0,
                     immigrant_rate=0)
        rid.solve(n_population=10)
        self.assertTrue(rid.stop_reason.startswith('estancamiento') or rid.stop_reason.startswith('solución'))


if __name__ == '__main__':
    unittest.main()
