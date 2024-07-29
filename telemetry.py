import tkinter as tk

# サブウィンドウ（テレメトリ）表示
class TelemetryPage(tk.Frame):
	def __init__(self, master, frame_tlm, frame_cvr):
		tk.Frame.__init__(self, master, frame_tlm)

		frame_cvr.tkraise()
		frame_tlm.tkraise()
		frame_title = tk.Frame(self.master, relief=tk.FLAT, bd=0, width=626, height=22, bg="#e0e0e0")
		frame_title.place(x=7, y=102)
		label1 = tk.Label(frame_title, text="TELEMETRY", bg="#e0e0e0", font=('Courie', 9, 'bold'))
		label1.place(x=10, y=0)

	