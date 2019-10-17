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
        self.max_win_size = (1200,700)
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
        self.close_button = Button(self.bottom_buttons_frame,
                                   command=self.close,
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
        self.generation_entry.config(font=self.main_font,width=5)
        # self.generation_entry.config(state="disabled")
        self.generation_entry.grid(row=0,column=1)
        #
        Label(self.bottom_entries_frame0, text=" Alive: ",font=self.main_font).grid(row=0, column=3)
        self.alive_entry = Entry(self.bottom_entries_frame0,justify='right')
        self.alive_entry.insert("end","0")
        self.alive_entry.config(font=self.main_font,width=5)
        # self.alive_entry.config(state="disabled")
        self.alive_entry.grid(row=0,column=4)
        #
        Label(self.bottom_entries_frame0, text=" High Score: ",font=self.main_font).grid(row=0, column=5)
        self.high_score = Entry(self.bottom_entries_frame0,justify='center')
        self.high_score.insert("end","0")
        self.high_score.config(font=self.main_font,width=17)
        self.high_score.config(state="disabled")
        self.high_score.grid(row=0,column=6)
        # bottom entries 1
        self.bottom_entries_frame1 = ttk.Frame(self.primary_window)
        self.bottom_entries_frame1.grid(row=5,column=0,columnspan=2)
        #
        #
        self.show_path_check = IntVar()
        self.show_path_check.set(1)
        self.show_path_button = Checkbutton(self.bottom_entries_frame1, text="Show Path", variable=self.show_path_check,font=self.main_font)
        self.show_path_button.grid(row=0,column=1)
        #
        Label(self.bottom_entries_frame1, text=" Width:",font=self.main_font).grid(row=0, column=4)
        self.width_entry = Entry(self.bottom_entries_frame1,justify='right')
        self.width_entry.insert("end", '11')
        self.width_entry.config(font=self.main_font,width=5)
        self.width_entry.grid(row=0,column=5)
        #
        Label(self.bottom_entries_frame1, text=" Height:",font=self.main_font).grid(row=0, column=6)
        self.height_entry = Entry(self.bottom_entries_frame1,justify='right')
        self.height_entry.insert("end", '8')
        self.height_entry.config(font=self.main_font,width=5)
        self.height_entry.grid(row=0,column=7)
        #
        Label(self.bottom_entries_frame1, text=" Max Steps:",font=self.main_font).grid(row=0, column=8)
        self.max_steps_entry = Entry(self.bottom_entries_frame1,justify='right')
        self.max_steps_entry.insert("end", '500')
        self.max_steps_entry.config(font=self.main_font,width=5)
        self.max_steps_entry.grid(row=0,column=9)
    def update_generation_entry(self):
        val = str(self.parent.generation_number)
        # self.generation_entry.config(state="normal")
        self.generation_entry.delete(0,'end')
        self.generation_entry.insert('end',val)
        # self.generation_entry.config(state='disabled')
    def update_alive_entry(self):
        val = str(self.parent.number_alive)
        if val != self.alive_entry.get():
            # self.alive_entry.config(state="normal")
            self.alive_entry.delete(0,'end')
            self.alive_entry.insert('end',val)
            # self.alive_entry.config(state='disabled')
    def update_high_score_entry(self):
        val = str(int(self.parent.best_adjusted_fitness//.0001))
        # self.high_score.config(state="normal")
        self.high_score.delete(0,'end')
        self.high_score.insert('end',val)
        # self.high_score.config(state='disabled')
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
    def close(self):
        # self.primary_window.destroy()
        self.parent.close()
    def create_bg(self):
        self.maze_bg = Image.open('source/maze.png')
        self.maze_bg = ImageTk.PhotoImage(self.maze_bg)
    def update_display(self,im):
        self.im[self.canvas_image_counter] = ImageTk.PhotoImage(im)
        self.the_canvas.create_image((0,0),anchor='nw',image=self.im[self.canvas_image_counter])
        if self.canvas_image_counter == 0: self.canvas_image_counter = 1
        else: self.canvas_image_counter = 0