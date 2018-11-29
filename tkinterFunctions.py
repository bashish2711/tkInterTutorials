import tkinter as tk
from tkinter import *
from math import *


class Checkbar(Frame):
	def __init__(self, parent=None, picks=[], side=LEFT, anchor=W):
		Frame.__init__(self, parent)
		self.vars = []
		for pick in picks:
			var = IntVar()
			chk = Checkbutton(self, text=pick, variable=var)
			chk.pack(side=side, anchor=anchor, expand=YES)
			self.vars.append(var)
	def state(self):
		return map((lambda var: var.get()), self.vars)



class Widget(Frame):
	def __init__(self, parent=None, side=LEFT, anchor=W):
		Frame.__init__(self, parent)

	def fetch(self,entries):
		for entry in entries:
			field = entry[0]
			text  = entry[1].get()
			print('%s: "%s"' % (field, text)) 

	def makeform(self, fields=[]):
		entries = []
		for field in fields:
			row = Frame(root)
			lab = Label(row, width=15, text=field, anchor='w')
			ent = Entry(row)
			row.pack(side=TOP, fill=X, padx=5, pady=5)
			lab.pack(side=LEFT)
			ent.pack(side=RIGHT, expand=YES, fill=X)
			entries.append((field, ent))
		return entries

	def monthly_payment(self,entries):
		# period rate:
		r = (float(entries['Annual Rate'].get()) / 100) / 12
		print("r", r)
		# principal loan:
		loan = float(entries['Loan Principle'].get())
		n =  float(entries['Number of Payments'].get())
		remaining_loan = float(entries['Remaining Loan'].get())
		q = (1 + r)** n
		# monthly = r * ( (q * loan - remaining_loan) / ( q - 1 ))
		monthly = r * ( (q * loan - remaining_loan) / ( q ))
		monthly = ("%8.2f" % monthly).strip()
		entries['Monthly Payment'].delete(0,END)
		entries['Monthly Payment'].insert(0, monthly )
		print("Monthly Payment: %f" % float(monthly))

	def final_balance(self,entries):
		# period rate:
		r = (float(entries['Annual Rate'].get()) / 100) / 12
		print("r", r)
		# principal loan:
		loan = float(entries['Loan Principle'].get())
		n =  float(entries['Number of Payments'].get()) 
		q = (1 + r)** n
		monthly = float(entries['Monthly Payment'].get())
		q = (1 + r)** n
		remaining = q * loan  - ( (q - 1) / r) * monthly
		remaining = ("%8.2f" % remaining).strip()
		entries['Remaining Loan'].delete(0,END)
		entries['Remaining Loan'].insert(0, remaining )
		print("Remaining Loan: %f" % float(remaining))

	def makeformForSheet(self, fields):
		entries = {}
		for field in fields:
			row = Frame(root)
			lab = Label(row, width=22, text=field+": ", anchor='w')
			ent = Entry(row)
			ent.insert(0,"0")
			row.pack(side=TOP, fill=X, padx=5, pady=5)
			lab.pack(side=LEFT)
			ent.pack(side=RIGHT, expand=YES, fill=X)
			entries[field] = ent
		return entries

