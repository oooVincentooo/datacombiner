# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 16:54:06 2022

@author: vpreemen
"""
import tkinter as tk
from tkinter import ttk

class progress(object):
    def __init__(self, master=None):
        
        #self.parent=parent
        self.master=master
        self.ctr=0
        
        #Console message window toplevel
        self.progress = tk.Toplevel()
        self.progress.geometry("720x100")
        self.progress.minsize(720,100)
        self.progress.title("Progress Bar")
        
        self.progress.tk.call('wm', 'iconphoto', self.progress._w, tk.PhotoImage(file='Settings/ICON small.png'))  
        
        self.progress.attributes('-topmost',True)
        
        self.progress.columnconfigure(0, weight=8)
        
        self.progress.rowconfigure(0, weight=2)
        self.progress.rowconfigure(1, weight=6)

        self.p = ttk.Progressbar(self.progress, orient=tk.HORIZONTAL,
                             mode='determinate')
        self.p.grid(column=0, row=0, columnspan = 1, rowspan =1,
                              padx=2, pady=5, sticky='NSEW')

        self.label=tk.Label(self.progress, text="Start", width=10, font=('helvetica', 12), wraplength=700)
        self.label.grid(column=0, row=1, columnspan = 1, rowspan =1,
                          padx=5, pady=5, sticky='NSEW')

        self.progress.update() 

        
        if self.master!=None:

            wc=self.progress.winfo_width()
            hc=self.progress.winfo_height()            

            w=self.master.winfo_width()
            h=self.master.winfo_height()
            x=self.master.winfo_x()
            y=self.master.winfo_y()
            
            #self.progress.geometry("+%d+%d" % (x  +5   , y + h - hc-5))
            
            self.progress.geometry("+%d+%d" % (x  + w/2 -wc/2   , y + h/2 - hc/2     ))


    def progress_update(self, ctr, text, determinate):
        self.determinate=determinate
        self.text=text
        self.ctr=ctr
        
        if self.determinate:
        
            self.p.config(mode="determinate", maximum=100, value=self.ctr)
            self.label["text"]=self.text
            self.progress.update() 
        else:
            self.p.config(mode="indeterminate", maximum=100)
            self.label["text"]=self.text           
            self.p.start(10)
            self.p.step(5)
            
            self.progress.update() 
            self.progress.tkraise()
    
    def progress_exit(self):

        self.progress.destroy()
        self.progress.update()

