import numpy as np
import math
import random

np.set_printoptions(suppress=True, precision=2, linewidth=140)

class GeneticAlgorithm:
    def __init__(self,parent,field_size,population):
        self.parent = parent
        self.field_size = list(field_size)
        self.field_size_y,self.field_size_x = self.field_size
        self.rows,self.columns = field_size
        self.population = population
        self.number_of_elites = population//10
        self.number_of_elites = max(self.number_of_elites,5)
        self.number_of_protected_elites = self.number_of_elites // 2
        self.number_of_protected_elites = max(self.number_of_protected_elites,1)
        if population == 1:
            self.number_of_elites = self.number_of_protected_elites = 0
        self.first_vector_positive = True
    def populate(self):
        # self.vector_field.shape = [population,rows,columns,thexycomponents]
        # self.vector_field = np.random.normal(0,.15,[self.population]+self.field_size+[2])
        self.vector_field = np.zeros([self.population]+self.field_size+[2])
        for i in range(self.population):
            y_components = self.generate_perlin_noise_2d((self.field_size_y+4,self.field_size_x+4),(9,9))
            self.vector_field[i,:,:,0] = y_components[2:self.field_size_y+2,2:self.field_size_x+2]
            x_components = -1*self.generate_perlin_noise_2d((self.field_size_y+4,self.field_size_x+4),(9,9))
            self.vector_field[i,:,:,1] = x_components[2:self.field_size_y+2,2:self.field_size_x+2]
        if self.first_vector_positive:
            self.vector_field[:,0,0,:] = np.abs(self.vector_field[:,0,0,:])
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
    def one_parent_mutate(self):
        # get mutation rate per citizen based on formula. Mutation rates will range evenly across citizens from 0 to 1/3
        # mutation rate to be reshaped to match dimensions of acceleration field
        mutation_rate = np.asarray([i/(10*self.population) for i in range(self.population)])
        mutation_rate = mutation_rate.reshape(self.population,1,1)
        mutation_rate = np.repeat(mutation_rate,self.field_size[0],1)
        mutation_rate = np.repeat(mutation_rate,self.field_size[1],2)
        # get uniformly random numbers between 0 and 1 to determine where node mutations will occur
        mutation_determination = np.random.random(([self.population]+self.field_size))
        # mutate accordingly
        mask = np.asarray([mutation_determination < mutation_rate])
        mask = mask.reshape([self.population]+self.field_size+[1])
        mask = np.repeat(mask,2,3)
        self.vector_field[mask]=np.random.normal(0,.15,[self.population]+self.field_size+[2])[mask]
    def crossover(self,score_set):
        if len(score_set)==1:
            self.one_parent_mutate()
            return # good luck with that
        def get_nth_largest(lst,n,excluded=[]):
            ar=np.asarray(lst)
            value = np.partition(ar.flatten(),-n)[-n]
            #
            value_index = None
            tries=0
            while value_index is None:
                i_try = [i for i, i_value in enumerate(lst) if i_value == value][0]
                if i_try in excluded: tries += 1
                else: value_index = i_try
            return value_index
        score_set_ar = np.asarray(score_set)
        lowest_elite_score = get_nth_largest(score_set,self.number_of_elites)
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
        offspring_fields = self.vector_field[parent_a_choices,...]
        _offspring_fields= self.vector_field[parent_b_choices,...]
        # # cross some parents by average instead
        # average_method = np.random.randint(2,size=([self.population]+self.field_size),dtype=bool)
        # substitute random nodes from parent 2
        offspring_fields[parent_gene_determinations,:] = _offspring_fields[parent_gene_determinations,:]
        # get mutation rate per citizen based on formula. Mutation rates will range evenly across citizens from 0 to 1/3
        # mutation rate to be reshaped to match dimensions of acceleration field
        mutation_rate = np.asarray([i/(10*self.population) for i in range(self.population)])
        mutation_rate = mutation_rate.reshape(self.population,1,1)
        mutation_rate = np.repeat(mutation_rate,self.field_size[0],1)
        mutation_rate = np.repeat(mutation_rate,self.field_size[1],2)
        # get uniformly random numbers between 0 and 1 to determine where node mutations will occur
        mutation_determination = np.random.random(([self.population]+self.field_size))
        # mutate accordingly
        mask = np.asarray([mutation_determination < mutation_rate])
        mask = mask.reshape([self.population]+self.field_size+[1])
        mask = np.repeat(mask,2,3)
        offspring_fields[mask]=np.random.normal(0,.15,[self.population]+self.field_size+[2])[mask]
        # # save protected elites
        protected_elites = np.zeros([self.number_of_protected_elites]+self.field_size+[2])
        elite_indices=[]
        for i in range(self.number_of_protected_elites):
            new_elite_index = get_nth_largest(score_set_ar,i+1,elite_indices)
            elite_indices.append(new_elite_index)
        protected_elites = self.vector_field[elite_indices,...]
        offspring_fields[elite_indices,...] = protected_elites
        # replace the vector field
        self.vector_field = offspring_fields