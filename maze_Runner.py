import numpy as np
from PIL import Image,ImageDraw,ImageTk
from matplotlib import pyplot as plt
from pylab import savefig
import random

class Runner:
    def __init__(self,parent,acc_field,maze,uID,start_cell=(0,0),start_point_in_cell=np.zeros((2))):
        self.parent = parent
        self.frame_duration = .1
        self.uID = uID
        # 
        self.maze = maze
        self.maze_rows,self.maze_cols = maze.shape
        self.maze_row_width = 1/self.maze_rows
        self.maze_col_width = 1/self.maze_cols
        self.row_boundaries = [i*self.maze_row_width for i in range(self.maze_rows)]
        self.col_boundaries = [i*self.maze_col_width for i in range(self.maze_cols)]
        #
        start_x = start_point_in_cell[1] * self.maze_col_width
        start_x_in_cell = max(0, min(start_point_in_cell[1], 1))
        start_y = start_point_in_cell[0] * self.maze_row_width
        start_y_in_cell = max(0, min(start_point_in_cell[0], 1))
        self.location = np.array((start_y+start_y_in_cell,start_x+start_x_in_cell),np.float32)
        self.previous_location = None
        self.previous_previous_location = None
        self.previous_draw_location = None
        #
        self.velocity = np.array((0,0),np.float32) # x and y components of velocity
        #
        self.acceleration_field = acc_field # shape = [rows,cols,2xycomponents]
        self.acceleration = np.zeros((2),np.float32)
        self.get_acceleration()
        #
        self.runner_drawn = False
        self.velocity_average_weight = 5
        self.step_count = 0
        self.fitness = 0
        self.best_fitness = 0
        self.best_adjusted_fitness = 0
        self.best_location = None
        self.location_of_best_fitness = None
        self.recent_step_history = np.zeros((30,2))
        self.average_location_history = np.zeros((30,2))
        self.alive = True
        self.cause_of_death = 'unknown'
        self.color = "#"+"".join([random.choice('0123456789ABCDEF') for j in range(6)])
        #
        # self.make_vector_image()
    def move(self):
        self.previous_previous_location = np.array(self.previous_location)
        # d = vt + (1/2)*at^2
        self.previous_location = np.array(self.location)
        delta_xy = self.velocity*self.frame_duration+1/2*self.acceleration*self.frame_duration**2
        self.location += delta_xy
        self.check_state()
        if self.alive == False: return
        # # vf = sqrt(vi^2 + 2ad)
        # self.velocity = (self.velocity**2+2*self.acceleration*delta_xy)**.5
        self.get_velocity()
        # # acceleration determined by acceleration field
        # self.get_acceleration()
        self.recent_step_history[self.step_count%30]=self.location
        self.average_location_history[self.step_count%30]=np.mean(self.location,axis=0)
        if self.step_count > 30:
            # if np.mean(np.std(self.recent_step_history)) < .05:
            if np.mean(np.std(self.average_location_history,axis=0)) < .01:
                self.alive = False
                self.cause_of_death = 'not moving enough'
        self.step_count += 1
        self.get_fitness()
    def get_velocity(self):
        acc_rows=self.acceleration_field.shape[0]
        acc_cols=self.acceleration_field.shape[1]
        acc_row_width = 1/acc_rows
        acc_col_width = 1/acc_cols
        row = int(self.location[0]/acc_row_width)
        col = int(self.location[1]/acc_col_width)
        self.velocity = ((self.velocity_average_weight - 1) * self.velocity + self.acceleration_field[row,col]) / self.velocity_average_weight
    def get_acceleration(self):
        acc_rows=self.acceleration_field.shape[0]
        acc_cols=self.acceleration_field.shape[1]
        acc_row_width = 1/acc_rows
        acc_col_width = 1/acc_cols
        row = int(self.location[0]/acc_row_width)
        col = int(self.location[1]/acc_col_width)
        self.acceleration = self.acceleration_field[row,col]
    def get_maze_location(self,loc):
        y_coord,x_coord=loc
        row = int(y_coord // self.maze_row_width)
        col = int(x_coord // self.maze_col_width)
        return row,col
    def check_state(self):
        def get_new_endpoint(i,f,x=None,y=None):
            y1,x1=i
            y2,x2=f
            slope=(y2-y1)/(x2-x1)
            y_intercept=i[0]-slope*i[1]
            if x is not None:
                return list((slope*x+y_intercept,x))
            elif y is not None:
                return list((y,(y-y_intercept)/slope))
        def dist(i,f):
            y1,x1=i
            y2,x2=f
            delta_y = y2-y1
            delta_x = x2-x1
            return (delta_x**2+delta_y**2)**.5
        # --------------------------------------------- #
        if np.all(self.location == self.previous_previous_location): 
            self.alive = False
            self.cause_of_death = 'not moving'
            return
        if self.location[0] < 0 or self.location[1] < 0 or self.location[0] > 1 or self.location[1] > 1:
            self.alive = False
            self.cause_of_death = 'off screen'
            return
        col_locations = [i * self.maze_col_width for i in range(1,self.maze_cols)]
        row_locations = [i * self.maze_row_width for i in range(1,self.maze_rows)]
        crosses_col = False
        crosses_row = False
        #
        contained_row = contained_col = None
        for row_index,row in enumerate(row_locations):
            if self.location[0] < row and row < self.previous_location[0]:
                contained_row = row_index
                break
            if self.previous_location[0] < row and row < self.location[0]:
                contained_row = row_index
                break
        for col_index,col in enumerate(col_locations):
            if self.location[1] < col and col < self.previous_location[1]:
                contained_col = col_index
                break
            if self.previous_location[1] < col and col < self.location[1]:
                contained_col = col_index
                break
        #
        hit_row = hit_col = False
        if contained_row is not None:
            row_intersection_point = get_new_endpoint(self.previous_location,self.location,y=row)
            x=row_intersection_point[1]
            for interval in self.parent.maze_maker.row_intervals[row_index]:
                if (interval[0] < x and x < interval[1]) or (interval[0] > x and x > interval[1]):
                    self.alive = False
                    self.cause_of_death = 'hit row'
                    hit_row = True
                    break
        if contained_col is not None:
            col_intersection_point = get_new_endpoint(self.previous_location,self.location,x=col)
            y=col_intersection_point[0]
            for interval in self.parent.maze_maker.col_intervals[col_index]:
                if (interval[0] < y and y < interval[1]) or (interval[0] > y and y > interval[1]):
                    self.alive = False
                    self.cause_of_death = 'hit column'
                    hit_col = True
                    break
        #
        if hit_row and hit_col:
            dist_to_col = dist(self.previous_location,col_intersection_point)
            dist_to_row = dist(self.previous_location,row_intersection_point)
            if dist_to_col < dist_to_row:
                self.location = col_intersection_point
            else:
                self.location = row_intersection_point
        elif hit_row:
            self.location = row_intersection_point
        elif hit_col:
            self.location = col_intersection_point
    def draw_path(self):
        def dist(a,b):
            delta=b-a
            squared=delta**2
            _sum=np.sum(squared)
            dist=_sum**.5
            return dist
        if self.previous_draw_location is None:
            self.previous_draw_location = np.zeros((2,))#self.previous_location
        if dist(self.location,self.previous_draw_location)>.01:
            current_point = self.location
            previous_point = self.previous_draw_location
            previous_point = (previous_point[1]*self.parent.display.canvas_size[0],previous_point[0]*self.parent.display.canvas_size[1])
            current_point = (current_point[1]*self.parent.display.canvas_size[0],current_point[0]*self.parent.display.canvas_size[1])
            self.parent.display.the_canvas.create_line((previous_point[0],                     previous_point[1],
                                 current_point[0],current_point[1]),
                                 fill=self.color,width=2,tags='path')
            self.previous_draw_location=np.copy(self.location)
        ###
        # previous_point = np.copy(self.previous_location)
        # current_point = np.copy(self.location)
        # previous_point = (previous_point[1]*self.parent.display.canvas_size[0],previous_point[0]*self.parent.display.canvas_size[1])
        # current_point = (current_point[1]*self.parent.display.canvas_size[0],current_point[0]*self.parent.display.canvas_size[1])
        # self.parent.display.the_canvas.create_line((previous_point[0],                     previous_point[1],
                             # current_point[0],current_point[1]),
                             # fill=self.color,width=2,tags='path')
    def create_runner(self):
        current_point = self.location
        current_point = (current_point[1]*self.parent.display.canvas_size[0],
                         current_point[0]*self.parent.display.canvas_size[1])
        self.parent.display.the_canvas.create_oval((current_point[0],current_point[1],
                             current_point[0],current_point[1]),
                             fill=self.color,outline=self.color,width=6,
                             tags=('runner'+str(self.uID),'runner'))
        self.runner_drawn = True
    def move_runner(self):
        if not self.runner_drawn: self.create_runner()
        else:
            delta = self.location - self.previous_location
            delta = (delta[1]*self.parent.display.canvas_size[0],delta[0]*self.parent.display.canvas_size[1])
            self.parent.display.the_canvas.move('runner'+str(self.uID),delta[0],delta[1])
    def delete_runner(self):
        self.the_canvas.delete('runner'+str(self.uID))
        self.runner_drawn = False
    def make_vector_image(self):
        figsize_x = self.parent.display.canvas_size[0]/100
        figsize_y = self.parent.display.canvas_size[1]/100
        plt.figure(figsize=(figsize_x,
                            figsize_y),
                            dpi=100) # will ensure figure is correct size
        x_comp = self.acceleration_field[...,1]
        y_comp = -1*self.acceleration_field[...,0]
        plt.quiver(x_comp,y_comp,color='#004400')
        plt.tight_layout()
        plt.axis('off')
        name=str(self.uID)+'.png'
        plt.savefig('flowfields/'+name,transparent=True,bbox_inches='tight',pad_inches=0.0)
        vec_im = Image.open('flowfields/'+name)
        w,h = vec_im.size
        crop_bounds = (95*figsize_x/13,27*figsize_y/7.2,
                      (w-30)*figsize_x/13,(h-30)*figsize_y/7.2)
        vec_im.crop(crop_bounds).save('flowfields/'+name)
    def get_fitness(self):
        if self.location is None: 
            return
        def get_cell_exit_point(cell,path,steps_along_path):
            if steps_along_path == len(path) - 1:
                return (1,1)
            else:
                next_cell = path[path.index(cell)+1]
                cell_width = 1/self.maze.shape[1]
                cell_height= 1/self.maze.shape[0]
                bottom_right_coordinates = ((cell[0]+1)*cell_height,(cell[1]+1)*cell_width)
                if next_cell[0]>cell[0]: 
                    exit = (bottom_right_coordinates[0],bottom_right_coordinates[1]-cell_width/2)
                elif next_cell[1]>cell[1]:
                    exit = (bottom_right_coordinates[0]-cell_height/2,bottom_right_coordinates[1])
                elif next_cell[0]<cell[0]: 
                    exit = (bottom_right_coordinates[0]-cell_height,bottom_right_coordinates[1]-cell_width/2)
                elif next_cell[1]<cell[1]: 
                    exit = (bottom_right_coordinates[0]-cell_height/2,bottom_right_coordinates[1]-cell_width)
                return exit
        def get_dist(a,b):
            delta_x = b[1]-a[1]
            delta_y = b[0]-a[0]
            return (delta_x**2+delta_y**2)**.5
        path = self.parent.maze_maker.solution
        cell = self.get_maze_location(self.location) # using previous location because current location will go through walls
        try: dist_from_path,closest_path_cell = self.parent.maze_maker.distance_to_path(cell)
        except:
            print("dist_from_path: " + str(dist_from_path))
            print("closest_path_cell: " + str(closest_path_cell))
            1/0
        score_per_cell = 1/len(path)
        cell_width = 1/self.maze.shape[1]
        cell_height= 1/self.maze.shape[0]
        cell_diagonal = (cell_width**2+cell_height**2)**.5
        if dist_from_path == 0:
            number_of_steps_along_path = path.index(cell)
            score_for_cell = (number_of_steps_along_path + 1) * score_per_cell
            cell_exit_point = get_cell_exit_point(cell,path,number_of_steps_along_path)
            score_for_position_in_cell = -1 * get_dist(self.previous_location,cell_exit_point)/cell_diagonal*score_per_cell
            score = (score_for_cell + score_for_position_in_cell)
        else:
            number_of_steps_along_path = path.index(closest_path_cell)
            score_for_cell = number_of_steps_along_path * score_per_cell
            penalty_for_leaving_path = dist_from_path * score_per_cell
            score = score_for_cell + penalty_for_leaving_path
            score = min(0,score)
        if self.step_count in self.parent.step_penalties:
            adjusted_score = score * self.parent.step_penalties[self.step_count]
        else:
            self.parent.step_penalties[self.step_count] = .998**self.step_count
            adjusted_score = score * self.parent.step_penalties[self.step_count]
        if self.best_fitness < score:
            self.best_fitness = score
            self.best_location = np.array(self.location)
        if self.best_adjusted_fitness < adjusted_score:
            self.best_adjusted_fitness = adjusted_score
            self.location_of_best_fitness = np.array(self.location)
