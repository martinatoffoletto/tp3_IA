'''
Experimentos del TP3.

1. Enumera por fuerza bruta (con poda) todas las soluciones exactas del acertijo,
   para tener una referencia contra la cual validar al algoritmo genetico.
2. Corre el AG con varias semillas y con cada metodo de generacion de individuos,
   y resume tasa de exito, generaciones, tiempo y quien usa Vim en cada corrida.
'''

import argparse
import time
from collections import Counter
from itertools import permutations

from ga import Phenotype, Riddle, colors, prefession, languaje, database, editor


def soluciones_exactas():
    ''' todas las asignaciones que cumplen las 15 pistas (pista 6 = inmediatamente a la derecha) '''
    C, P, L, D, E = (list(d.values()) for d in (colors, prefession, languaje, database, editor))
    sols = []
    for c in permutations(C):
        if c.index('green') != c.index('white') + 1:
            continue
        for p in permutations(P):
            if p[0] != 'Developer' or p[c.index('blue')] != 'Developer' or p[c.index('red')] != 'Mathematician':
                continue
            for e in permutations(E):
                if e[2] != 'Notepad++' or e[c.index('green')] != 'Brackets' or e[p.index('Analyst')] != 'Atom':
                    continue
                for d in permutations(D):
                    if d[c.index('yellow')] != 'Cassandra' or p[d.index('MongoDB')] != 'Engineer' \
                            or e[d.index('Neo4j')] != 'Sublime Text':
                        continue
                    for l in permutations(L):
                        if l[p.index('Hacker')] != 'Python' or l[d.index('Redis')] != 'Java':
                            continue
                        if abs(d.index('HBase') - l.index('JavaScript')) != 1 or abs(d.index('Cassandra') - l.index('C#')) != 1:
                            continue
                        sols.append([[c[h], p[h], l[h], d[h], e[h]] for h in range(5)])
    return sols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--corridas', type=int, default=30)
    parser.add_argument('--poblacion', type=int, default=1000)
    args = parser.parse_args()

    exactas = soluciones_exactas()
    vim_exactas = Counter(Phenotype(Phenotype.encode(s)).who_uses('Vim') for s in exactas)
    print(f"Soluciones exactas del acertijo: {len(exactas)}")
    print(f"Quién usa Vim en ellas: {dict(vim_exactas)}\n")
    claves_exactas = {tuple(Phenotype.encode(s)) for s in exactas}

    for metodo in ['random', 'heuristic']:
        exitos, generaciones, tiempos, vim, distintas = 0, [], [], Counter(), set()
        motivos = Counter()
        for seed in range(args.corridas):
            t0 = time.time()
            rid = Riddle(seed=seed, verbose=False, init_method=metodo)
            fit, best = rid.solve(n_population=args.poblacion)
            tiempos.append(time.time() - t0)
            motivos[rid.stop_reason] += 1
            if best.is_solution():
                assert tuple(best.chromosome) in claves_exactas, 'el AG devolvió una solución que no es exacta'
                exitos += 1
                generaciones.append(rid.generation)
                vim[best.who_uses('Vim')] += 1
                distintas.add(tuple(best.chromosome))

        print(f"== Generación '{metodo}' | población {args.poblacion} | {args.corridas} corridas ==")
        print(f"  Éxito: {exitos}/{args.corridas}")
        if generaciones:
            print(f"  Generaciones hasta la solución: prom {sum(generaciones)/len(generaciones):.1f}, "
                  f"mín {min(generaciones)}, máx {max(generaciones)}")
        print(f"  Tiempo promedio por corrida: {sum(tiempos)/len(tiempos):.2f}s")
        print(f"  Motivos de corte: {dict(motivos)}")
        print(f"  Quién usa Vim: {dict(vim)}")
        print(f"  Soluciones distintas encontradas: {len(distintas)} de {len(exactas)}\n")


if __name__ == '__main__':
    main()
