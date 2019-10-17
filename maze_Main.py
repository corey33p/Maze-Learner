from maze_Display import Display
from maze_Maze import Mazer
from maze_FlowFieldGA import GeneticAlgorithm
from maze_Runner import Runner
from tkinter import mainloop
import os
import win32gui
import win32con
import threading
from queue import Queue
from PIL import Image
import time
import traceback
from collections import Counter

class Parent:
    def __init__(self):
        # settings
        self.population_size = 65
        self.maze_size = (10,10)
        self.field_size = (41,41)
        #
        self.main_queue = Queue()
        self.display  = Display(self)
        self.maze_maker = Mazer(self)
        self.gen_alg = GeneticAlgorithm(self,self.field_size,self.population_size)
        self.population = None
        self.number_alive = 0
        self.generation_number = 1
        self.resize_CLI_window()
        self.showing_path = not self.display.show_path_check.get()
        self.new_game()
        self.game_over = False
        self.best_fitness = 0
        self.best_adjusted_fitness = 0
        self.max_steps = self.display.max_steps_entry.get()
        self.step_penalties = {}
        #
        self.pause = False
        main_queue_thread = threading.Thread(target=lambda: self.main_queue_thread())
        main_queue_thread.daemon = True
        main_queue_thread.start()
       
        mainloop()
    def play(self):
        self.pause_step = False
        number_of_steps = 0
        self.hit_wall = 0
        self.stopped = 0
        self.off_edge = 0
        while True:
            self.number_alive = 0
            while self.pause and not self.pause_step: 
                time.sleep(.2)
            any_alive = False
            for runner in self.population.values():
                if runner.alive:
                    self.number_alive += 1
                    any_alive = True
                    runner.move()
                    if self.display.show_path_check.get():
                        runner.draw_path()
                    else:
                        runner.move_runner()
            self.display.update_alive_entry()
            number_of_steps += 1
            if number_of_steps > int(self.max_steps):
                print("Reached " + self.max_steps + " steps.")
                for runner in self.population.values():
                    runner.alive = False
                    if runner.cause_of_death == 'unknown':
                        runner.cause_of_death = 'too many steps'
                    any_alive = False
                    number_of_steps = 0
            if not any_alive:
                self.scores = []
                self.adjusted_scores = []
                for runner in self.population.values():
                    current_score = runner.best_fitness
                    self.scores.append(current_score)
                    if current_score > self.best_fitness:
                        self.best_fitness = current_score
                        self.display.update_high_score_entry()
                        x_loc = runner.best_location
                        x_loc = (x_loc[1]*self.display.canvas_size[0],
                                 x_loc[0]*self.display.canvas_size[1])
                        self.display.the_canvas.delete("redX")
                        self.display.the_canvas.create_text(x_loc,text='X',font=self.display.main_font,fill='red',tags=('X','redX'))
                    current_score = runner.best_adjusted_fitness
                    self.adjusted_scores.append(current_score)
                    if current_score > self.best_adjusted_fitness:
                        self.best_adjusted_fitness = current_score
                        self.display.update_high_score_entry()
                        x_loc = runner.location_of_best_fitness
                        x_loc = (x_loc[1]*self.display.canvas_size[0],
                                 x_loc[0]*self.display.canvas_size[1])
                        self.display.the_canvas.delete("greenX")
                        self.display.the_canvas.create_text(x_loc,text='X',font=self.display.main_font,fill='green',tags=('X','greenX'))
                number_of_steps = 0
                cause_of_death = [runner.cause_of_death for runner in self.population.values()]
                if None in self.scores: 1/0
                self.game_over = True
                print("All runners died!")
                cause_of_death = dict(Counter(cause_of_death))
                print("Cause of death: ")
                for i in cause_of_death: 
                    print("    "+str(i)+": "+str(cause_of_death[i]))
                time.sleep(.5) # time to see the end result
                self.crossover()
            self.pause_step = False
    def populate(self):
        self.best_fitness = 0
        self.best_adjusted_fitness = 0
        self.game_over = False
        self.display.the_canvas.delete('path')
        self.display.the_canvas.delete('runner')
        self.display.the_canvas.delete('X')
        self.population = {}
        self.gen_alg.populate()
        for i in range(self.population_size):
            self.population[i] = Runner(self,self.gen_alg.vector_field[i,...],self.maze_maker.maze,i)
        # if self.display.show_field_check.get() == 1:
            # field = Image.open('flowfields/0.png')
            # field = field.resize(self.display.canvas_size)
            # self.maze_image.paste(field,(0,0),
                                # mask=field)
            # self.display.update_display(self.maze_image)
        self.number_alive = len(self.population)
        self.max_steps = self.display.max_steps_entry.get()
        print("\nNew population created.")
    def crossover(self):   
        self.game_over = False
        self.display.the_canvas.delete('path')
        self.display.the_canvas.delete('runner')    
        self.gen_alg.crossover(self.adjusted_scores)
        self.population = {}
        for i in range(self.population_size):
            self.population[i] = Runner(self,self.gen_alg.vector_field[i,...],self.maze_maker.maze,i)
        self.number_alive = len(self.population)
        self.generation_number += 1
        self.display.update_generation_entry()
        print("\nBegin generation "+str(self.generation_number))
    def resize_CLI_window(self):
        def get_windows():
            def check(hwnd, param):
                title = win32gui.GetWindowText(hwnd)
                if 'maze_Main' in title and 'Notepad++' not in title:
                    param.append(hwnd)
            wind = []
            win32gui.EnumWindows(check, wind)
            return wind
        self.cli_handles = get_windows()
        for window in self.cli_handles:
            win32gui.MoveWindow(window,0,0,self.display.max_win_size[0],self.display.max_win_size[1],True)
            # win32gui.MoveWindow(window,-1020,300,1015,640,True)
    def new_game(self):
        self.maze_maker.make_maze((int(self.display.height_entry.get()),int(self.display.width_entry.get())))
        self.maze_maker.make_maze_images(im_size=self.display.canvas_size)
        self.get_maze_im()
        # blank_im = Image.new("RGBA",self.display.canvas_size,(0,0,0,0))
        # self.display.update_display(blank_im)
        self.display.update_display(self.maze_image)
        self.populate()
    def get_maze_im(self):
        if self.display.show_path_check.get() and not self.showing_path:
            self.maze_image = Image.open("source/maze_with_path.png")#.resize(self.display.canvas_size)
            self.showing_path = True
        elif not self.display.show_path_check.get() and self.showing_path:
            self.maze_image = Image.open("source/maze.png")#.resize(self.display.canvas_size)
            self.showing_path = False
        self.display.update_display(self.maze_image)
    def main_queue_thread(self):
        while True: 
            time.sleep(.25)
            try:
                next_action = self.main_queue.get(False)
                next_action()
            except Exception as e: 
                if str(e) != "": 
                    print(traceback.format_exc())
        self.main_queue.queue.clear()
        self.close()
    def close(self):
        for handle in self.cli_handles:
            win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)

if __name__ == '__main__':
    main_object = Parent()
    