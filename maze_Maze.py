import numpy as np
from PIL import Image,ImageDraw
import random

class Mazer:
    def __init__(self,parent):
        self.parent=parent
    def make_maze(self,size,start_cell=(0,0)):
        # self.maze key
        # 0=all open
        # 1=closed on right 
        # 2=closed on bottom 
        # 3=closed on bottom and right
        def find_unvisited_neighbors(cell,visited_cells):
            row,column=cell
            rows,columns=visited_cells.shape
            unvisited_neighbors = []
            if row > 0:
                neighbor_cell = row-1,column
                if visited_cells[neighbor_cell] == 0: unvisited_neighbors.append(tuple((neighbor_cell)))
            if row < rows-1:
                neighbor_cell = row+1,column
                if visited_cells[neighbor_cell] == 0: unvisited_neighbors.append(tuple((neighbor_cell)))
            if column > 0:
                neighbor_cell = row,column-1
                if visited_cells[neighbor_cell] == 0: unvisited_neighbors.append(tuple((neighbor_cell)))
            if column < columns-1:
                neighbor_cell = row,column+1
                if visited_cells[neighbor_cell] == 0: unvisited_neighbors.append(tuple((neighbor_cell)))
            return tuple(unvisited_neighbors)
        def relative_position(curr,next):
            y1,x1=curr
            y2,x2=next
            if (x2 - x1) == 1 and y1 == y2: return 'right'
            elif (x2 - x1) == -1 and y1 == y2: return 'left'
            elif x1 == x2 and (y2 - y1) == 1: return 'down'
            elif x1 == x2 and (y2 - y1) == -1: return 'up'
            else: return 'not adjacent'
        def update_maze(cell,side):
            maze_val = self.maze[(cell)]
            new_maze_val = None
            if side=='right':
                if   maze_val == 1: new_maze_val = 0
                elif maze_val == 3: new_maze_val = 2
            elif side=='down':
                if   maze_val == 2: new_maze_val = 0
                elif maze_val == 3: new_maze_val = 1
            return new_maze_val
        # ----------------------------- #
        self.size = size
        self.maze=3*np.ones(self.size)
        final_solution_found = False
        visited_cells = np.zeros(self.size)
        current_cell = start_cell
        self.solution = [current_cell]
        visited_cells_with_unvisited_neighbors = []
        while 0 in visited_cells:
            visited_cells[current_cell] = 1
            unvisited_neighbors = find_unvisited_neighbors(current_cell,visited_cells)
            if len(unvisited_neighbors) > 0:
                next_cell = random.choice(unvisited_neighbors)
                direction_went = relative_position(current_cell,next_cell)
                if direction_went in ('right','down'):
                    self.maze[current_cell] = update_maze(current_cell,direction_went)
                else:
                    if direction_went == 'left':
                        cell_to_change = current_cell[0],current_cell[1]-1
                        self.maze[cell_to_change] = update_maze(cell_to_change,'right')
                    elif direction_went == 'up':
                        cell_to_change = current_cell[0]-1,current_cell[1]
                        self.maze[cell_to_change] = update_maze(cell_to_change,'down')
                if len(unvisited_neighbors) > 1: 
                    visited_cells_with_unvisited_neighbors.append(current_cell)
                current_cell = next_cell
                if not final_solution_found: 
                    self.solution.append(current_cell)
            elif len(visited_cells_with_unvisited_neighbors) > 0:
                current_cell = visited_cells_with_unvisited_neighbors.pop(len(visited_cells_with_unvisited_neighbors)-1)
                if not final_solution_found: 
                    self.solution = self.solution[:self.solution.index(current_cell)+1]
            if (not final_solution_found) and (current_cell == (self.size[0]-1,self.size[1]-1)):
                final_solution_found = True
        self.get_maze_equations()
    def get_maze_equations(self):
        rows,cols = self.size
        row_width = 1/rows
        col_width = 1/cols
        row_coords = [i*row_width for i in range(1,rows)]
        col_coords = [i*col_width for i in range(1,cols)]
        self.col_intervals = {}
        self.row_intervals = {}
        for col in range(cols):
            self.col_intervals[col]=[]
        for row in range(rows):
            self.row_intervals[row]=[]
        for row in range(rows):
            for col in range(cols):
                if self.maze[row,col] == 1:
                    self.col_intervals[col].append((row*row_width,(row+1)*row_width))
                if self.maze[row,col] == 2:
                    self.row_intervals[row].append((col*col_width,(col+1)*col_width))
                if self.maze[row,col] == 3:
                    self.col_intervals[col].append((row*row_width,(row+1)*row_width))
                    self.row_intervals[row].append((col*col_width,(col+1)*col_width))
    def make_maze_images(self,im_size=(300,300)):
        bottom_line_numbers = (2,3)
        right_line_numbers = (1,3)
        im = Image.new('RGBA',im_size,(0,0,0,0))
        draw=ImageDraw.Draw(im)
        column_width = im_size[0] / self.maze.shape[1]
        row_width = im_size[1] / self.maze.shape[0]
        for row in range(self.maze.shape[0]):
            for column in range(self.maze.shape[1]):
                if self.maze[row,column] in bottom_line_numbers:
                    i = column * column_width, (row + 1) * row_width
                    f = i[0] + column_width, i[1]
                    draw.line((i[0],i[1],
                               f[0],f[1]),
                               fill="#AFAFAF",
                               width=4)
                if self.maze[row,column] in right_line_numbers:
                    i = (column + 1) * column_width, row * row_width
                    f = i[0], i[1] + row_width
                    draw.line((i[0],i[1],
                               f[0],f[1]),
                               fill="#AFAFAF",
                               width=4)
        try: im.save("source/maze.png")
        except Exception as e: 
            if str(e) != "": print(e)
        for i in range(len(self.solution)-1):
            start_point = self.solution[i]
            end_point = self.solution[i+1]
            i = start_point[1] * column_width + column_width / 2,start_point[0] * row_width + row_width / 2
            f = end_point[1] * column_width + column_width / 2,end_point[0] * row_width + row_width / 2
            draw.line((i[0],i[1],
                       f[0],f[1]),
                       fill="#550000FF",
                       width=10)
        try: im.save("source/maze_with_path.png")
        except Exception as e: 
            if str(e) != "": print(e)
    def distance_to_path(self,start_cell):
        start_cell = tuple(start_cell)
        paths_found = []
        dist_to_path = self.maze.size
        visited_cells = np.zeros(self.size)
        steps_taken = 0
        unvisited_neighbors = []
        unvisited_neighbors.append(start_cell)
        visited_cells = []
        while unvisited_neighbors:
            for cell in list(unvisited_neighbors):
                if cell in self.solution: 
                    return steps_taken, cell
                visited_cells.append(cell)
                if cell[0]>0:
                    if self.maze[cell[0]-1,cell[1]] in (0,1):
                        cell_to_check = (cell[0]-1,cell[1])
                        if cell_to_check not in visited_cells:
                            unvisited_neighbors.append(cell_to_check)
                if cell[1]>0:
                    if self.maze[cell[0],cell[1]-1] in (0,2):
                        cell_to_check = (cell[0],cell[1]-1)
                        if cell_to_check not in visited_cells:
                            unvisited_neighbors.append(cell_to_check)
                if cell[0] < self.maze.shape[0]-1:
                    if self.maze[cell] in (0,1):
                        cell_to_check = (cell[0]+1,cell[1])
                        if cell_to_check not in visited_cells:
                            unvisited_neighbors.append(cell_to_check)
                if cell[1] < self.maze.shape[1]-1:
                    if self.maze[cell] in (0,2):
                        cell_to_check = (cell[0],cell[1]+1)
                        if cell_to_check not in visited_cells:
                            unvisited_neighbors.append(cell_to_check)
                unvisited_neighbors.remove(cell)
                # print("unvisited_neighbors: " + str(unvisited_neighbors))
            steps_taken += 1
            # print("steps_taken: " + str(steps_taken))

