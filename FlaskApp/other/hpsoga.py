import numpy as np
import random
# Define system parameters
Np = 50  # population size
Ng = 100  # number of generations
rc = 0.8  # crossover ratio
rm = 0.2  # mutation ratio
I = 0.5  # inertia
C = 2.0  # cognitive parameter
S = 2.0  # social parameter

def optimizer(population,Np=50,Ng=100,rc=0.8,rm=0.2,I=0.5,C=2.0,S=2.0):
    for i in range(Ng):
        if(i==0):
            fitness = np.zeros(Np)
            for i in range(Np):
                fitness[i] = knapsack_problem(population[i])
            parents = selection(population)
        elif(i==Ng-1):
            return pso_childrens,gbest
        else:
            fitness = np.zeros(Np)
            for i in range(Np):
                fitness[i] = knapsack_problem(pso_childrens[i])
            parents = selection(pso_childrens,fitness)

        childrens = crossover(parents,rc)

        mutated_childrens = mutation(childrens,rm)
        mutated_childrens = np.array(mutated_childrens)


        pso_childrens,gbest =  pso_growth(mutated_childrens,mutated_childrens[int(random.random()*10)],ub,lb,fitness)


# Define the Knapsack problem as a function
#this is a objective or fitness function
def knapsack_problem(x):
    weights = np.array([1, 3, 2, 5, 4])
    values = np.array([6, 12, 10, 16, 14])
    capacity = 10
    total_weight = np.dot(weights, x)
    total_value = np.dot(values, x)
    # Penalty if the total weight exceeds the capacity
    if total_weight > capacity:
        total_value -= (total_weight - capacity) * 1000
    return -total_value  # Negative since we want to maximize the value

def selection(population,fitness):
    
    # Sort the population by fitness (in descending order)
    sorted_pop = population[np.argsort(-fitness)]
    # Choose the top 50% of the population to become parents
    num_parents = int(0.5 * Np)
    parents = sorted_pop[:num_parents]
    return parents

def crossover(parents, rc):
    children = []
    for i in range(0, len(parents)-1, 2):
        if random.random() < rc:
            child1, child2 = create_children(parents[i], parents[i+1])
            children.append(child1)
            children.append(child2)
        else:
            children.append(parents[i])
            children.append(parents[i+1])
    return children

def create_children(parent1, parent2):
    child1 = np.zeros_like(parent1)
    child2 = np.zeros_like(parent2)
    # Choose a random crossover point
    cxpoint = np.random.randint(1, len(parent1)-1)
    # Combine parent genes up to crossover point
    child1[:cxpoint] = parent1[:cxpoint]
    child2[:cxpoint] = parent2[:cxpoint]
    # Combine parent genes after crossover point
    child1[cxpoint:] = parent2[cxpoint:]
    child2[cxpoint:] = parent1[cxpoint:]
    return child1, child2

def mutation(children, rm):
    for i in range(len(children)):
        for j in range(len(children[i])):
            if random.random() < rm:
                # Cast the decision variable to an integer and flip a random bit
                x = int(children[i][j])
                x = x ^ (1 << random.randint(0, len(bin(x)[2:])-1))
                children[i][j] = float(x)
    return children

import numpy as np

def pso_growth(mutated_childrens,gbest,UB,LB,fitness):
    Np, D = mutated_childrens.shape
    v = np.zeros((Np, D)) # Velocity
    pbest = mutated_childrens.copy() # Initialize personal best
    
    
    # Update personal best for each child
    for i in range(Np):
        if fitness[i] > knapsack_problem(pbest[i]):
            pbest[i] = mutated_childrens[i]
    
    # Update global best
    if fitness.max() > knapsack_problem(gbest):
        if len(mutated_childrens) > 0:
            gbest = mutated_childrens[fitness.argmax()]
        else:
            gbest = np.zeros(D) # create a dummy array of zeros

    
    # Update velocity and position for each child
    for i in range(Np):
        r1 = np.random.rand(D)
        r2 = np.random.rand(D)
        v[i] = I * v[i] + C * r1 * (pbest[i] - mutated_childrens[i]) + S * r2 * (gbest - mutated_childrens[i])
        mutated_childrens[i] += v[i]
        # Make sure the new position is within the search space
        mutated_childrens[i] = np.maximum(mutated_childrens[i], LB)
        mutated_childrens[i] = np.minimum(mutated_childrens[i], UB)
    
    return mutated_childrens, gbest


# Define the lower and upper bounds for the decision variables
lb = np.zeros(5)
ub = np.ones(5)

# Generate the initial population
pop = np.random.randint(2, size=(Np, 5))
pop = np.where(pop == 0, lb, ub)

childrens,gbest = optimizer(pop)

print()
print(gbest)