if __name__ == '__main__':     
	root = tk.Tk()
	logo = tk.PhotoImage(file="python_logo_small.gif")
	explanation = """At present, only GIF and PPM/PGM
	formats are supported, but an interface 
	exists to allow additional image file
	formats to be added easily."""

	whatever_you_do = """ Whatever you do will be insignificant, \
	but it is very important that you do it.\n\n(Mahatma Gandhi)"""

	left = "left"
	right = "right"
	center = tk.CENTER
	titleText = "Hello Ashish"
	titleText = "Done Upto Widgets"
	counter = 0

	def windowTitle():
		root.title(titleText)

	def showImageOnly(imageSide=right):
		w1 = tk.Label(root, image=logo).pack(side=imageSide)

	def showTextJustified(justifySide=right, textSide=left, text="Hi"): 
		w2 = tk.Label(root, 
		              justify=justifySide,
		              padx = 10, 
		              fg = "light green",
		              bg = "dark green",	
		              font = "Helvetica 16 bold italic",				
		              text=text).pack(side=textSide)
	# w3 = tk.Label(root, 
	#              compound = tk.CENTER,
	#              text=explanation, 
	#              image=logo).pack(side="right")
	def showJustifedTextWithImage(justifySide=left,imageSide=center, textSide=left, text="Hi", image=logo):
		w4 = tk.Label(root, 
						justify=justifySide,
						compound = imageSide,
						padx = 10, 
						text=text, 
						image=image).pack(side=textSide)

	def showDistroyButton():
		button = tk.Button(root,
						text='like !', 
						width=25, 
						command=root.destroy).pack()

	def showQuitButton():
		button = tk.Button(root, 
						text="QUIT", 
						fg="red",
						command=quit).pack(side=tk.RIGHT)

	def showSlogan():
		slogan = tk.Button(root,
						text="Hello",
						command=writeSlogan).pack(side=tk.LEFT)

	def counter_label(label):
		def count():
			global counter
			counter += 10
			label.config(text=str(counter))
			label.after(1000, count)
		count()

	def showMessage():
		msg = tk.Message(root, 
				text = whatever_you_do)
		msg.config(bg='lightgreen',
				fg='darkgreen', #foreground Text color. The default value is system specific.
				font=('times', 24, 'italic'),
				anchor = tk.NW , 	#The position: N, NE, E, SE, S, SW, W, NW, or CENTER.
				aspect = 200,		#Note that if the width is explicitly set, this option is ignored.
				borderwidth =2,		#Border width. Default value is 2. can use bd Short for borderwidth.
				#cursor =,	Defines the kind of cursor to show when the mouse is moved over the message widget. By default the standard cursor is used..
				highlightbackground = 'white', #Together with highlightcolor and highlightthickness, this option controls how to draw the highlight region.
				highlightcolor = 'blue',	#See highlightbackground.
				highlightthickness= 6,#See highlightbackground. 
				justify = center,	#Defines how to align multiple lines of text. Use LEFT, RIGHT, or CENTER. Note that to position the text inside the widget, use the anchor option. Default is LEFT.
				padx = 6,	#Horizontal padding. Default is -1 (no padding).
				pady = 2,	#Vertical padding. Default is -1 (no padding).
				relief =  tk.RAISED,#Border decoration. The default is FLAT. Other possible values are SUNKEN, RAISED, GROOVE, and RIDGE.
				#takefocus = FALSE#If true, the widget accepts input focus. The default is false.
				#textvariable 	Associates a Tkinter variable with the message, which is usually a StringVar. If the variable is changed, the message text is updated.
				#width 	Widget width given in character units. A suitable width based on the aspect setting is automatically chosen, if this option is not given. 
				)
		msg.pack()

	def writeSlogan():
	    print("Tkinter is easy to use!")

	def showRadioButton(buttonStyle="circular"):
		v = tk.IntVar()
		v.set(1)  # initializing the choice, i.e. Python

		languages = [
		    ("Python",1),
		    ("Perl",2),
		    ("Java",3),
		    ("C++",4),
		    ("C",5)
		]

		def ShowChoice():
		    print(v.get())

		tk.Label(root, 
		         text="""Choose your favourite programming language:""",
		         justify = tk.LEFT,
		         padx = 20).pack()
		if buttonStyle=="Indicator":
			for val, language in enumerate(languages):
				tk.Radiobutton(root, 
			                  text=language,
			                  indicatoron = 0,
			                  width = 20,
			                  padx = 20, 
			                  variable=v, 
			                  command=ShowChoice,
			                  value=val).pack(anchor=tk.W)
		else:
			for val, language in enumerate(languages):
			    tk.Radiobutton(root, 
			                  text=language,
			                  padx = 20, 
			                  variable=v, 
			                  command=ShowChoice,
			                  value=val).pack(anchor=tk.W)

	def showCheckBox():
		master = Tk()

		def var_states():
		   print("male: %d,\nfemale: %d" % (var1.get(), var2.get()))

		Label(master, text="Your sex:").grid(row=0, sticky=W)
		var1 = IntVar()
		Checkbutton(master, text="male", variable=var1).grid(row=1, sticky=W)
		var2 = IntVar()
		Checkbutton(master, text="female", variable=var2).grid(row=2, sticky=W)
		Button(master, text='Quit', command=master.quit).grid(row=3, sticky=W, pady=4)
		Button(master, text='Show', command=var_states).grid(row=4, sticky=W, pady=4)

	def showWidget():
		master = Tk()
		Label(master, text="First Name").grid(row=0)
		Label(master, text="Last Name").grid(row=1)

		e1 = Entry(master)
		e2 = Entry(master)

		e1.grid(row=0, column=1)
		e2.grid(row=1, column=1)

	# showImageOnly(imageSide=right)
	windowTitle()
	# showTextJustified(justifySide=center, textSide=right, text=explanation)
	# showTextJustified() # All arguments are optional
	# showJustifedTextWithImage(justifySide=center,imageSide=center, textSide=left, text=explanation, image=logo)

	# label = tk.Label(root, fg="green", font = "Helvetica 16 bold italic")
	# label.pack()
	# counter_label(label)
	# showMessage()
	# showSlogan()
	# writeSlogan()
	# showDistroyButton()

	# showRadioButton(buttonStyle = "Indicator")
	# showRadioButton()
	# showCheckBox()
	# showQuitButton()

	#Related to CheckBox ********************************************
	# lng = Checkbar(root, ['Python', 'Ruby', 'Perl', 'C++'])
	# tgl = Checkbar(root, ['English','German'])
	# lng.pack(side=TOP,  fill=X)
	# tgl.pack(side=LEFT)
	# lng.config(relief=GROOVE, bd=2)

	# def allstates(): 
	# 	print(list(lng.state()), list(tgl.state()))
	# Button(root, text='Quit', command=root.quit).pack(side=RIGHT)
	# Button(root, text='Peek', command=allstates).pack(side=RIGHT)
	# END Related to CheckBox ****************************************

	# Related to Widget **********************************************
	options = Widget(root)
	# ents = options.makeform(['Last Name', 'First Name', 'Job', 'Country'])
	# root.bind('<Return>', (lambda event, e=ents: fetch(e)))   
	# b1 = Button(root, text='Show',
	# 	command=(lambda e=ents: options.fetch(e)))
	# b1.pack(side=LEFT, padx=5, pady=5)
	# b2 = Button(root, text='Quit', command=root.quit)
	# b2.pack(side=LEFT, padx=5, pady=5)
	ents = options.makeformForSheet(('Annual Rate', 'Number of Payments', 'Loan Principle', 'Monthly Payment', 'Remaining Loan'))
	root.bind('<Return>', (lambda event, e=ents: fetch(e)))   
	b1 = Button(root, text='Final Balance',
	      command=(lambda e=ents: options.final_balance(e)))
	b1.pack(side=LEFT, padx=5, pady=5)
	b2 = Button(root, text='Monthly Payment',
	      command=(lambda e=ents: options.monthly_payment(e)))
	b2.pack(side=LEFT, padx=5, pady=5)
	b3 = Button(root, text='Quit', command=root.quit)
	b3.pack(side=LEFT, padx=5, pady=5)
	# END Related to Widget ******************************************

	# showWidget()
	root.mainloop()