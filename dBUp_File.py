# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 09:55:34 2022

@author: vpreemen
"""

import glob
import time
import os
from datetime import datetime, timedelta

import numpy as np

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askokcancel

from tkcalendar import DateEntry
import babel.numbers

import tkinter.filedialog as fd

from pathlib import Path
from dBUp_Progress import progress

#Date entry not visible babel.numbers
#https://stackoverflow.com/questions/66604431/problem-with-py-to-exe-tkinter-widgets-not-visible
        
class fileselect(object):
    def __init__(self, master, button=None, directories=None, filefilter=None):
 
        self.master=master       
        
        self.button=button
        self.button.config(state='disabled')
        
        self.directories=directories
        self.filefilter=filefilter
    
        self.filearray=[]
        
        #Console message window toplevel
        self.fileselect = tk.Toplevel()
        self.fileselect.iconify()

        x=self.master.winfo_x()
        y=self.master.winfo_y()
        
        self.fileselect.geometry("+%d+%d" % (x+25   , y+25 ))
        
        self.fileselect.tk.call('wm', 'iconphoto',self.fileselect._w, tk.PhotoImage(file='Settings/ICON small.png'))  
        
        self.fileselect.columnconfigure(0, minsize=5)
        self.fileselect.columnconfigure(1, weight=15)
        self.fileselect.columnconfigure(2, minsize=5)
            
        self.fileselect.rowconfigure(0, weight=10)
        self.fileselect.rowconfigure(1, weight=0)
        self.fileselect.rowconfigure(2, weight=0)
        self.fileselect.rowconfigure(3, weight=0)
        self.fileselect.rowconfigure(4, weight=0)
        self.fileselect.rowconfigure(5, weight=0)  

        self.fileselect.geometry("720x405")
        self.fileselect.minsize(720,405)
        self.fileselect.title("Custom Filedialog")
        self.fileselect.protocol("WM_DELETE_WINDOW", self.exit_dialog)
        self.fileselect.attributes('-topmost',True)
        

         
        self.endtime=datetime.now()       
        self.starttime=(self.endtime-timedelta(days=30))
      
        columns=('File', 'Extension', 'Date')
 
        self.searchbox = ttk.Combobox(self.fileselect, textvariable='select (custom) filetype', font=('helvetica', 12))
        self.searchbox.grid(column=1, row=2, columnspan = 1, rowspan =1,
                          padx=5, pady=5, sticky='EW')
        
        self.searchbox['values']=self.filefilter     
        self.searchbox.current(0)

        self.searchbox.bind("<KeyRelease>", self.fileupdate)       
        self.searchbox.bind('<<ComboboxSelected>>', self.fileupdate)  

        self.dirlabel = ttk.Label(self.fileselect, text="", font=('helvetica', 12), anchor=tk.W)
        self.dirlabel.grid(column=0, row=3, columnspan = 2, rowspan =1,
                          padx=5, pady=0, sticky='WE') 
  
        self.directory=tk.Button(self.fileselect, text='Path', command=self.filedir, font=('helvetica', 12), width=10)
        self.directory.grid(column=2, row=3, columnspan = 1, rowspan =1,
                          padx=5, pady=5, sticky='W') 
        
        self.style = ttk.Style()
        #self.style.theme_use("default")

        self.style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('helvetica', 12)) # Modify the font of the body
        self.style.configure("mystyle.Treeview.Heading", font=('helvetica', 12)) # Modify the font of the headings   
        
        self.pathbox=ttk.Treeview(self.fileselect, columns=columns,style="mystyle.Treeview", selectmode='extended')  
        self.scrollpath = ttk.Scrollbar(self.fileselect, orient='vertical', command=self.pathbox.yview)
        self.scrollpath.grid(column=2, row=0, columnspan = 1, rowspan = 1,
                            sticky='NSE')        
  
        self.pathbox.heading('File',text='File',anchor=tk.W)
        self.pathbox.heading('Extension',text='Extension',anchor=tk.W)
        self.pathbox.heading('Date',text='Date',anchor=tk.W)
 
        self.pathbox.column("#0", minwidth=10, width=10, stretch=False)
        self.pathbox.column("File", minwidth=400, width=400, stretch=True)  
        self.pathbox.column("Extension", minwidth=50, width=50, stretch=True)          
        self.pathbox.column("Date", minwidth=50, width=50, stretch=True)
        
        self.pathbox.bind("<Delete>", self.pathboxdelete)    
        self.pathbox.grid(column=0, row=0, columnspan = 3, rowspan =1,
                           sticky='NSEW')

        #self.pathbox['show'] = 'headings'
        self.pathbox['yscrollcommand'] = self.scrollpath.set

        self.endlabel = ttk.Label(self.fileselect, text="end date:", width=35)
        self.endlabel.grid(column=2, row=1, columnspan = 1, rowspan =1,
                          padx=5, pady=0, sticky='EW')    
        self.end = DateEntry(self.fileselect, width=12, background='gray' , date_pattern='dd/mm/y',
                        foreground='white', borderwidth=0, font=('helvetica', 12))
        self.end.grid(column=2, row=2, columnspan = 1, rowspan =1,
                          padx=5, pady=5, sticky='EW') 
        self.end.set_date(self.endtime)
        self.end.bind('<<DateEntrySelected>>', self.fileupdate)          


        self.startlabel = ttk.Label(self.fileselect, text="start date:", width=35)
        self.startlabel.grid(column=0, row=1, columnspan = 1, rowspan =1,
                          padx=5, pady=0, sticky='EW') 
        self.start = DateEntry(self.fileselect, width=12, background='gray', date_pattern='dd/mm/y' ,
                        foreground='white', borderwidth=0, font=('helvetica', 12))
        self.start.set_date(self.starttime)
        self.start.bind('<<DateEntrySelected>>', self.fileupdate)    
        self.start.grid(column=0, row=2, columnspan = 1, rowspan =1,
                          padx=5, pady=5, sticky='EW')       

        self.searchlabel = ttk.Label(self.fileselect, text="find:")
        self.searchlabel.grid(column=1, row=1, columnspan = 1, rowspan =1,
                          padx=5, pady=0, sticky='EW') 
        
        self.fileselect.option_add('*TCombobox*Listbox.font', ('helvetica', 12))
    

        self.ok=tk.Button(self.fileselect, text='Open', command=self.close, font=('helvetica', 12), width=10)
        self.ok.grid(column=2, row=4, columnspan = 1, rowspan =1,
                           padx=5, pady=5, sticky='W')   
        
        self.cancel=tk.Button(self.fileselect, text='Cancel', command=self.exit_dialog, font=('helvetica', 12), width=10)
        self.cancel.grid(column=2, row=4, columnspan = 1, rowspan =1,
                           padx=5, pady=5, sticky='E')  
               
        self.info = ttk.Label(self.fileselect, text="Advanced file search: press <del>/<Entf> to remove files from list. Search depth: " 
                              + str(self.directories) + " directories (recipe setting).", font=('helvetica', 10),width=50)
        
        self.info.grid(column=0, row=5, columnspan = 3, rowspan =1,
                          padx=5, pady=0, sticky='EW') 

        
    def pathboxdelete(self, event=None):
        
        selected_items = self.pathbox.selection()        
        for selected_item in selected_items:          
           self.pathbox.delete(selected_item)
 
           
    def fileupdate(self, event=None):

        if len(self.dirlabel['text'])>0:
            self.searchbox.focus()
            self.fileselect.update()        
            self.searchfiles()

        
    def datestr(self, date):
        return date.strftime("%d/%m/%Y")      


    def searchfiles(self):

        self.pathbox.delete(*self.pathbox.get_children())
 
        dirs=len(Path(self.dir).parents) - 1
        answer=True
        
        if dirs<=2 or self.directories>3:         
        
            answer = askokcancel(parent=self.fileselect, 
                title='Confirmation',
                message='Root Directory:\n' +  str(self.dir) +  "\n\nSearch for: " + str(self.searchbox.get()) + ", in: " + str(self.directories) + " subdirectories deep?"  )
                
        if answer:
            self.pbar=progress(self.fileselect)
            self.pbar.progress_update(5, 'Reading files...' ,True)  
            self.searchdirectories()              
        

        self.pbar.progress_exit()


    def searchdirectories(self):

        
        files_total=[]
        searchdepth=""
        
        for i in range(self.directories):
 
            
  
            
            #https://stackoverflow.com/questions/14798220/how-can-i-search-sub-folders-using-glob-glob-module
            
            path=os.path.join("", Path(self.dir), searchdepth,str(self.searchbox.get()) )

            self.pbar.progress_update(80*(i+1)/self.directories, 'Reading: ' + str(path)  + str(self.searchbox.get())   ,True) 


            files_subdir = glob.glob(path, recursive = True)        
            files_total=files_total+files_subdir
            searchdepth=os.path.join("",searchdepth,"*","","")


        size=len(files_total)
        
        for i, file_path in enumerate(files_total):
            
            if i%50==0:
                self.pbar.progress_update((i+1)/size*100, 'Reading: ' + str(i+1) + "/" + str(size) + ", " + str(file_path)    ,True)
             
            t=os.path.getmtime(file_path)     
            file_t=datetime.fromtimestamp(t)         
            file_t=file_t.date()
            
            if (file_t<=self.end.get_date()) and (file_t>=self.start.get_date()):
                filename=os.path.basename(file_path)
                extension = os.path.splitext(filename)[1]
                self.pathbox.insert('', tk.END, iid=os.path.join('',file_path), 
                                    text=os.path.join('',file_path),  values=[filename,extension,self.datestr(file_t)])            
        
        
        



    def fileboxdelete(self):

        selected_items = self.pathbox.selection()        
        for selected_item in selected_items:          
           self.pathbox.delete(selected_item)

    
    def filedir(self):
    
        self.dir= fd.askdirectory(parent=self.fileselect)
        self.dirlabel['text'] =self.dir
        #print(self.dir)
        
        if not(self.dir==None or len(self.dir)==0):
            self.searchfiles()


    def close(self):     
        self.fileselect.update()
        self.filearray=self.pathbox.get_children()
        self.button.config(state='normal')
        self.fileselect.destroy()


    def exit_dialog(self):     
        self.fileselect.update()
        self.filearray=[]
        self.button.config(state='normal')
        self.fileselect.destroy()
       

    def show(self):
      
        self.fileselect.deiconify()
        self.fileselect.wait_window()
        value = self.filearray

        return value
        #https://stackoverflow.com/questions/29497391/creating-a-tkinter-class-and-waiting-for-a-return-value        

#root = tk.Tk()
#s = ttk.Style(root)
#app = fileselect(root,1,2,['*.*'])
#root.mainloop()




