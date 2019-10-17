import numpy as np
import math

class GeneticAlgorithm:
    def __init__(self,parent,field_size,population):
        self.parent = parent
        self.field_size = list(field_size)
        self.rows,self.columns = field_size
        self.population = 100
        self.number_of_elites = population//10
        self.first_vector_positive = True
    def populate(self):
        # self.acceleration_field.shape = [population,rows,columns,thexycomponents]
        # self.acceleration_field = np.random.normal(0,.15,[self.population]+self.field_size+[2])
        self.acceleration_field = np.zeros([self.population]+self.field_size+[2])
        for i in range(self.population):
            y_components = self.generate_perlin_noise_2d((36,36),(6,6))
            self.acceleration_field[i,:,:,0] = y_components[2:34,2:34]
            x_components = -1*self.generate_perlin_noise_2d((36,36),(6,6))
            self.acceleration_field[i,:,:,1] = x_components[2:34,2:34]
        if self.first_vector_positive:
            self.acceleration_field[:,0,0,:] = np.abs(self.acceleration_field[:,0,0,:])
        self.fitnesses = np.zeros([self.population])
    def generate_perlin_noise_2d(self,shape, res): # taken from https://pvigier.github.io/2018/06/13/perlin-noise-numpy.html
        def f(t):
            return 6*t**5 - 15*t**4 + 10*t**3
        
        delta = (res[0] / shape[0], res[1] / shape[1])
        d = (shape[0] // res[0], shape[1] // res[1])
        grid = np.mgrid[0:res[0]:delta[0],0:res[1]:delta[1]].transpose(1, 2, 0) % 1
        # Gradients
        angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
        gradients = np.dstack((np.cos(angles), np.sin(angles)))
        g00 = gradients[0:-1,0:-1].repeat(d[0], 0).repeat(d[1], 1)
        g10 = gradients[1:,0:-1].repeat(d[0], 0).repeat(d[1], 1)
        g01 = gradients[0:-1,1:].repeat(d[0], 0).repeat(d[1], 1)
        g11 = gradients[1:,1:].repeat(d[0], 0).repeat(d[1], 1)
        # Ramps
        n00 = np.sum(grid * g00, 2)
        n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1])) * g10, 2)
        n01 = np.sum(np.dstack((grid[:,:,0], grid[:,:,1]-1)) * g01, 2)
        n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)
        # Interpolation
        t = f(grid)
        n0 = n00*(1-t[:,:,0]) + t[:,:,0]*n10
        n1 = n01*(1-t[:,:,0]) + t[:,:,0]*n11
        return np.sqrt(2)*((1-t[:,:,1])*n0 + t[:,:,1]*n1)
    def crossover(self,score_set):
        def get_nth_largest(ar,n):
            return np.partition(ar.flatten(),-n)[-n]
        score_set_ar = np.asarray(score_set)
        lowest_elite_score = get_nth_largest(score_set_ar,self.number_of_elites)
        score_set_ar[score_set_ar < lowest_elite_score] = 0
        # decide the parents
        score_indices = np.arange(len(score_set)).reshape(len(score_set),1)
        scores_table = np.concatenate((score_indices, score_set_ar.reshape(len(score_set),1)),axis=1)
        probabilities = scores_table[:,1]/scores_table[:,1].sum()
        parent_a_choices = np.random.choice(list(scores_table[:,0]),self.population,p=probabilities).reshape(self.population)
        parent_a_choices = np.asarray(parent_a_choices,dtype=np.int32)
        parent_b_choices = np.zeros((parent_a_choices.shape),dtype=np.int32)
        for row in range(self.population):
            scores_table_copy = np.copy(scores_table)
            scores_table_copy = np.delete(scores_table_copy,parent_a_choices[row],axis=0)
            probabilities = scores_table_copy[:,1]/scores_table_copy[:,1].sum()
            parent_b_choices[row] = np.random.choice(list(scores_table_copy[:,0]),1,p=probabilities)
        if np.any(parent_a_choices==parent_b_choices): 1/0
        # # get random boolean values for every node to determine offspring genotype
        parent_gene_determinations = np.random.randint(2,size=([self.population]+self.field_size),dtype=bool)
        # copy parents
        offspring_fields = self.acceleration_field[parent_a_choices,...]
        _offspring_fields= self.acceleration_field[parent_b_choices,...]
        # substitute random nodes from parent 2
        offspring_fields[parent_gene_determinations,:] = _offspring_fields[parent_gene_determinations,:]
        # get mutation rate per citizen based on formula. Mutation rates will range evenly from 0 to 1/3
        mutation_rate = np.asarray([i/(3*self.population) for i in range(self.population)])
        # get uniformly random numbers between 0 and 1 to determine where node mutations will occur
        mutation_determination = np.random.random(([self.population]+self.field_size))
        mutation_determination = mutation_determination.reshape([self.population]+self.field_size+[1])
        mutation_determination = np.repeat(mutation_determination,2,3)
        # mutate accordingly
        print("mutation_rate: " + str(mutation_rate))
        mask = np.asarray([mutation_determination < mutation_rate])
        mask = mask.reshape([self.population]+self.field_size+[2])
        offspring_fields[mask]=np.random.normal(0,.25,[self.population]+self.field_size+[2])[mask]