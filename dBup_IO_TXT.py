# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 09:45:56 2021

@author: vpreemen
"""
import yaml
#from pandastable import Table, TableModel
#import pandas as pd



class recipe:
    
    #class Yaml_Recipe:
    def read_recipe(path):
        #load recipe
        with open(path) as file:
            doc = yaml.full_load(file)
        return doc
    
    def write_recipe(path, dict_file):
        with open(path, 'w') as file:
            documents = yaml.dump(dict_file, file, sort_keys=False)
        
    

class data_txt:

    def __init__(self, recipe):
        #self.test=recipe['TXT_import'][section][]
        
        self.recipe=recipe
        
        self.seperator=recipe['Import (text)']['general']['delimiter']['value'] 
        
        self.datasize=0
     
        
    def data_format(self,section):
        
        self.active=self.recipe['Import (text)'][section]['active']['value']
        self.search=self.recipe['Import (text)'][section]['search']['value']
        self.offset=self.recipe['Import (text)'][section]['offset']['value']
        self.location=self.recipe['Import (text)'][section]['location']['value']
        self.rows=self.recipe['Import (text)'][section]['rows']['value']
        self.order=self.recipe['Import (text)'][section]['order']['value'] 
 
    def data_open(self,path):
        with open(path) as temp_f:
           self.datafile = temp_f.readlines()        
   
        temp_f.close()
        

            
       

    def data_search(self):

       self.datasize=self.offset + self.rows
        
       if self.datasize>=len(self.datafile):
          self.datasize=len(self.datafile)
        
       if self.location=="top":
           
           self.data=self.datafile[0:self.datasize]         
           n=self.data_find()[0]  
           data=self.data[n]
                
       else:
           self.data=self.datafile[len(self.datafile)-self.datasize:]
                               
           n=self.data_find()[0]
           data=self.data[n]
           #n=n+len(self.datafile)-self.rows
         
       data=self.data_array(data)  
       #print(data)

       return [n,data,self.search,self.data_find()[1]]


    def data_find(self):
        for i, line in enumerate(self.data[::self.order]):
        
            if self.search in line:

                if self.order==1:
                    n=i
                else:
                    n=self.datasize-i-1
                
                result=[n+self.offset, True] # The string is found
                break
            else:
                result=[i,False]
      
        return result
 
    def data_header(self):
     
        self.data_format("header") 
 
        if self.active==1:
            if self.search.lower()=='none' or len(self.search)==0:
                n=self.offset
                data=self.datafile[n]
                data=self.data_array(data)  
                result=[n,data,'',True]
                                
            else:    
                result=self.data_search()
 
        else:
                result=[0,['Column'],'',False]        
             
        return result             

    def data_start(self):
     
        self.data_format("start data") 

 
        if self.active==1:
            if self.search.lower()=='none' or len(self.search)==0:
                n=self.offset
                data=self.datafile[n]
                data=self.data_array(data)  
                result=[n,data,'',True]
                           
            else:    
                result=self.data_search()
 
        else:
                result=[1,[''],'',False]        
             
        return result  

    def data_end(self):
     
        self.data_format("end data") 
 
        if self.active==1:
            if self.search.lower()=='none' or len(self.search)==0:
                n=self.offset
                data=self.datafile[n]
                data=self.data_array(data)  
                result=[n,data,'',True]
                                
            else:    
                result=self.data_search()
 
        else:
                result=[len(self.datafile),[''],'',False]        
             
        return result  

        
    def data_row(self,n):
        
           
        data=self.data[n]
        
        
        return data
    
    def data_array(self,header):            
        seperator=(self.seperator)
        #remove carage return and set define tab symbol
        header = header.replace("\n","") 
        header = header.split(seperator.replace("\\t","\t"))
         
        return header


