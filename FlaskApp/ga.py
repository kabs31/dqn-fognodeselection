import numpy as np

class FogGeneticAlgorithm:
    
    def __init__(self, fog_nodes, edge_node, population_size=20, num_generations=1000, mutation_rate=0.1, crossover_rate=0.8):
        self.fog_nodes = fog_nodes
        self.edge_node = edge_node
        self.population_size = population_size
        self.num_generations = num_generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.chromosome_length = len(fog_nodes)
        self.population = np.random.randint(2, size=(self.population_size, self.chromosome_length))
        mask = ~np.all(self.population == 0, axis=1)
        self.population = self.population[mask]
    
    def calculate_latency(self, edge_node, fog_nodes, chromosome):
        connected_fog_nodes = [fog_nodes[i] for i in range(len(chromosome)) if chromosome[i] == 1]
        processing_time = sum([edge_node['workload'] / fog_node['capacity'] * 100 for fog_node in connected_fog_nodes])
        distance = sum([np.linalg.norm(fog_node['location'] - edge_node['location']) for fog_node in connected_fog_nodes])
        latency = distance + processing_time
        return -latency
    
    def select_parents(self, fitness_scores):
        #roulette wheel selection
        sum_fitness = sum(fitness_scores)
        relative_fitness = [fitness / sum_fitness for fitness in fitness_scores]
        parent1_index = np.argmax(relative_fitness)
        parent2_index = np.argmin(relative_fitness)
        parent1 = self.population[parent1_index]
        parent2 = self.population[parent2_index]
        return parent1, parent2
    
    def generate_offspring(self, parent1, parent2):
        #single point crossover
        if(np.random.rand()<self.crossover_rate):
            crossover_point = np.random.randint(self.chromosome_length)
            child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
            child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
        else:
            child1=parent1
            child2=parent2

        for j in range(self.chromosome_length):
            if np.random.rand() < self.mutation_rate:
                child1[j] = 1 - child1[j]
                child2[j] = 1 - child2[j]

        return child1, child2
    
    def run(self):
        for generation in range(self.num_generations):
            # Calculate the fitness for each chromosome in the population
            fitness_scores = [self.calculate_latency(self.edge_node, self.fog_nodes, chromosome) for chromosome in self.population]

            # Create new offspring using crossover and mutation
            offspring = []
            for i in range(int(self.population_size/2)):
                parent1, parent2 = self.select_parents(fitness_scores)
                child1, child2 = self.generate_offspring(parent1, parent2)
                offspring.append(child1)
                offspring.append(child2)

            # Replace the old population with the new offspring
            self.population = np.array(offspring)

            # Remove any all-zero chromosomes
            mask = ~np.all(self.population == 0, axis=1)
            self.population = self.population[mask]

        # Select the best solution from the final population
        fitness_scores = [self.calculate_latency(self.edge_node, self.fog_nodes, chromosome) for chromosome in self.population]
        best_index = np.argmax(fitness_scores)
        best_chromosome = self.population[best_index]
        best_latency = fitness_scores[best_index]
        for i in range(len(best_chromosome)):
            if best_chromosome[i] == 1:
                return self.fog_nodes[i]['id']
        



