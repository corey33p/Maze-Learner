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

class Parent:
    def __init__(self):
        # settings
        self.population_size = 100
        self.maze_size = (10,10)
        self.field_size = (32,32)
        #
        self.main_queue = Queue()
        self.display  = Display(self)
        self.maze_maker = Mazer(self)
        self.gen_alg = GeneticAlgorithm(self,self.field_size,self.population_size)
        self.population = None
        self.resize_CLI_window()
        self.new_game()
        self.game_over = False
        #
        self.pause = False
        main_queue_thread = threading.Thread(target=lambda: self.main_queue_thread())
        main_queue_thread.daemon = True
        main_queue_thread.start()
        mainloop()
    def play(self):
        self.display.update_state_entry("Running")
        self.pause_step = False
        number_of_steps = 0
        while True:
            while self.pause and not self.pause_step: 
                time.sleep(.2)
            for runner in self.population.values():
                any_alive = False
                if runner.state == 'alive':
                    any_alive = True
                    runner.move()
                    runner.draw_path()
            if not any_alive:
                self.scores = [runner.get_fitness() for runner in self.population.values()]
                self.game_over = True
                print("All runners died!")
                self.display.update_state_entry("No runners!")
                self.crossover()
            self.pause_step = False
            number_of_steps += 1
            if number_of_steps > 1000:
                print("Reached 1000 steps.")
                for runner in self.population.values():
                    runner.state = 'dead' 
    def populate(self):
        self.game_over = False
        self.display.the_canvas.delete('path')
        self.display.the_canvas.delete('runner')
        self.population = {}
        self.gen_alg.populate()
        for i in range(self.population_size):
            self.population[i] = Runner(self,self.gen_alg.acceleration_field[i,...],self.maze_maker.maze,i)
        # if self.display.show_field_check.get() == 1:
            # field = Image.open('flowfields/0.png')
            # field = field.resize(self.display.canvas_size)
            # self.maze_image.paste(field,(0,0),
                                # mask=field)
            # self.display.update_display(self.maze_image)
        print("\nNew population created.")
    def crossover(self):   
        self.game_over = False
        self.display.the_canvas.delete('path')
        self.display.the_canvas.delete('runner')    
        self.gen_alg.crossover(self.scores)
        self.population = {}
        for i in range(self.population_size):
            self.population[i] = Runner(self,self.gen_alg.acceleration_field[i,...],self.maze_maker.maze,i)
        print("Begin generation.")
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
            # win32gui.MoveWindow(window,0,0,self.display.max_win_size[0],self.display.max_win_size[1],True)
            win32gui.MoveWindow(window,-1020,300,1015,640,True)
    def new_game(self):
        self.maze_maker.make_maze((int(self.display.height_entry.get()),int(self.display.width_entry.get())))
        self.maze_image = self.maze_maker.make_maze_image(im_size=self.display.canvas_size)
        blank_im = Image.new("RGBA",self.display.canvas_size,(0,0,0,0))
        self.display.update_display(blank_im)
        self.display.update_display(self.maze_image)
        self.populate()
    def main_queue_thread(self):
        while True: # handle objects in the queue until game_lost
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
    