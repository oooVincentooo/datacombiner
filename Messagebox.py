from tkinter import *

class GUI(Tk):
    def __init__(self):
        super().__init__()
        self.geometry('600x400')
        self.sum_var= StringVar()
        Label(self, text="Main window").pack()
        Button(self, text="To enter Data", command=self.entry_Fn).pack()
        sum = Label(self, textvariable=self.sum_var)
        sum.pack()

    def entry_Fn(self):
        self.level_1 = Toplevel(self)
        Label(self.level_1, text = "level one").pack()
        self.entry_1 = Entry(self.level_1)
        self.entry_1.pack()
        self.entry_2 = Entry(self.level_1)
        self.entry_2.pack()
        Button(self.level_1, text="submit", command=self.submitBtn).pack()

    def submitBtn(self):
        val_1 = self.entry_1.get()
        val_2 = self.entry_2.get()
        self.sum_var.set(int(val_1)+ int(val_2))
        self.level_1.destroy()

root = GUI()

root.mainloop()