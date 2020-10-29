import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import *
import sqlite3
from tkinter import messagebox

# Region 1 Start(Window Settings)
window = Tk()
window.title("Text Analyzer")

w = window.winfo_reqwidth()
h = window.winfo_reqheight()
ws = window.winfo_screenwidth()
hs = window.winfo_screenheight()
x = (ws/4) - (w/4)
y = (hs/4) - (h/4)
window.geometry('+%d+%d' % (x, y))

window.config(background='black')

style = ttk.Style(window)
style.configure('lefttab.TNotebook', tabposition='wn',)

tab_control = ttk.Notebook(window, style='lefttab.TNotebook')

tab1 = ttk.Frame(tab_control, height=100)
tab2 = ttk.Frame(tab_control, height=100)
tab3 = ttk.Frame(tab_control, height=100)
tab5 = ttk.Frame(tab_control, height=100)

# ADD TABS TO NOTEBOOK
tab_control.add(tab2, text=f'{"TextRank Algorithm":^20s}')
tab_control.add(tab5, text=f'{"About ":^30s}')

label2 = Label(tab2, text='TextRank Algorithm', padx=5, pady=5)
label2.grid(column=1, row=0)

label4 = Label(tab5, text='About', padx=5, pady=5)
label4.grid(column=0, row=0)

tab_control.pack(expand=1, fill='both')
# Region 1 End(Window Settings)

def deEmojify(inputString):
    return inputString.encode('ascii', 'ignore').decode('ascii')


def summarize():
	text = str(displayed_file.get('1.0',tk.END))
	if text == '\n':
		messagebox.showinfo("Error", "Input field cannot be empty")
	else:
		tab2_display_text.insert(INSERT, Summarizer.summarize(text, ratio=0.4, words=500))

# Clear entry widget

# Clear Text  with position 1.0
def clear_text_file():
	displayed_file.delete('1.0',END)

# Clear Result of Functions
def clear_text_result():
	tab2_display_text.delete('1.0',END)

#TextRank tab
l1=Label(tab2,text="Enter text to summarize")
l1.grid(row=1,column=1)

displayed_file = ScrolledText(tab2,height=7)# Initial was Text(tab2)
displayed_file.grid(row=2,column=0, columnspan=3,padx=5,pady=3)

# BUTTONS FOR SECOND TAB/FILE READING TAB

b2=Button(tab2,text="Summarize ", width=12,command=summarize,bg='#03A9F4',fg='#fff')
b2.grid(row=3,column=0,padx=10,pady=10)

b1=Button(tab2,text="Clear ", width=12,command=clear_text_file,bg='#03A9F4',fg='#fff')
b1.grid(row=3,column=1,padx=10,pady=10)

b3=Button(tab2,text="Clear Result", width=12,command=clear_text_result, bg='#03A9F4',fg='#fff')
b3.grid(row=5,column=1,padx=10,pady=10)

# Display Screen
# tab2_display_text = Text(tab2)
tab2_display_text = ScrolledText(tab2,height=10)
tab2_display_text.grid(row=7,column=0, columnspan=3,padx=5,pady=5)

# Allows you to edit
tab2_display_text.config(state=NORMAL)

window.mainloop()