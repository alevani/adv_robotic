import numpy as np
import robot_evolutionary_simulation as sim
import random
from random import randint
from copy import deepcopy

# TODO enlever les float dans la Q table.


def init_population(n):
    Qs = []
    for _ in range(0, n-1):
        Qintermediate = []
        for _ in range(0, 5):
            Qintermediate.append(
                list(np.random.randint(low=-500, high=500, size=4)))
        Qs.append((Qintermediate, 0))
    return Qs


def mutation(gene, n):
    #! can mute the same more than once
    copied_gene = deepcopy(gene)
    for _ in range(0, n):
        state = randint(0, 5 - 1)
        action = randint(0, 4 - 1)

        chromosome = copied_gene[state][action]

        random_index = randint(0, 8 - 1)
        chromosome = chromosome ^ (1 << random_index)

        if chromosome > 500:
            chromosome = 500
        elif chromosome < -500:
            chromosome = -500

        copied_gene[state][action] = chromosome

    return copied_gene


def crossover(gene1, gene2):
    ''' Joe
    gene1: Q table
    gene2: Q table
    ! see in lecture how crossover works
    return: 2 Q table
    '''
    # return gene
    pass


def selection(pop, n):
    pop.sort(key=lambda pop: pop[1], reverse=False)
    pop = [p[0] for p in pop]
    return pop[:n]  # ! return without fitness


def create_new_population(best, population_n):
    # Select 1/4 of the population which are not going to evolve or mutate
    elitism_n = int(0.25 * len(best))
    elected_elitists = [best.pop(i) for i in range(elitism_n)]

    new_population = []

    #! < or <=?
    #! when crossover, maybe do 50/50
    while len(new_population) < population_n - elitism_n:
        # crossover()
        n_gene_to_mutate = randint(0, 10)  # arbitrary
        g_to_mutate = best[randint(0, len(best)-1)]
        new_population.append(mutation(g_to_mutate, n_gene_to_mutate))

    return elected_elitists + new_population


def main():
    population_n = 10  # ?
    population = init_population(population_n)

    convergence = 100
    ttl = 5000  # counter

    best_population_size = int(0.5 * population_n)  # ?

    #! deepcopy?
    #! maybe keep fitness when selection to make some statistics
    for i in range(0, convergence):
        print("Epoch: ", i)
        bests = selection(population, best_population_size)

        new_Qs = create_new_population(
            bests, population_n)  # ! return array(type: q)

        population = []
        for q in new_Qs:
            print("Start new simulation")
            fitness = sim.simulate(q, ttl)
            population.append((q, fitness))
        print(selection(population, 1))


main()
