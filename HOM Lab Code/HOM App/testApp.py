import os
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import filedialog
from PIL import ImageTk, Image

from HOMlab import *

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("960x576")
        self.root.title("HOM Phase Map Generation")

        self.root.resizable(False, False)

        self.font = tkFont.Font(family="Arial Rounded MT Bold", size=14)
        self.contentfont = tkFont.Font(family="Arial", size=16, weight="normal")
        self.labelfont = tkFont.Font(family="Courier New", size=13)

        self.smallfont = tkFont.Font(family="Arial", size=16, weight="bold")
        self.bigfont = tkFont.Font(family="Arial Rounded MT Bold", size=30,)
        self.messagefont = tkFont.Font(
            family="Arial", size=30, weight='bold')

        self.beam_size_label = tk.Label(
            self.root, text="Average Beam Size (mm):", font=self.font, )
        self.beam_size_label.place(x=112, y=20)

        self.beam_size_entry = tk.Entry(
            self.root, font=self.contentfont, width=6, justify='center', bd=0, highlightthickness=0.6, highlightbackground='#DBDBDB')
        self.beam_size_entry.place(x=362, y=22)

        self.beam_size_entry.insert(0, "1.3")

        # create the dropdown menu
        hom_options = ["HG11", "HG22", "HG33", "HG44", "HG55", "HG66"]
        self.selected_hom = tk.StringVar(self.root)
        self.selected_hom.set(hom_options[2])

        self.hom_menu_label = tk.Label(
            self.root, text="Select Your HOM: ", font=self.font)
        self.hom_menu_label.place(x=572, y=20)

        self.hom_menu = tk.OptionMenu(
            self.root, self.selected_hom, *hom_options)
        self.hom_menu.config(font=self.contentfont, width=6, justify="center", highlightthickness=3, bd=3)
        self.hom_menu.place(x=750, y=12)

        # Create the first slider
        self.slider1_label = tk.Label(
            self.root, text="Beam Size (x): ", font=self.font)
        self.slider1_label.place(x=50, y=77)

        self.slider1 = tk.Scale(
            self.root, from_=0.5, to=1.5, orient=tk.HORIZONTAL, resolution=0.01, length=500, font=self.contentfont)
        self.slider1.place(x=200, y=54)

        self.slider1.set(1.0)

        # Create the second slider
        self.slider2_label = tk.Label(
            self.root, text="Beam Size (y): ", font=self.font)
        self.slider2_label.place(x=50, y=127, )

        self.slider2 = tk.Scale(
            self.root, from_=0.5, to=1.5, orient=tk.HORIZONTAL, resolution=0.01, length=500, font=self.contentfont)
        self.slider2.place(x=200, y=104)

        self.slider2.set(1.0)

        # Create the force button
        self.force_button = tk.Button(
            self.root, text="No Astigmatism", command=self.force_slider, font=self.font, height=2, width=14, cursor="hand2")
        self.force_button.place(x=735, y=84)

        self.var = tk.IntVar()
        self.R1 = tk.Radiobutton(
            self.root, text="Single Map", variable=self.var, value=1, command=self.select, font=self.font)

        self.R2 = tk.Radiobutton(
            self.root, text="Multiple Maps", variable=self.var, value=2, command=self.select, font=self.font)

        self.R1.place(x=57, y=173)
        self.R2.place(x=57, y=206)

        # Create the Generate button
        self.generate_button = tk.Button(
            self.root, text="Generate", command=self.generate_image, font=self.bigfont, width=8, height=1, cursor="hand2")
        # self.generate_button = ttk.Button(
        #     self.root, text="Generate", command=self.generate_image, cursor="hand1", style='RoundedButton.TButton')
        self.generate_button.place(x=630, y=290)

        # Create the display window

        defaultImage = Image.fromarray(np.ones((270, 450)))
        default_tk_image = ImageTk.PhotoImage(master=self.root, image=defaultImage)
        shadow_display = tk.Label(self.root, image=default_tk_image, bg="#000000")
        self.display = tk.Label(
            self.root, image=default_tk_image, bg="#BEBEBE")

        shadow_display.place(x=100+1, y=258+1)
        self.display.place(x=100, y=258)


        self.displaylabel = tk.Label(
            self.root, text="Phase Map Preview", font=self.font)
        self.displaylabel.place(x=247, y=538)

        
        # back_savebtn = tk.Button(self.root, bg="black", font=self.bigfont, width=9, height=2, cursor="hand1", bd=0, activebackground="black", highlightthickness=0)
        self.save_button = tk.Button(
            self.root, text="Save", command=self.save_image, font=self.bigfont, width=8, height=1, cursor="hand2")

        # back_savebtn.place(x=630+2, y=405+2)
        self.save_button.place(x=630, y=410)

        self.map_size = []
        self.pil_images = []

    def display_notification(self, message, type):
        if type == "success":
            fg = "green"
        elif type == "warning":
            fg = "red"
        else:
            fg = "orange"
        messagelabel = tk.Label(self.root, text=message,
                                highlightthickness=0, bg="#BEBEBE")
        messagelabel.place(x=148, y=380)
        messagelabel.config(font=self.messagefont, fg=fg)

        # schedule the label to disappear after three seconds
        messagelabel.after(3000, messagelabel.destroy)

    def select(self):
        value = int(self.var.get())
        if value == 1:
            try:
                self.map_size_range_label.destroy()
                self.map_size_start.destroy()
                self.map_size_start_label.destroy()
                self.map_size_end.destroy()
                self.map_size_end_label.destroy()
                self.map_size_steps.destroy()
                self.map_size_steps_label.destroy()
            except:
                pass
            finally:
                # Create the map size slider
                self.map_size_label = tk.Label(
                    self.root, text="Map Size", font=tkFont.Font(family="DejaVu Math TeX Gyre", size=22))

                self.map_size_slider = tk.Scale(
                    self.root, from_=0, to=1, orient=tk.HORIZONTAL, resolution=0.01, length=500, font=self.smallfont)

                self.map_size_label.place(x=765, y=187)
                self.map_size_slider.place(x=230, y=170)
                self.map_size_slider.set(0.5)

        elif value == 2:
            try:
                self.map_size_label.destroy()
                self.map_size_slider.destroy()
            except:
                pass
            finally:
                self.map_size_range_label = tk.Label(
                    self.root, text="Map Size Range ", font=tkFont.Font(family="DejaVu Math TeX Gyre", size=22))

                self.map_size_start = tk.Entry(
                    self.root, font=self.contentfont, width=5, justify="center")
                self.map_size_start_label = tk.Label(
                    self.root, text="Min Map Size", font=self.labelfont)
                self.map_size_end = tk.Entry(
                    self.root, font=self.contentfont, width=5, justify="center")
                self.map_size_end_label = tk.Label(
                    self.root, text="Max Map Size", font=self.labelfont)
                self.map_size_steps = tk.Entry(
                    self.root, font=self.contentfont, width=5, justify="center")
                self.map_size_steps_label = tk.Label(
                    self.root, text="Number of Maps", font=self.labelfont)

                self.map_size_start.insert(0, "0.2")
                self.map_size_end.insert(0, "0.8")
                self.map_size_steps.insert(0, "6")

                self.map_size_range_label.place(x=685, y=171)

                self.map_size_start.place(x=280, y=173)
                self.map_size_start_label.place(x=250, y=213)

                self.map_size_end.place(x=430, y=173)
                self.map_size_end_label.place(x=407, y=213)

                self.map_size_steps.place(x=580, y=175)
                self.map_size_steps_label.place(x=556, y=213)

        else:
            return

    def force_slider(self):
        # Set the value of slider2 to be the same as slider1
        self.slider2.set(self.slider1.get())

    def get_image(self, var=None):
        value = int(self.var.get())
        if value == 1:
            self.map_size = [float(self.map_size_slider.get())]
        elif value == 2:
            start = float(self.map_size_start.get())
            end = float(self.map_size_end.get())
            steps = int(self.map_size_steps.get())

            self.map_size = np.linspace(start, end, steps, endpoint=True)

        w0 = float(self.beam_size_entry.get())*1e-3
        w1 = float(self.slider1.get())
        w2 = float(self.slider2.get())

        w1 *= w0
        w2 *= w0

        self.pil_images = []
        if len(self.map_size) == 0:
            self.display_notification(
                message="Select Map Size Options!", type="warning")
            return

        for map_size in self.map_size:
            map_size1 = map_size*w1
            map_size2 = map_size*w2

            HOM = self.selected_hom.get()

            if HOM == "HG11":
                phaseHG = phaseHG11(map_size1, map_size2)
            elif HOM == "HG22":
                phaseHG = phaseHG22(map_size1, map_size2)
            elif HOM == "HG33":
                phaseHG = phaseHG33(map_size1, map_size2)
            elif HOM == "HG44":
                phaseHG = phaseHG44(map_size1, map_size2)
            elif HOM == "HG55":
                phaseHG = phaseHG55(map_size1, map_size2)
            elif HOM == "HG66":
                phaseHG = phaseHG66(map_size1, map_size2)

            pil_image = Image.fromarray(phaseHG*127.5)
            self.pil_images.append(pil_image)
            pil_image = pil_image.resize((450, 270))
            tk_image = ImageTk.PhotoImage(pil_image)
            self.display.configure(image=tk_image)
            self.display.image = tk_image

    def save_image(self):
        try:
            self.pil_images
        except:
            self.get_image()

        HOM = self.selected_hom.get()
        if len(self.pil_images) == 0:
            self.display_notification(
                message="Generate An Image First!", type="warning")
            return
        elif len(self.pil_images) == 1:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".bmp", initialfile=f"{HOM}_size_{self.map_size[0]:.3f}.bmp",)
            self.pil_images[0].convert(mode='L').save(file_path)
            return

        file_path = filedialog.asksaveasfilename(
            initialfile=f"{HOM}_size_.bmp",)
        head, tail = os.path.split(file_path)
        tail = tail.split(".")[0]
        for idx, image in enumerate(self.pil_images):
            filename = f"{tail}{self.map_size[idx]:.3f}.bmp"
            savedfilename = os.path.join(head, filename)
            image.convert(mode='L').save(savedfilename)

    def generate_image(self):
        self.get_image()

app = App()
app.root.mainloop()
