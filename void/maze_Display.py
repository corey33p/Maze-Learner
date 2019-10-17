from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import Canvas,Tk,ttk,Label,Entry,Button,mainloop,Text,Frame,IntVar,Checkbutton
import os
import numpy as np
from tkinter import filedialog
import math
import random
import time

class Display:
    def __init__(self, parent):
        self.parent = parent
        self.main_font = ("Courier", 22, "bold")
        self.max_win_size = (1280,950)
        self.canvas_size = ((self.max_win_size[0],self.max_win_size[1]-230))
        self.canvas_image_counter = 0
        self.im = {}
        self.setup_window()
    def open_images(self):
        pil_img = Image.open('source/icons/play.gif').resize((80,80), Image.ANTIALIAS)
        self.play_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/icons/pause.gif').resize((80,80), Image.ANTIALIAS)
        self.pause_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/icons/close.gif').resize((80,80), Image.ANTIALIAS)
        self.close_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/icons/accept.gif').resize((80,80), Image.ANTIALIAS)
        self.accept_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/icons/refresh.gif').resize((80,80), Image.ANTIALIAS)
        self.refresh_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/icons/random.gif').resize((80,80), Image.ANTIALIAS)
        self.random_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/icons/next.gif').resize((80,80), Image.ANTIALIAS)
        self.step_photo=ImageTk.PhotoImage(pil_img)
        pil_img = Image.open('source/icons/trash.gif').resize((80,80), Image.ANTIALIAS)
        self.clear_photo=ImageTk.PhotoImage(pil_img)
    def setup_window(self):
        # initial setup
        self.primary_window = Tk()
        self.open_images()
        self.primary_window.wm_title("Maze Runners")
        self.primary_window.geometry('1274x960-1+0')
        self.primary_window.minsize(width=100, height=30)
        self.primary_window.maxsize(width=self.max_win_size[0], height=self.max_win_size[1])
        
        # image & canvas
        self.im_frame = ttk.Frame(self.primary_window)
        self.im_frame.grid(row=0,column=0,columnspan=2,sticky="nsew")
        self.im_frame.columnconfigure(0, weight=1)
        self.im_frame.rowconfigure(0, weight=1)
        self.primary_window.columnconfigure(0, weight=1)
        self.primary_window.rowconfigure(0, weight=1)
        
        self.canvas_frame = ttk.Frame(self.primary_window)
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.columnconfigure(0, weight=1)
        
        self.the_canvas = Canvas(self.canvas_frame,
                                width=self.canvas_size[0],
                                height=self.canvas_size[1],
                                background='black')
        self.the_canvas.grid(row=0, column=0,columnspan=2, sticky="ew")
        
        # bottom buttons
        self.bottom_buttons_frame = ttk.Frame(self.primary_window)
        self.bottom_buttons_frame.grid(row=3,column=0,columnspan=2)
        #
        self.play_button = Button(self.bottom_buttons_frame,
                                    command= self.play_button_func,
                                    image=self.play_photo,
                                    width="80",height="80")
        self.play_button.grid(row=0,column=0)
        #
        self.pause_button = Button(self.bottom_buttons_frame,
                                      command=self.pause_button_func,
                                      image=self.pause_photo,
                                      width="80",height="80")
        self.pause_button.grid(row=0,column=2)
        #
        self.random_button = Button(self.bottom_buttons_frame,
                                    command=self.parent.new_game,
                                    image=self.refresh_photo,
                                    width="80",height="80")
        self.random_button.grid(row=0,column=3)
        #
        self.step_button = Button(self.bottom_buttons_frame,
                                   command=self.step,
                                   image=self.step_photo,
                                   width="80",height="80")
        self.step_button.grid(row=0,column=4)
        #
        self.clear_button = Button(self.bottom_buttons_frame,
                                   command=self.clear,
                                   image=self.clear_photo,
                                   width="80",height="80")
        self.clear_button.grid(row=0,column=5)
        #
        self.close_button = Button(self.bottom_buttons_frame,
                                   command=self.parent.close,
                                   image=self.close_photo,
                                   width="80",height="80")
        self.close_button.grid(row=0,column=6)
        # bottom entries 0
        self.bottom_entries_frame0 = ttk.Frame(self.primary_window)
        self.bottom_entries_frame0.grid(row=4,column=0,columnspan=2)
        #
        Label(self.bottom_entries_frame0, text="Generation Number: ",font=self.main_font).grid(row=0, column=0)
        self.generation_entry = Entry(self.bottom_entries_frame0,justify='right')
        self.generation_entry.insert("end","1")
        self.generation_entry.config(state="disabled",font=self.main_font,width=5)
        self.generation_entry.grid(row=0,column=1)
        #
        Label(self.bottom_entries_frame0, text=" Population: ",font=self.main_font).grid(row=0, column=3)
        self.population = Entry(self.bottom_entries_frame0,justify='right')
        self.population.insert("end","0")
        self.population.config(state="disabled",font=self.main_font,width=5)
        self.population.grid(row=0,column=4)
        #
        Label(self.bottom_entries_frame0, text=" State: ",font=self.main_font).grid(row=0, column=5)
        self.state = Entry(self.bottom_entries_frame0,justify='center')
        self.state.insert("end","Normal")
        self.state.config(state="disabled",font=self.main_font,width=17)
        self.state.grid(row=0,column=6)
        # bottom entries 1
        self.bottom_entries_frame1 = ttk.Frame(self.primary_window)
        self.bottom_entries_frame1.grid(row=5,column=0,columnspan=2)
        #
        #
        self.show_field_check = IntVar()
        self.show_field_check.set(1)
        self.show_field_button = Checkbutton(self.bottom_entries_frame1, text="Show Field", variable=self.show_field_check,font=self.main_font)
        self.show_field_button.grid(row=0,column=1)
        #
        Label(self.bottom_entries_frame1, text=" Width:",font=self.main_font).grid(row=0, column=4)
        self.width_entry = Entry(self.bottom_entries_frame1,justify='right')
        # self.width_entry.insert("end", str(self.canvas_size[0]//3))
        self.width_entry.insert("end", '5')
        self.width_entry.config(font=self.main_font,width=5)
        self.width_entry.grid(row=0,column=5)
        #
        Label(self.bottom_entries_frame1, text=" Height:",font=self.main_font).grid(row=0, column=6)
        self.height_entry = Entry(self.bottom_entries_frame1,justify='right')
        # self.height_entry.insert("end", str(self.canvas_size[1]//3))
        self.height_entry.insert("end", '3')
        self.height_entry.config(font=self.main_font,width=5)
        self.height_entry.grid(row=0,column=7)
    def update_generation_entry(self):
        val = str(self.parent.board.generation)
        self.generation_entry.config(state="normal")
        self.generation_entry.delete(0,'end')
        self.generation_entry.insert('end',val)
        self.generation_entry.config(state='disabled')
    def update_population_entry(self):
        val = str(self.parent.board.population)
        self.population.config(state="normal")
        self.population.delete(0,'end')
        self.population.insert('end',val)
        self.population.config(state='disabled')
    def update_state_entry(self,message):
        self.state.config(state="normal")
        self.state.delete(0,'end')
        self.state.insert('end',message)
        self.state.config(state='disabled')
    def play_button_func(self):
        self.parent.pause = False
        self.parent.main_queue.put(self.parent.play)
    def pause_button_func(self):
        if self.parent.pause: self.parent.pause = False
        else: self.parent.pause = True
    def step(self):
        self.parent.pause_step = True
        self.parent.pause = True
        if self.parent.main_queue.empty() and not self.parent.game_over:
            self.parent.main_queue.put(self.parent.play)
    def clear(self):
        y = int(self.height_entry.get())
        x = int(self.width_entry.get())
        self.parent.board.setup_board(x,y,0)
        self.board_state = 'Normal'
        #
        self.update_generation_entry()
        self.update_population_entry()
        self.update_state_entry()
        #
        if self.grid_check.get(): self.create_grid()
        self.make_canvas_interactive()
        self.update_display2()
    def create_bg(self):
        self.maze_bg = Image.open('source/maze.png')
        self.maze_bg = ImageTk.PhotoImage(self.maze_bg)
    def update_display(self,im):
        self.im[self.canvas_image_counter] = ImageTk.PhotoImage(im)
        self.the_canvas.create_image((0,0),anchor='nw',image=self.im[self.canvas_image_counter])
        if self.canvas_image_counter == 0: self.canvas_image_counter = 1
        else: self.canvas_image_counter = 0