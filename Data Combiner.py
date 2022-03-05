# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 11:22:33 2022

@author: vpreemen
"""
 

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askokcancel, showinfo
import tkinter.filedialog as fd
import tkinter.simpledialog as sd

from datetime import datetime
import time
 
import pandas as pd
from pandastable import Table, TableModel
from pandas.api.types import is_numeric_dtype

import openpyxl 

from dBup_IO_TXT import recipe
from dBup_IO_TXT import data_txt
from dBup_IO_XLS import data_xls
from dBUp_File import fileselect
from dBUp_Progress import progress

import numpy as np
import os
import sys
from pathlib import Path

from PIL import Image, ImageTk

class MainApp(tk.Frame): # Inherits Frame methods
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs) # Initializes the frame
        
        self.version="version: 0.0142"
        self.master=master
        self.createWidgets()   

        #open default recipe
        self.recipe=recipe.read_recipe('recipes/Default.yaml')  
        self.recipelabel.config(text=os.path.basename("recipes/Default.yaml"))  
        self.recipename='Default.yaml' 
        self.recipe_read()
  
        self.fileselect=[]
        
    def createWidgets(self):  
                
        #Grid for objects in frame
        #https://stackoverflow.com/questions/24644339/python-tkinter-resize-widgets-evenly-in-a-window
        self.columnconfigure(0, minsize=5)
        self.columnconfigure(1, weight=20)
        self.columnconfigure(2, minsize=5)
        self.columnconfigure(3, weight=20)
        self.columnconfigure(4, minsize=5)
        self.columnconfigure(5, minsize=20)
        self.columnconfigure(6, minsize=5)
        
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, minsize=5)
        self.rowconfigure(3, weight=40)
        self.rowconfigure(4, weight=0)

        self.pack(fill=tk.BOTH, expand=True)        

        self.filedialog=None
        
        #app logo image
        #https://stackoverflow.com/questions/24274072/tkinter-pyimage-doesnt-exist
        self.img = Image.open('settings/ICON.png')
        self.img = self.img.resize((int(650*0.25), int(900*0.25)))
        self.bg = ImageTk.PhotoImage(self.img)
        self.lbl = tk.Label(self, image=self.bg)
        self.lbl.grid(column=5, row=1,   padx=(0,0), sticky='NSEW')
        self.img.close()
        
        #Button Select Files
        self.selectfiles = tk.Button(self, text="Select Files", command=self.file_open,font=('helvetica', 12))
        self.selectfiles.grid(column=1, row=2, columnspan = 1, rowspan =1,
                              padx=0, pady=5, sticky='NES')

        #Button Open Recipe
        self.openrecipe = tk.Button(self, text="Open Recipe", command=self.recipe_open,font=('helvetica', 12))
        self.openrecipe.grid(column=3,row=2,columnspan = 1, rowspan =1,
                             padx=125, pady=5, sticky='NES')  

        #Add a Button Save Recipe
        self.saverecipe = tk.Button(self, text="Save Recipe", command=self.recipe_save,font=('helvetica', 12))
        self.saverecipe.grid(column=3, row=2, columnspan = 1, rowspan =1,
                        padx=0, pady=5,sticky='NSE') 

        #Start Batch
        self.startbatch = tk.Button(self, text="Start Batch", command=self.batch,font=('helvetica', 12))
        self.startbatch.grid(column=5, row=2, columnspan = 1, rowspan =1, 
                        padx=0, pady=5, sticky='NEWS')
        
        #Add frame for panda stable
        self.tableframe = tk.Frame(master=self)
        self.tableframe.grid(row=3, column=1, columnspan =5, rowspan =1,  padx=0, pady=5, sticky=tk.N+tk.S+tk.E +tk.W)
        
        #Add listbox for files
        self.pathlabel = tk.Label(self, text="",width=40, anchor=tk.W)
        self.pathlabel.config(font=('helvetica', 12))
        self.pathlabel.grid(column=1, row=0, columnspan = 1, rowspan =1,sticky='EW')
 
        #Style
        self.style = ttk.Style()
        #self.style.theme_use("default")
        self.style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('helvetica', 12)) # Modify the font of the body
        self.style.configure("mystyle.Treeview.Heading", font=('helvetica', 12)) # Modify the font of the headings       

        #Treeview File Path         
        columns=('Filename','Path','Data')
        self.pathbox=ttk.Treeview(self, columns=columns,style="mystyle.Treeview", selectmode='browse')  
        #self.pathbox=ttk.Treeview(self, style="mystyle.Treeview", selectmode='browse')  
        
        
        self.pathbox.heading('Filename',text='Filename',anchor=tk.W)
        self.pathbox.heading('Path',text='Path',anchor=tk.W)
        self.pathbox.heading('Data',text='Data',anchor=tk.W)

        self.pathbox.column("#0", minwidth=300, width=300, stretch=True)
        self.pathbox.column("Filename", minwidth=0, width=0, stretch=False)
        self.pathbox.column("Path",  minwidth=0, width=0, stretch=False)
        self.pathbox.column("Data",  minwidth=0, width=0, stretch=False)
        self.pathbox.bind('<<TreeviewSelect>>', self.file_update)       
        self.pathbox.grid(column=1, row=1, columnspan = 1, rowspan =1,
                           sticky='NSEW')

        self.pathbox['show'] = 'tree'
        self.scrollpath = ttk.Scrollbar(self, orient='vertical', command=self.pathbox.yview)
        self.scrollpath.grid(column=2, row=1, columnspan = 1, rowspan = 1,
                            sticky='NSEW')
        self.pathbox['yscrollcommand'] = self.scrollpath.set
        
        #Recipe treeview
        self.recipelabel = tk.Label(self, text="Recipe",width=40, anchor=tk.W)
        self.recipelabel.config(font=('helvetica', 12))
        self.recipelabel.grid(column=3, row=0, columnspan = 1, rowspan =1,
                              sticky='SW')
        
        self.recipetree = ttk.Treeview(self,style="mystyle.Treeview", selectmode='browse')
        self.recipetree["columns"]=("one","two")
        self.recipetree.bind("<Double-1>", self.recipe_click) 
        self.recipetree.column("#0", width=200, stretch=False)
        self.recipetree.column("one", width=150, stretch=False)
        self.recipetree.column("two", width=200, stretch=True)
        self.recipetree.heading("#0",text="Recipe Item",anchor=tk.W)
        self.recipetree.heading("one", text="Value",anchor=tk.W)
        self.recipetree.heading("two", text="Info",anchor=tk.W)
        
        self.recipetree.grid(column=3, row=1, columnspan = 1, rowspan =1,
                                sticky='NSEW')
        
        self.scrolltree = ttk.Scrollbar(self, orient='vertical', command=self.recipetree.yview)
        self.scrolltree.grid(column=4, row=1, columnspan = 1, rowspan = 1, sticky='NSEW')       
        self.recipetree['yscrollcommand'] = self.scrolltree.set
        
        self.tableframe = tk.Frame(master=self)
        self.tableframe.grid(row=3, column=1, columnspan =5, rowspan =1,  padx=0, pady=0, sticky='NSEW')
        self.table=Table(self.tableframe,enable_menus=False, showtoolbar=False, showstatusbar=True)
        self.table.show()
        
        #Version label
        self.versionlabel = tk.Label(self, text="")
        self.versionlabel.config(font=('helvetica', 12))
        self.versionlabel.grid(column=5, row=4, columnspan = 1, rowspan =1, sticky='NE')
        self.versionlabel.config(text=self.version)
        
        #Console message window toplevel
        self.console = tk.Toplevel()
        self.console.geometry("720x270")
        self.console.title("Console Messages")
        self.console.protocol("WM_DELETE_WINDOW", self.consoleexit)
        self.console.attributes('-topmost',True)
        self.console.withdraw()

        self.consoletext = tk.Text(self.console, wrap="none", font=('helvetica', 12))
        self.consoletext.insert(tk.END, "Console window.")
        
        self.scroll_bar = tk.Scrollbar(self.console, command=self.consoletext.yview)
        self.scroll_bar.pack(side=tk.RIGHT,fill="y", padx=(0,0), pady=0)      
        self.consoletext['yscrollcommand'] = self.scroll_bar.set             
        self.consoletext.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5,0), pady=(0,5), expand=True)
        
        #Console visible checkbox root
        self.consoleon = tk.IntVar ()
        self.consoleshow = tk.Checkbutton(self, text='console',variable=self.consoleon, 
                                          onvalue=True, offvalue=False, command=self.consolehide, font=('helvetica', 12))
        self.consoleshow.grid(row=4, column=1, columnspan =1, rowspan =1,  padx=0, pady=0, sticky='W')


        self.console.tk.call('wm', 'iconphoto', self.console._w, tk.PhotoImage(file='Settings/ICON small.png'))        
        
    def consolemessage(self,text):
        
        dt=datetime.now() 
        sdt=dt.strftime("%b %d %Y %H:%M:%S")
        self.consoletext.insert(tk.END, "\n" + sdt + "> " + text)
        self.consoletext.yview_pickplace("end")
        

    def consoleexit(self):
        
         self.consolemessage("exit: close main window.")
         self.console.withdraw()
         self.consolemessage("console: hidden")
         self.consoleon.set(False)
         pass 

    def consolehide(self):
        
        if self.consoleon.get()==False:
            self.console.withdraw()
            self.consolemessage("console: hidden")
        else:
           self.console.deiconify()     
           self.consolemessage("console: visible")
           
           self.master.update()

           wc=self.console.winfo_width()
           hc=self.console.winfo_height()
           self.consolemessage("console: width=" + str(wc) + 
                               ", height=" + str(hc) )


           w=self.master.winfo_width()
           h=self.master.winfo_height()
           x=self.master.winfo_x()
           y=self.master.winfo_y()
           self.consolemessage("root: width=" + str(w) + 
                               ", height=" + str(h) + 
                               ", x=" + str(x) + 
                               ", y=" + str(y)  )
           self.console.geometry("+%d+%d" % (x  +5   , y + h - hc-5))
 
    
    def recipe_read(self):
        
        self.recipetree.delete(*self.recipetree.get_children())
         
        for ancestor in self.recipe:  
            
            self.recipetree.insert("","end",ancestor, text=ancestor, open=False)  
           
            for parent in self.recipe[ancestor]:
                p=self.recipetree.insert(ancestor,"end",text=parent, open=False)               

                for child in self.recipe[ancestor][parent]:
                   
                   value=self.recipe[ancestor][parent][child]['value']
                   info=self.recipe[ancestor][parent][child]['info']

                   if len(str(value))>30:
                      value="..."  
                   
                   self.recipetree.insert(p,"end",text=child,values=[value,info], open=False)
                 

    def recipe_open(self):
        
        inipath=os.path.join(os.getcwd(),"Recipes")
        file = fd.askopenfilename(parent=self.console, title='Open Recipe', filetypes=[
                        ("recipe *.yaml", ".yaml")], initialdir = inipath)
        
        if file is None or file=="": 
            self.consolemessage("open: cancelled")
            return

        self.recipename=Path(file).stem        
        self.recipe=recipe.read_recipe(file)
        self.recipe_read()
        self.recipelabel.config(text=os.path.basename(file)) 
        self.pathbox.delete(*self.pathbox.get_children())
        self.file_update(self)
        self.consolemessage("recipe: " + os.path.basename(file))

        
    def recipe_save(self):
        
        answer = askokcancel(parent=self.console, 
                title='Confirmation',
                message='Do you want to save (overwrite) recipe?')
            
        if answer:
        
            inipath=os.path.join(os.getcwd(),"Recipes")
            
            f = fd.asksaveasfile(parent=self.console, mode='w', defaultextension=".yaml", filetypes=[("recipe", ".yaml")], initialdir = inipath)
            if f is None or f=="": 
                self.consolemessage("save: cancelled")
                return
            
            # Create new (overwrite) blanco file and close
            f.write("")
            f.close()        
            recipe.write_recipe(f.name,self.recipe)
    
            self.recipelabel.config(text=os.path.basename(f.name))     
            if self.recipelabel.cget("text")[-1]=="*":
                self.recipelabel.config(text=self.recipelabel.cget("text")[:-1])
            
            self.consolemessage("saved: " + f.name)
            
            self.recipe=recipe.read_recipe(f.name)  
            self.recipelabel.config(text=os.path.basename(f.name))  
            self.recipename=Path(f.name).stem  
            self.recipe_read()

            
    def recipe_click(self,event):
       
         self.item = self.recipetree.selection()[0]
         parent =self.recipetree.parent(self.item)
         children = self.recipetree.get_children(self.item)
         
         if self.recipetree.parent(self.item):
             parent=self.recipetree.parent(self.item)       
             if self.recipetree.parent(parent): 
                 self.ancestor_text=self.recipetree.parent(parent)
         
         self.parent_text=self.recipetree.item(parent)['text']
         self.item_text=self.recipetree.item(self.item)['text']
         self.value_text=self.recipetree.item(self.item)['values']       

         #Only open message box for children
         if len(children)==0:
             self.recipe_message()
             

    def recipe_filter(self):
        
        n=self.recipe['Filter']['create']['count']['value']
        filters=len(self.recipe['Filter'])-1
           
        if n<filters and n>=0:
      
            for i in range(filters-n):
            
                del self.recipe['Filter']['filter ' + str(1+n+i)]
                self.consolemessage("filter: " + str(1+n+i) + " deleted")

            self.recipe_filterfocus()

        if n>filters:            
            for i in range(n-filters):      
                
                self.recipe['Filter']['filter ' + str(filters+i+1)] = {'comment': {'value': 'Filtering dataset on specified column.','info': 'info'},
                                     'active': {'value': 0, 'info': 'on=1/off=0, enable or disable filter.'}, 
                                     'column': {'value': 0, 'info': 'Integer, select column for filtering. Count inluding ID cols.'}, 
                                     'minimum': {'value': 0.0, 'info': 'decimal, minimum value (. is decimal seperator).'}, 
                                     'maximum': {'value': 1000000, 'info': 'decimal, maximum value (. is decimal seperator).'}}
                self.consolemessage("filter: " + str(filters+i+1)  + " created")

            self.recipe_filterfocus()
 

    def recipe_filterfocus(self):

        self.recipe_read() 
        self.update()
 
        #Set focus on last created filter                
        for child in self.recipetree.get_children():
            if self.recipetree.item(child)["text"]=='Filter':
                for c in self.recipetree.get_children(child):
                        self.recipetree.item(c, open=False)     
                        self.recipetree.selection_set(c) 
                        self.recipetree.see(c) 
 
    def recipe_identifier(self):
        
        n=self.recipe['ID Custom']['create']['count']['value']
        filters=len(self.recipe['ID Custom'])-1
           
        if n<filters and n>=0:
      
            for i in range(filters-n):
            
                del self.recipe['ID Custom']['custom ' + str(1+n+i)]
                self.consolemessage("custom id: " + str(1+n+i) + " deleted")

            self.recipe_itentifierfocus()

        if n>filters:            
            
            for i in range(n-filters):      
                
                self.recipe['ID Custom']['custom ' + str(filters+i+1)]={'comment': {'value': 'Custom column number for grouping. Index is enumeration rows every individual','info': 'info'},
                                     'active': {'value': 0, 'info': 'on=1/off=0 group by custom column. Index is enumeration rows every individual.'}, 
                                     'column': {'value': 0, 'info': 'Integer, select column (count exlcuding ID col). Set 0 for Index (rownum).'}, 
                                     'decimals': {'value': 0.0, 'info': 'Round column value to decimal places. Only for grouping column (construct=active).'}}
                self.consolemessage("custom id: " + str(filters+i+1) + " created")

            self.recipe_itentifierfocus()
 

    def recipe_itentifierfocus(self):

        self.recipe_read() 
        self.update()
        
        #Set focus on last created filter                
        for child in self.recipetree.get_children():
            if self.recipetree.item(child)["text"]=='ID Custom':
                for c in self.recipetree.get_children(child):
                        self.recipetree.item(c, open=False)     
                        self.recipetree.selection_set(c) 
                        self.recipetree.see(c) 

                        
    def recipe_message(self):  

        if self.item_text=='comment':
            
            self.value_text=self.recipe[self.ancestor_text][self.parent_text][self.item_text]['value']
            
            showinfo(title=str(self.ancestor_text) +": " + str(self.parent_text), 
                                        message=(self.value_text), parent=self.recipetree)
            
        else:

            value=self.recipe_msgselect()
  
            if value is not None:
                self.value_text['value']=value   
                self.recipetree.item(self.item, values=[self.value_text.get('value'),self.value_text.get('info')])                 
                self.recipe[self.ancestor_text][self.parent_text][self.item_text]=self.value_text
                
                self.recipe_filter()
                self.recipe_identifier()
                self.recipe_changed()
                self.table_construct()
                self.file_update(self)  
                
                self.consolemessage(message="update: recipe " + str(self.ancestor_text) + "\\" +
                                str(self.parent_text)    + "\\" +
                                str(self.item_text) + "=" + 
                                str(self.value_text['value']), parent=self.recipetree) 


    def recipe_msgselect(self):
        
        self.value_text=self.recipe[self.ancestor_text][self.parent_text][self.item_text]
        
        

        if isinstance(self.value_text.get('value'),str):

            value = sd.askstring(
                        str(self.ancestor_text) +": " + 
                        str(self.parent_text),"Item: " + 
                        str(self.item_text) + ".\nEnter new string:", 
                        parent=self.recipetree, initialvalue=(self.value_text.get('value')))
  
        else:
            value = sd.askfloat(
                        str(self.ancestor_text) + ": " + 
                        str(self.parent_text),"Item: " + 
                        str(self.item_text)+ ".\nEnter new value:", 
                        parent=self.recipetree, initialvalue=(self.value_text.get('value')))
            
            if  value%1==0:
                #print("integer")
                value=int(value)
        
        return value
        
    
    def recipe_changed(self):
         
        if self.recipelabel.cget("text")[-1]!="*":
            self.recipelabel.config(text=self.recipelabel.cget("text") + "*")
        
        self.consolemessage("recipe: changed") 
 

    def file_settings(self):
        
        filt=self.recipe['Browser']['file']['filter']['value']      
        self.filefilter = filt.split('%')
        self.active =self.recipe['Browser']['file']['active']['value']             
        self.directories=self.recipe['Browser']['file']['directories']['value']    

        
    def file_open(self):
        
        self.file_settings()
        
        if self.active==0:
        
            self.file = fd.askopenfilenames(parent=self, title='Open Images', filetypes=[
                        ("COMBI (*.xlsx *.xls, *.txt, *.csv)", ".xlsx" ),
                        ("COMBI (*.xlsx *.xls, *.txt, *.csv)", ".xls" ),
                        ("COMBI (*.xlsx *.xls, *.txt, *.csv)", ".txt" ),
                        ("COMBI (*.xlsx *.xls, *.txt, *.csv)", ".csv" ),
                        ("COMBI (*.xlsx *.xls, *.txt, *.csv)", ".datafile" ),
                        ("TXT (*.txt)", ".txt"),("CSV (*.csv)", ".csv"),
                        ("EXCEL (*.xlsx *.xls,*.xlsm)", ".xlsx"),
                        ("EXCEL (*.xlsx *.xls,*.xlsm)", ".xlsm"),
                        ("EXCEL (*.xlsx *.xls,*.xlsm)", ".xls"),
                        ("ALL FILES", ".*")])
        
        else:

            self.filedialog=fileselect(self.master, self.selectfiles, self.directories, self.filefilter)        
            self.file=self.filedialog.show()
            self.filedialog
        
        self.files=self.file[::-1]  
    
        self.pathbox.delete(*self.pathbox.get_children())
        
        # add data to the treeview
        for file in self.files[::-1]:
            filename=os.path.basename(file)
            
            extension=os.path.splitext(filename)[1]
            
            if extension==".xls" or extension==".xlsx":
                self.pathbox.insert('', tk.END, iid=file, text=filename,  values=[filename,file,0])              
            else:
                self.pathbox.insert('', tk.END, iid=file, text=filename,  values=[filename,file,1])    
    
            self.pathlabel.config(text=file)
            
            self.path=file
        
        self.file_update(self)


    def file_selected(self):
        
        curItem=self.pathbox.focus()
        item=self.pathbox.item(curItem)['values']  
        self.sheet=0
        
        if item=="":

            self.table_construct()
            self.consolemessage("data: none selected")   
 
            result=False
        else:
            self.path=item[1]
            self.sheet=item[2]
            self.filename=os.path.basename(self.path)  
            self.consolemessage("file: " + str(self.filename) + ", sheet: " + str(self.sheet)) 

            self.pathlabel.config(text=str(item[1]))           
            result=True
        return result
            
    def file_update(self,event):
        
        if self.file_selected():

            try:
                
                extension=os.path.splitext(self.path)[1]
                    
                if extension.find("xls")>0:
    
                    self.table_xlsimport()
    
                else:
      
                    self.table_txtimport()
                
                self.table_redraw()
                
            except BaseException as error:

                self.sheet=0  
                self.table_error(str(error))
            
            return False

    def table_errmessage(self, err):
    
        data= [  ['File:', str(self.filename)]
                ,['Error:', err]
                ,['Failure:', 'Check console messages']
                ,['Check:', 'TXT: Delimiter like tab, \\t']
                ,['Check:', 'XLS: column name, \'A\', \'B\'...' ]
                ,['Check:', 'Header names']                
                ,['Check:', 'Search string: start, end, header']
                ,['Check:', 'Filter settings: disable or change limits']
                ,['Hint:', 'Set <delimiter>: none']
                ,['Hint:', 'Disable <search> set to: none or empty']
                ,['Hint:', 'Enable or Disable: header, Start and End Data']
                ,['Hint:', 'Check offset from searched text.']]
     
        return data              


    def table_error(self,error_string):
        
        #self.table_construct()            
        self.consolemessage("error: " + error_string)         
        self.df = pd.DataFrame(self.table_errmessage(error_string), columns = ['item', 'Message'])
        self.table.columncolors['item'] = 'salmon'
        self.table.columnformats['alignment']['item']='e'                    
        self.table_redraw()    


    def table_filtersetting(self, n):

        self.batchfilteractive=self.recipe['Filter']['filter ' + str(n) ]['active']['value']        
        self.batchfiltercolumn=int(self.recipe['Filter']['filter ' + str(n)]['column']['value'])
        self.batchfiltermin=self.recipe['Filter']['filter ' + str(n)]['minimum']['value']
        self.batchfiltermax=self.recipe['Filter']['filter ' + str(n)]['maximum']['value']


    def table_filter(self):
        
        filtercount=self.recipe['Filter']['create']['count']['value']
        
        for n in range(filtercount):
        
            self.table_filtersetting(n+1)
            self.table_filter_set()     
        
    
    def table_filter_set(self):
        
        if self.batchfilteractive==1:

            if (self.batchfiltercolumn<=0) or len(self.df.columns)<=(self.batchfiltercolumn-1):
                filtercol=self.df.columns[1]
            else:
                filtercol=self.df.columns[self.batchfiltercolumn-1]
            
            if is_numeric_dtype(self.df[filtercol]):
            
                mask = (self.df[filtercol] >= (self.batchfiltermin)) & (self.df[filtercol] <= (self.batchfiltermax))
                self.df=self.df.loc[mask]
                
                if self.df.size==0:
                    raise (Exception)('No data, check filter settings, ' + filtercol + ", between: " +  str(self.batchfiltermin) + " and " + str(self.batchfiltermax))
                    self.consolemessage("filter: no data, " + filtercol + " between: " +  str(self.df.size))
                else:
                    self.consolemessage("filter: enabled, " + filtercol + " between: " +  str(self.batchfiltermin) + " and " + str(self.batchfiltermax) + ' (marked yellow)') 
                    self.table.columncolors[filtercol] = 'beige' 
                
            else:
                raise (Exception)('No data, no numeric column, ' + filtercol + ", between: " +  str(self.batchfiltermin) + " and " + str(self.batchfiltermax))
                self.consolemessage("filter: no numeric column, " + filtercol + " between: " +  str(self.df.size))                
       
        
    def table_groupcolor(self):
        
        self.batch_setting()
        
        if self.batchstats==1:
            for group in self.groupcols:
                self.table.columncolors[self.df.columns[group-1]] = 'lightsteelblue'  
            self.consolemessage("grouping: enabled for, " + repr(self.groupcols) + ' (marked blue)') 
    
    
    def table_identifiercolor(self):
        
        i=0
        for identifier in self.identifierarray:
            if identifier==1:
                self.table.columncolors[self.df.columns[i]] = 'lightgray'  
                i+=1        
    

    def table_grouping(self):    
        
        data= self.df.select_dtypes(include='number')        
        
        grouparray=[]
        sortarray=[]
        for groupcol in self.groupcols:
            grouparray.append(self.df.iloc[:,int(groupcol-1)]) 

        group = self.df.groupby(grouparray)  
        
        f={}
        for col in self.df.columns:
            if col in data.columns:
                f[col]=['mean'] #number column
                
            else:
                f[col]=['first'] #text column
                
        data=group.agg(f)
        data.columns = data.columns.map('{0[0]}'.format)       
        self.df=data 
        
        self.consolemessage("grouping: initial enabled, meanvalues from every datafile/sheet") 
        
      
    def table_redraw(self):
        
        self.table_identifiersetting()

        if not self.sheet==0:  
            self.table.columncolors.clear()
            self.table_filter() 
            
            self.table_identifiercolor()
            
            if self.statsinitial==1:
                self.table_groupitems()
                self.table_grouping()
                
            if self.statsactive==1:
                self.table_groupitems()
                self.table_groupcolor()        

        self.table.rowselectedcolor=None
        self.table.highlighted=None        

        self.table.updateModel(TableModel(self.df))         
        self.table.redraw()        

        
    def table_construct(self):      

        self.sheet=0
        self.df= pd.DataFrame([['','','']], columns = ['a','b','c'])
        self.table.updateModel(TableModel(self.df))
        self.table=Table(self.tableframe,enable_menus=False, showtoolbar=False, showstatusbar=True)
        self.table.show()
        self.table_redraw()

        
    def table_setheader(self,header):
        #header size df columns
        header=np.resize(header,len(self.df.columns))
    
        self.df.columns=header            
        cols=pd.Series(self.df.columns)

        #rename duplicate names.
        for dup in cols[cols.duplicated()].unique(): 
            cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]   
            
        self.df.columns=cols   


    def table_identifiersetting(self):
        
        self.identifierfile=self.recipe['ID File']['file']['active']['value']
        self.identifieridorder=self.recipe['ID File']['id']['order']['value']         
        self.identifierid=self.recipe['ID File']['id']['active']['value']
        
        IDgroup=self.recipe['ID File']['id']['select']['value']     
        self.identifieridselect = [(int(y) if y.strip() else None) for y in IDgroup.split(',')]
   
        customnum=self.recipe['ID Custom']['create']['count']['value']
        self.identifierarray=[self.identifierfile, self.identifierid]
        
        for i in range(customnum):
            active=self.recipe['ID Custom']['custom ' + str(i+1)]['active']['value']   
            self.identifierarray.append(active)                            
   
        self.statsactive=self.recipe['Output']['statistics']['total']['value']
        self.statsinitial=self.recipe['Output']['statistics']['initial']['value']
        
    
    def table_groupitems(self):
        
        try: 
        
            IDgroup=self.recipe['Output']['statistics']['groupby']['value'] 
            self.groupcols = [(int(y) if y.strip() else None) for y in IDgroup.split(',')]          
            self.groupcols  = np.where(self.groupcols==0, 1, self.groupcols )
            self.groupcols  = np.where(self.groupcols==None, 1, self.groupcols )
            
        except BaseException as error:
            raise BaseException('Group failure: [Output][statistics][groupby]=' + str(IDgroup))   
        
        if np.max(self.groupcols)>len(self.df.columns):
            raise BaseException('Group max column: [Output][statistics][groupby]=' + str(IDgroup) + ", max col dataset: " + str(len(self.df.columns)  ) )  
        
        
    def table_identifiers(self):

        #self.table_identifiersetting()
        self.table_setheader(self.header) 

        n=0
        for i, custom in enumerate((self.identifierarray[2:])):
   
            if custom==1:
                
                customcolumn=int(self.recipe['ID Custom']['custom ' + str(i+1)]['column']['value']+n-1)
                
                if (customcolumn<=-1) or (len(self.df.columns)<=(customcolumn)):
                    #self.customcolumn=0
                    self.df.reset_index()
                    customcol=self.df.index
                    customname='ID) Index'
                  
                else:
                    customcol=self.df.iloc[:,customcolumn]
                    customname='ID) ' + str(self.df.columns[customcolumn])
                    
                self.consolemessage("identifier: " + str(customname) + " set (marked gray)")    

                self.header.insert(n, customname)
                self.df.insert(loc=n, column='tempname_'+str(i), value=customcol)
                self.table_setheader(self.header)                 
                
                n+=1
                               
                if not self.df[customname].dtype == object:
                    decimals=self.recipe['ID Custom']['custom ' + str(i+1)]['decimals']['value'] 
                    self.df[customname] = self.df[customname].round(decimals=int(decimals))    

                self.table_setheader(self.header) 
            
        if self.identifierarray[1]==1:
            self.table_ID()  
            self.df.insert(loc=0, column='tempname_'+str(n), value=self.ID)
            self.header.insert(0,'ID) file-ID')
            self.consolemessage("identifier: ID set (marked gray)")  
            self.table_setheader(self.header) 
            n+=1
            
        if self.identifierarray[0]==1:
        
            self.df.insert(loc=0, column='tempname_'+str(n), value=self.filename)
            self.header.insert(0,'ID) File')
            self.consolemessage("identifier: File set (marked gray)")    
            self.table_setheader(self.header) 

    
    def table_ID(self):
          
        num_str = ""
        j=0
        for i, char in enumerate(self.filename):
            if char.isdigit():
                if (i-j)==1:
                    num_str = num_str  + char
                else:
                    num_str = num_str +"_" + char       
                j=i
        
        arr_str=num_str.split("_")      
        self.arr_num = list(map(int, arr_str[1:]))
        
        self.ID=''
        
        for n in self.identifieridselect:
            self.ID= self.ID +'_' + str(self.table_ID_form(n) )
        
        self.ID=self.ID[1:]
        self.consolemessage("ID: " + str(self.ID))
 
    
    def table_ID_form(self, n):
        
        if (len(self.arr_num)-n)>=0:
            if self.identifieridorder.lower()=="left": 
                ID=self.arr_num[n-1]
            else:
                ID=self.arr_num[-n]
        else:
            ID=0      
        return ID


    def table_txtimport(self):
        #Open file TXT and set Table     
        self.f=data_txt(self.recipe)
        self.f.data_open(self.path)   
        
        self.table_txtdelimiter()
        self.table_txtstartend()
        self.table_txtsetdata()
        
        self.table_identifiers()


    def table_txtdelimiter(self):
        self.seperator=self.recipe['Import (text)']['general']['delimiter']['value'] 
        self.seperator=self.seperator.replace("\\t","\t")
        
        self.decimal=self.recipe['Import (text)']['general']['decimal']['value'] 
        self.thousants=self.recipe['Import (text)']['general']['thousants']['value']     


    def table_txtsetdata(self):
        self.df=pd.read_csv(self.path, delimiter=self.seperator, decimal=self.decimal, thousands=self.thousants, 
                               skiprows=self.start,nrows=self.end-self.start+1, header=None, encoding="unicode_escape")
        
        
    def table_txtstartend(self):
        
        readfile=self.f.data_start()
        self.start=readfile[0]
        self.consolemessage("start row: " + str(readfile[0]) + 
                            ", found: " + str(readfile[2]) + 
                            ", " + str(readfile[3]))                

        readfile=self.f.data_end()
        self.end=readfile[0]            
        self.consolemessage("end row: " + str(readfile[0]) + 
                            ", found: " + str(readfile[2]) + 
                            ", " + str(readfile[3]))      
  
        readfile=self.f.data_header()                            
        self.header=readfile[1]
        self.consolemessage("header: " + str(readfile[0]) + 
                            ", found: " + str(readfile[2]) + 
                            ", " + str(readfile[3]))   


    def table_xlsmessage(self):

        data=[['Filename:', str(self.filename)]]
        
        for i, sheet in enumerate(self.sheets):
               data=np.append(data,[['Sheet:'+ str(i+1), sheet ]],axis=0)
 
        self.df= pd.DataFrame(data, columns = ['item','name'])
        self.table.columnformats['alignment']['item']='e'
        self.table.columncolors['item'] = 'lightgreen'
        self.table_redraw()


    def table_xlssheet(self):

        if self.sheet==0:
            self.table_xlsdelchild()           
            
            for sheet in self.sheets:

                self.pathbox.insert(self.path, tk.END,text=sheet,values=[self.filename, self.path,sheet], open=True)  

            #expand tree
            self.pathbox.item(self.path, open=True) 
        

    def table_xlsdelchild(self):
       
       item = self.pathbox.selection()[0]
       parent =self.pathbox.parent(item)
       children = self.pathbox.get_children(item)
       
       for child in children:
           self.pathbox.delete(child)

           
    def table_xlsimport(self):
        #Open file XLS and XLSX and set Table          
        if self.sheet==0:
            self.consolemessage("search xls: open excel" )    
            
            self.f=data_xls(self.recipe)
            self.f.data_open(self.path)          
            self.consolemessage("search xls: finished open, start count" )  
            
            self.sheets=self.f.data_sheets()
            self.consolemessage("search xls: counted sheets" )  
            self.table_xlssheet()
            self.f.data_close()
            
            self.table_xlsmessage()
        
        else:
            self.consolemessage("search xls: open excel" )                

            self.f=data_xls(self.recipe)
            self.f.data_open(self.path)  
            self.f.data_sheet(self.sheet)
            self.consolemessage("search xls: finished open" )  
           
            self.table_xlsstartend()
            self.table_xlssetdata()
            
            self.table_identifiers()
            self.f.data_close()
  
    
    def table_xlsstartend(self):
        
        #https://pythonbasics.org/read-excel/
        readfile=self.f.data_start()
        self.start=readfile[0]
        self.consolemessage("start row: " + str(readfile[0]) + 
                            ", found: " + str(readfile[2]) + 
                            ", " + str(readfile[3]))                

        readfile=self.f.data_end()
        self.end=readfile[0]            
        self.consolemessage("end row: " + str(readfile[0]) + 
                            ", found: " + str(readfile[2]) + 
                            ", " + str(readfile[3]))      
  
        readfile=self.f.data_header()                            
        self.header=readfile[1]
        self.consolemessage("header: " + str(readfile[0]) + 
                            ", found: " + str(readfile[2]) + 
                            ", " + str(readfile[3])) 

    def table_xlsrecipe(self):
        
        self.usecols=self.recipe['Import (excel)']['general']['usecols']['value']
        
        if self.usecols.lower()=='none':
            self.usecols=None
        
    def table_xlssetdata(self):
        
        self.table_xlsrecipe()
        
        self.df=pd.read_excel(self.path, sheet_name=self.sheet, skiprows=self.start,nrows=self.end-self.start+1, header=None, usecols=self.usecols)        
        self.consolemessage("dataframe: loaded") 
        
        
    def batch(self):
        
        self.batch_setting()
        
        showinfo(title="Information", message="Select output (save) directory.", parent=self.master)
        
        #os.path.dirname(self.path)
        #inidir=os.path.abspath(os.path.join(self.path, '..'))
        inidir=Path(self.path).parents[0]

        self.savedir= fd.askdirectory(parent=self.console, initialdir=inidir)
        
        if self.savedir==None or len(self.savedir)==0:
            self.consolemessage("batch: cancelled no directory selected" )
        
        else:
            self.consolemessage("destination: " + str(self.savedir) )       
            self.pbar=progress(self.master)

            self.batch_loopfiles()

            self.batch_savexls()
            
            self.pbar.progress_exit()


    def batch_loopfiles(self):
        
        self.df_col={}
        self.df_list={}
        self.df_column={}
        self.df_concat={}
        self.df_count=0
        
        items=len(self.pathbox.get_children())
        
        self.pbar.progress_update(0, 'Start',True)
        
        for i, children in enumerate(self.pathbox.get_children()):
            
            #for child in parent:
            self.consolemessage(str(children))
            self.pathbox.focus(children)
            self.pathbox.selection_set(children)  
            self.pathbox.see(children)              
     
            self.update()
            
            self.consolemessage("batch: " + str(self.filename))
            
            if not self.sheet==0:
                self.batch_dataframes()
            
            text="batch: " + str(self.filename) + ", sheet: " +  str(self.sheet) + ", Status: " + str(i+1) + "/" + str(items)
            self.pbar.progress_update(100*(1+i)/items, text,  True)
    
            child=self.pathbox.get_children(children)
            for c in child:
       
                self.pathbox.focus(c)
                self.pathbox.selection_set(c)                
                self.pathbox.see(c) 
                self.update()
                
                self.consolemessage("batch: " + str(self.filename + ", sheet: " +  str(self.sheet)))
  
                if not self.sheet==0:
                    self.batch_dataframes()
 
    
    def batch_xlsfilename(self, name):                
        
        dt=datetime.now() 
        sdt=dt.strftime("%y%m%d-%H%M%S")
        
        if self.identifierid==1:
            minID=self.df_list['ID) file-ID'].min()
            maxID=self.df_list['ID) file-ID'].max()

            filename=str(sdt)+ "_"  + minID[:10] + "-" +  maxID[:10] +  "_" + str(self.recipename) + "_"  +  str(name)+ ".xlsx"
            
        else:
            
            filename=str(sdt)+ "_" + str(self.recipename) + "-"  +  str(name)+ ".xlsx"
            
        self.xlsname = "".join(i for i in filename if i not in '<>:"/\|?*')
        self.xlsfilepath=os.path.join(self.savedir,filename) 
  

    def batch_savexls(self):
        
        items=len(self.df_list.items())
        i=0
        
        self.pbar.progress_update(2, "Creating excel XLSX", True)
          
        for name, self.df_list in self.df_list.items():

            self.batch_xlsfilename(name)
                      
            self.writer = pd.ExcelWriter(self.xlsfilepath, engine='openpyxl')  
            

            self.pbar.progress_update(5, "File Created: " + self.xlsname , True)
            
            if self.rowdata==1:
  
                self.df_list.to_excel(self.writer, sheet_name='Data_Rows', index=False)
  
                text="Saving excel XLSX, " + str(name)+".xlsx, Status: " + str(i+1) + "/" + str(items)
                self.consolemessage("saving: " + str(name)+".xlsx, Status: " + str(i+1) + "/" + str(items))
                self.pbar.progress_update(95*(i+1)/items, text, True)           
  
            
            if self.columndata==1:
                
                self.df_column[name].to_excel(self.writer, sheet_name='Data_Columns', index=False)
    
                text="Saving excel XLSX, " + str(name)+".xlsx, Status: " + str(i+1) + "/" + str(items)
                self.consolemessage("saving: " + str(name)+".xlsx, Status: " + str(i+1) + "/" + str(items))
                self.pbar.progress_update(95*(i+1)/items, text, True)           
  
    
            if self.batchstats==1:

                self.batch_stats()
            
            text="Finishing, closing excel XLSX: " + str(name)+".xlsx, Status: " + str(i+1) + "/" + str(items)
            self.consolemessage("finishing: " + str(name)+".xlsx, Status: " + str(i+1) + "/" + str(items))
            self.pbar.progress_update(95*(i+1)/items, text, True) 
            self.writer.close()      
   
            i+=1         
   
        text="Finished"
        self.pbar.progress_update(100*(i+1)/items, text, True)              

  
    def batch_stats(self):
        
        def percentile(n):
            def percentile_(x):
                return np.percentile(x, n)
            percentile_.__name__ = 'PCTL(%s%%)' % n
            return percentile_

        def CI_LB():
            def CI_LB_(x):
                n=np.size(x)
                q=0.5
                z=1.96
                lb=(n*q-z*np.sqrt(n*q*(1-q)))/n
                if lb>1: lb=1
                if lb<0: lb=0
                return np.percentile(x, 100*lb)
            CI_LB_.__name__ = 'PCTL_LB(CI 95%)' 
            return CI_LB_

        def CI_UB():
            def CI_UB_(x):
                n=np.size(x)
                q=0.5
                z=1.96
                ub=(n*q+z*np.sqrt(n*q*(1-q)))/n
                if ub>1: ub=1
                if ub<0: ub=0
                return np.percentile(x, 100*ub)
            CI_UB_.__name__ = 'PCTL_UB(CI 95%)' 
            return CI_UB_
        
        def sheetrename(name):
            #validate to excel sheetname
            for char in ['?','\\','/','*','[',']',':']:
                name=name.replace(char,'')
                
            return name[:30]
        
        #Selects columns with data
        data= self.df_list.select_dtypes(include='number')  

        if data.size>0:

            f={}
            n=0
            cols=len(data.columns)
            
            
            for col in data.columns:
                
                text="Saving excel XLSX, stats column, " + str(col) + ", Status: " + str(n+1) + "/" + str(cols)
                self.consolemessage("saving: column: " + str(col) + ", status: " + str(n+1) + "/" + str(cols))                
                self.pbar.progress_update(100*(n+1)/cols, text, True) 
                
                f[col]=['count', np.mean, np.std, 'min', 'max', np.median, percentile(5), percentile(25), percentile(50), percentile(75), percentile(95), CI_LB(), CI_UB()]

                
                grouparray=[]
                sortarray=[]
                for groupcol in self.groupcols:
                    grouparray.append(self.df_list.iloc[:,int(groupcol-1)]) 
                    
                group = self.df_list.groupby(grouparray)   
                stats=group.agg(f)
                #self.consolemessage("grouping: " + repr(grouparray))   

                
                self.df_list.index
         
                stats.columns = stats.columns.map('{0[0]} {0[1]}'.format)
                
                sortarray=[]
              
                for groupcol in self.groupcols[::-1]:                
                    colname=self.df_list.columns[int(groupcol-1)]
                    sortarray.append(colname)
                    groupcol=group.agg({colname : 'first'})[colname]
                    stats.insert(loc=0, column=colname, value=groupcol)
   
                stats = stats.reset_index(drop=True)                
                stats.sort_values(by=sortarray[::-1], inplace=True)
                stats = stats.reset_index(drop=True)
                
                sheetname=col + '_stats'
                sheetname=sheetrename(sheetname)

                stats.to_excel(self.writer, sheet_name=sheetname, index=False)

                n+=1
                f={}
    
                
    def batch_setting(self):
        
        self.rowdata=self.recipe['Output']['total']['rows']['value']
        self.columndata=self.recipe['Output']['total']['columnar']['value']       
        self.batchstats=self.recipe['Output']['statistics']['total']['value']
        
  
    def batch_dataframes(self):
        
        df_exist=False
        
        if self.sheet==1:
            df_name= str("%03d" % (self.df_count)) 
        else:
            df_name= str("%03d" % (self.df_count))  + "_"  + str(self.sheet )
    
    
        for name, df_col in self.df_col.items():

            if np.array_equal(df_col,self.df.columns.values):
                df_exist=True
                break#else:
        
        if not df_exist:
                
            self.df_col[df_name]=self.df.columns.values
            self.df_list[df_name]=self.df
            self.df_count+=1
            self.df_column[df_name]=self.df

        else:
            
            self.df_list[name]= pd.concat([self.df_list[name], self.df], axis=0)
            
            if self.columndata==1:
                if len(self.df_column[name].columns)<15000:
                    
                    self.df.reset_index(drop=True, inplace=True)
                    self.df_column[name].reset_index(drop=True, inplace=True)                    
                    self.df_column[name]  = pd.concat([self.df_column[name], self.df], axis=1)


def quit():
 
    if app.recipelabel.cget("text")[-1]=="*":
        if askokcancel(title="Quit", message="Recipe changed, close without saving?" ):
            root.destroy()
    else:
        root.destroy()

try:
    import pyi_splash
    pyi_splash.update_text('Datacombiner Loaded ...')
    pyi_splash.close()
except:
    pass 


root = tk.Tk()  # Creates a master
root.geometry('1440x810') # set initial size
root.title('Data Combiner')
root.minsize(1440,810)
root.protocol("WM_DELETE_WINDOW", quit)    

root.iconbitmap(default='Settings/ICON small.ico')

#root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file='Settings/ICON small.png'))




app = MainApp(root) # Initializes app using root as master

root.mainloop() # Runs window




#https://stackoverflow.com/questions/47240509/python-how-to-tokenize-from-file
