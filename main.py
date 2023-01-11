import tkinter as tk
from tkinter import ttk

import messagebox
import requests
import json
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy import stats
import matplotlib.pyplot as plt
import math as math
import os

LARGE_FONT = ("Lexend", 15)
SMALL_FONT = ("Lexend", 10)
my_list = []
alphaAux = 0
betaAux = 0
tempAux = 0


# my_list.insert(0, [100, 1])
# my_list.insert(0, [200, 1.5])
# my_list.insert(0, [300, 2])
# my_list.insert(0, [400, 2.5])
# my_list.insert(0, [500, 3])
# my_list.insert(0, [600, 3.5])
# my_list.insert(0, [700, 4])
# my_list.insert(0, [800, 4.5])
# my_list.insert(0, [900, 5])


# f = open("calibration.dat", "w")
# for x in range(len(my_list)):
#    a = my_list[len(my_list)-x-1]
#    f.write('' + a[0].__str__() + ' ' + a[1].__str__() + '\n')
# f.close()


# print(my_list)

class AplicationVibon(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Aplicação de Vibon")
        self.geometry("1000x800")
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

    def get_page(self, page_class):
        return self.frames[page_class]


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.alphaAux = 0
        self.betaAux = 0
        self.tempAux = 0
        label = tk.Label(self, text="Calibração do Sonar", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button = tk.Button(self, text="Inserção de dados",
                           command=lambda: controller.show_frame(PageOne), font=SMALL_FONT)
        button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        button2 = tk.Button(self, text="Demonstração de dados",
                            command=self.updateFrameAndShow, font=SMALL_FONT)
        button2.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        button2 = tk.Button(self, text="Medir distancia",
                            command=self.showAlert, font=SMALL_FONT)
        button2.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        button3 = tk.Button(self, text="Apagar dados recolhidos",
                            command=self.eraseValues, font=SMALL_FONT)
        button3.place(relx=0.2, rely=0.7, anchor=tk.CENTER)


        button3 = tk.Button(self, text="Sair", command=self.exit, font=SMALL_FONT)
        button3.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        bottom_frame = tk.Frame(self)
        bottom_frame.pack(side="bottom")
        self.label1 = tk.Label(bottom_frame, text="Temp: ", font=SMALL_FONT)
        self.label1.grid(row=0, column=0, padx=10, pady=50)
        self.change_label1_text()

    def updateFrameAndShow(self):
        page = self.controller.get_page(PageTwo)
        page.calculateValues()
        if page.is_empty():
            messagebox.showerror("Error", "Não foram introduzidos dados")
        else:
            self.controller.show_frame(PageTwo)

    def change_label1_text(self):
        try:
            response = requests.get('http://192.168.4.1/temperature')
            json_response = response.json()
            temp = json_response["temperature"]
            self.tempAux = temp
            text = "Temp: " + temp
            self.label1.config(text=text)
            self.after(5000, self.change_label1_text)
        except:
            print("Erro ao obter temperatura")

    def showAlert(self):
        page = self.controller.get_page(StartPage)
        valueAux = 0
        alphaAux = page.alphaAux
        betaAux = page.betaAux
        print(alphaAux)
        print(betaAux)

        link = 'http://192.168.4.1/hooke?alpha=' + alphaAux.__str__() + '&beta=' + betaAux.__str__()
        print(link)
        try:

            response = requests.get(link)

            json_response = response.json()
            hooke = json_response["hooke"]
            valueAux = hooke
            msg = 'Distancia obtida (mm): ' + valueAux.__str__()
            messagebox.showinfo("Distancia", msg)
        except:
            print("Erro ao obter distancia")

    def eraseValues(self):
        open('calibration.dat', 'w').close()
        my_list.clear()


    def exit(self):
        self.quit()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
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

        button = tk.Button(self, text="Obter um valor", command=self.get_value, font=SMALL_FONT)
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
        if not input_value and not input_value2:  # If the input field is empty
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
                    a = my_list[len(my_list) - x - 1]
                    f.write('' + a[0].__str__() + ' ' + a[1].__str__() + '\n')
                f.close()
                #messagebox.showinfo("Sucesso", "Dado obtido com sucesso")
            except:
                messagebox.showerror("Error", "Erro ao realizar a calibração")

        self.input_text.delete(0, "end")
        self.input_text2.delete(0, "end")


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.path = "calibration.dat"
        label = tk.Label(self, text="Demonstração de dados", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        print(my_list)

        graph_frame = tk.Frame(self)
        graph_frame.pack(side="top", pady=10, padx=10)

        file = "calibration.dat"
        if self.is_empty():
            time_ms = [0]
            dist_mm = [0]
        else:
            data = np.loadtxt(self.path)
            time_ms = data[:, 1]
            dist_mm = data[:, 0]

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.scatter(time_ms, dist_mm)
        self.ax.plot(time_ms, dist_mm, color="red", linewidth=1)
        self.ax.set(xlabel='Tempo (ms)', ylabel='Distancia (mm)', title='Calibração dos Dados')

        # Create the Tkinter Canvas widget that will display the graph
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack()
        self.canvas.draw()

        table_frame = tk.Frame(self)
        table_frame.pack(side="bottom", fill="both", expand=True)

        self.table = ttk.Treeview(table_frame, height=7)
        self.table["columns"] = ("one", "two", "three", "four", "five")

        self.table.heading("one", text="Grandeza")
        self.table.heading("two", text="Simbolo")
        self.table.heading("three", text="Valor")
        self.table.heading("four", text="Incerteza Padrão")
        self.table.heading("five", text="Incerteza Relativa (%)")
        self.table.column('#0', width=0, minwidth=0)
        self.table.pack(pady=10, padx=10)

        self.table.column("one", width=150)
        self.table.column("two", width=100)
        self.table.column("three", width=100)
        self.table.column("four", width=100)
        self.table.column("five", width=100)

        button1 = tk.Button(self, text="Página Inicial",
                            command=lambda: controller.show_frame(StartPage), font=SMALL_FONT)
        button1.pack(pady=10, padx=10)

        button1.place(relx=0.5, rely=0.90, anchor=tk.CENTER)

    def calculateValues(self):
        self.table.delete(*self.table.get_children())
        page = self.controller.get_page(StartPage)
        if self.is_empty():
            time_ms = [0]
            dist_mm = [0]
        else:
            data = np.loadtxt(self.path)
            time_ms = data[:, 1]
            dist_mm = data[:, 0]
        self.ax.clear()  # clear the existing graph
        self.ax.scatter(time_ms, dist_mm)
        self.ax.plot(time_ms, dist_mm, color="red", linewidth=1)
        self.ax.set(xlabel='Tempo (ms)', ylabel='Distancia (mm)', title='Calibração dos Dados')
        self.canvas.draw()

        # Termometro
        theta_1C = float(page.tempAux)
        theta_1K = theta_1C + 273.15

        Rterm = 0.1
        aTerm = Rterm
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

        self.table.insert("", "end", values=(
            "Tempertura ambiente", "\u03B8 (K)", "%.3f" % theta_1K, "%.3f" % uTheta1, "%.3f" % uRelTheta1))
        self.table.insert("", "end", values=(
            "Velocidade do som (ref.)", "V_ref (m/s)", "%.3f" % vref, "%.3f" % uVref, "%.3f" % uRelVref))
        self.table.insert("", "end", values=(
            "Declive da reta", "\u03B1 (mm m/s) ", "%.3f" % alpha_1, "%.3f" % stderr, "%.3f" % relStdErr))
        self.table.insert("", "end", values=(
            "Ordenada na origem", "\u03B2 (mm)", "%.3f" % beta_1, "%.3f" % intErr, "%.3f" % relIntErr))
        self.table.insert("", "end", values=("Coeficiente de correlação", "r2", "%.6f" % rValue, "-----", "-----"))
        self.table.insert("", "end", values=(
            "Velocidade do som (exp.)", "V_som (m/s)", "%.3f" % vsom, "%.3f" % (2 * stderr), "%.3f" % relStdErr))
        self.table.insert("", "end",
                          values=("Desvio relativo (exactidão)", "\u0394 (%)", "%.3f" % desvRel, "-----", "-----"))

        page.alphaAux = "%.3f" % alpha_1
        page.betaAux = "%.3f" % beta_1

        print(page.alphaAux)
        print(page.betaAux)

    def is_empty(self):
        filepath = self.path
        return os.stat(filepath).st_size == 0


app = AplicationVibon()
app.mainloop()
