import tkinter as tk
import messagebox
import requests
import json
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import stats
import matplotlib.pyplot as plt
import math as math

LARGE_FONT = ("Lexend", 15)
SMALL_FONT = ("Lexend", 10)
my_list = []
tempAux = 0

my_list.insert(0, [100, 1])
my_list.insert(0, [200, 1.5])
my_list.insert(0, [300, 2])
my_list.insert(0, [400, 2.5])
my_list.insert(0, [500, 3])
my_list.insert(0, [600, 3.5])
my_list.insert(0, [700, 4])
my_list.insert(0, [800, 4.5])
my_list.insert(0, [900, 5])

#f = open("calibration.dat", "w")
#for x in range(len(my_list)):
#    a = my_list[len(my_list)-x-1]
#    f.write('' + a[0].__str__() + ' ' + a[1].__str__() + '\n')
#f.close()


# print(my_list)

class AplicationVibon(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Aplicação de Vibon")
        self.geometry("500x500")
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Página Inicial", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = tk.Button(self, text="Inserção de dados",
                           command=lambda: controller.show_frame(PageOne), font=SMALL_FONT)
        button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        button2 = tk.Button(self, text="Demonstração de dados",
                            command=lambda: controller.show_frame(PageTwo), font=SMALL_FONT)
        button2.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side="bottom")
        self.label1 = tk.Label(bottom_frame, text="Temp: ", font=SMALL_FONT)
        self.label1.grid(row=0, column=0, padx=10, pady=10)
        self.change_label1_text()

    def change_label1_text(self):
        try:
            response = requests.get('http://192.168.4.1/temperature')
            json_response = response.json()
            temp = json_response["temperature"]
            tempAux = temp
            text = "Temp: " + temp.__str__()
            self.cont1 += 1
            self.label1.config(text=text)
            self.after(5000, self.change_label1_text)
        except:
            print("Erro ao obter temperatura")


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Inserção de dados", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        self.input_label = tk.Label(self, text="Distancia (mm):", font=SMALL_FONT)
        self.input_label.pack()
        self.input_text = tk.Entry(self)
        self.input_text.pack()

        self.input_label2 = tk.Label(self, text="Número de medições:", font=SMALL_FONT)
        self.input_label2.pack()
        self.input_text2 = tk.Entry(self)
        self.input_text2.pack()

        button = tk.Button(self, text="Get Value", command=self.get_value, font=SMALL_FONT)
        button.pack()

        button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        button1 = tk.Button(self, text="Página Inicial",
                            command=lambda: controller.show_frame(StartPage), font=SMALL_FONT)
        button1.pack()

        button1.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    def get_value(self):
        # Get the value from the input field
        input_value = self.input_text.get()
        input_value2 = self.input_text2.get()
        if not input_value:  # If the input field is empty
            messagebox.showerror("Error", "Introduza um valor válido")
        else:
            # print(input_value)  # print the value for testing purposes
            try:
                link = 'http://192.168.4.1/calibration?dist=' + input_value + '&n=' + input_value2
                response = requests.get(link)
                json_response = response.json()
                calibration = json_response["calibration"]
                print(calibration)
                my_list.insert(0, [input_value, calibration])
                f = open("calibration.dat", "w")
                for x in range(len(my_list)):
                    a = my_list[len(my_list)-x-1]
                    f.write('' + a[0].__str__() + ' ' + a[1].__str__())
                f.close()
            except:
                print("Erro ao realizar a calibração")


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Demonstração de dados", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        print(my_list)
        button1 = tk.Button(self, text="Página Inicial",
                            command=lambda: controller.show_frame(StartPage), font=SMALL_FONT)
        button1.pack()

        button1.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        graph_frame = tk.Frame(self)
        graph_frame.pack(side="bottom")

        file = "calibration.dat"
        data = np.loadtxt(file)
        time_ms = data[:, 1]
        dist_mm = data[:, 0]


        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(4, 3)
        self.ax.scatter(time_ms, dist_mm)
        self.ax.plot(time_ms, dist_mm)
        self.ax.set(xlabel='X Axis', ylabel='Y Axis', title='Simple Line Plot')

        # Create the Tkinter Canvas widget that will display the graph
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()


        self.calculateValues()


    def calculateValues(self):
        file = "calibration.dat"
        data = np.loadtxt(file)
        time_ms = data[:, 1]
        dist_mm = data[:, 0]

        # Termometro
        theta_1C = tempAux
        theta_1K = theta_1C + 273.15

        Rterm = 1
        aTerm = Rterm / 2
        uTheta1 = aTerm / math.sqrt(3)

        uRelTheta1 = (uTheta1 / theta_1K) * 100
        print('\nTheta1 (K): ', theta_1K)
        # print(aTerm)
        print('Incerteza padrão - Theta1: ', uTheta1)
        print('Incerteza relativa - Theta1: ', uRelTheta1)

        # Velocida de referência
        vref = 20.05 * math.sqrt(theta_1K)
        uRelVref = 0.5 * uRelTheta1
        uVref = vref * (uRelVref / 100)

        print('\nVelocidade de referencia: ', vref)
        print('Incerteza padrão - Velocidade de referencia: ', uVref)
        print('Incerteza relativa - Velocidade de referencia: ', uRelVref)

        res = stats.linregress(time_ms, dist_mm)

        alpha_1 = res.slope
        beta_1 = res.intercept

        rValue = res.rvalue
        stderr = res.stderr  # Incerteza padrão do declive
        intErr = res.intercept_stderr  # Incerteza padrão da ordenada na origem
        print('\n')

        print('alpha1: ', alpha_1)
        print('beta1: ', beta_1)
        print('R^2: ', rValue)

        print("\nReta de regressão linear: d = %f teco + %f" % (alpha_1, beta_1))

        vsom = 2 * alpha_1
        print('\nVelocidade do som: ', vsom)

        print("\nIncertezas Padrao:")
        print('Incerteza padrão - alpha1: ', stderr)
        print('Incerteza padrão - beta1: ', intErr)
        print('Incerteza padrão - velocidade do som: ', 2 * stderr)

        print("\nIncertezas relativas:")
        relStdErr = (stderr / alpha_1) * 100
        relIntErr = np.abs(intErr / beta_1) * 100
        print('Incerteza relativa - alpha1: ', relStdErr)
        print('Incerteza relativa - beta1: ', relIntErr)
        print('Incerteza relativa - velocidade do som: ', relStdErr)

        desvRel = ((vsom - vref) / vref) * 100
        print('\nDesvio Relativo (exatidão): ', desvRel)

        plt.figure()
        titulo = 'Calibração sonar'

        plt.title(titulo, fontsize=14)
        plt.xlabel('Tempo de eco , teco (ms)', fontsize=14)
        plt.ylabel('Distancia, d (mm)', fontsize=14)

        plt.scatter(time_ms, dist_mm, color="black", )
        plt.plot(time_ms, dist_mm, color="blue", linewidth=1)




app = AplicationVibon()
app.mainloop()
