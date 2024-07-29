import tkinter as tk

# サブウィンドウ（デジピータ）表示
class DigiPeaterPage(tk.Frame):
	def __init__(self, master, frame_dpt, frame_cvr):
		tk.Frame.__init__(self, master, frame_dpt)
	
		frame_cvr.tkraise()
		frame_dpt.tkraise()
		frame_title = tk.Frame(self.master, relief=tk.FLAT, bd=0, width=626, height=22, bg="#e0e0e0")
		frame_title.place(x=7, y=102)
		label1 = tk.Label(frame_title, text="DIGIPEATER", bg="#e0e0e0", font=('Courie', 9, 'bold'))
		label1.place(x=10, y=0)	
