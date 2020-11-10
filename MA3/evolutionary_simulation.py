import numpy as np
import robot_evolutionary_simulation as sim
import random
from random import randint
from copy import deepcopy

# TODO enlever les float dans la Q table.


def init_population(n):
    Qs = []
    for _ in range(0, n):
        Qintermediate = []
        for _ in range(0, 6):
            Qintermediate.append(
                list(np.random.randint(low=-500, high=500, size=4)))
        Qs.append(Qintermediate)
    return Qs


def mutation(gene, n):
    ''' Alex
    gene: Q table
    n: number of mutation
    return Q table (with the mutation)
    '''
    copied_gene = deepcopy(gene)
    for _ in range(0, n):
        state = randint(0, 6 - 1)
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


def selection(p):
    ''' Cedric
    truncate 20 best element (sort by fitness)
    return Qs table with lenght 20 
    '''
    pass


def create_new_population():
    elitism_n = 5
    crossover()
    mutation()
    pass


def main():
    population_n = 200  # ?
    Qs = init_population(population_n)
    convergence = 10
    ttl = 5000  # counter

    population = []
    best_population_size = 20  # ?

    for q in Qs:
        fitness = sim.simulate(q, ttl)
        population.append((q, fitness))

    #! deepcopy?
    for _ in range(0, convergence):
        bests = selection(population, best_population_size)
        new_Qs = create_new_population(
            bests, population_n)  # ! return array(type: q)

        population = []
        for q in new_Qs:
            fitness = sim.simulate(q, ttl)
            population.append((q, fitness))
