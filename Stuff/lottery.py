#! python3
from tkinter import *
from tkinter import ttk

import os
import random

from collections import OrderedDict

from common import ExperimentFrame, InstructionsFrame
from gui import GUI


################################################################################
# TEXTS

options = ((26, 28, 30, 32, 34),
           (5, 10, 20, 40, 80),
           (400, 250, 170, 100, 60))

instructions = """
V následujícím úkolu uděláte 5 nezávislých rozhodnutí mezi dvěma možnostmi. První možnost vždy reprezentuje jistou odměnu a druhá možnost vždy reprezentuje loterii. Číslo s procenty reprezentuje pravděpodobnost, že vyhrajete a získáte uvedenou odměnu. Pokud prohrajete, Vaše odměna bude 0 Kč.

Až tuto úlohu dokončíte, bude stanovena Vaše odměna. Bude náhodně vybráno jedno z rozhodnutí (každé se stejnou pravděpodobností) a dostanete jistou odměnu nebo bude realizována odpovídající loterie (podle toho, zda se ve vybrané volbě rozhodnete pro jistou odměnu nebo loterii). I když učiníte 5 rozhodnutí, pouze jedno z nich bude tedy rozhodovat o Vaši odměně.

V každém z 5 řádků se rozhodněte a vyberte prosím, zda preferujete jistou odměnu nebo loterii.
"""

wintext = """
Bylo náhodně vybráno Vaše rozhodnutí číslo {}.

{}
"""

sure = "Protože jste zvolil(a) jistou odměnu, vyhráváte {} Kč."
risky = "Protože jste zvolil(a) loterii, loterie byla realizována a vyhráváte {} Kč."



################################################################################


class Lottery(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)
        self.options = options
           
        self.text = Text(self, font = "helvetica 15", relief = "flat", background = "white", height = 14,
                         wrap = "word", highlightbackground = "white", width = 90)
        self.text.grid(row = 1, column = 0, columnspan = 4)
        self.text.insert("1.0", instructions)
        self.text.config(state = "disabled")

        self.leftLabel = ttk.Label(self, text = "Jistá odměna", font = "helvetica 15", background = "white")
        self.leftLabel.grid(row = 3, column = 1, pady = 10)
        self.rightLabel = ttk.Label(self, text = "Loterie", font = "helvetica 15", background = "white")
        self.rightLabel.grid(row = 3, column = 2, pady = 10)

        self.variables = OrderedDict()
        self.rbuttonsL = {}
        self.rbuttonsR = {}
        for i in range(5):
            row = i + 4
            self.variables[i] = StringVar()
            self.rbuttonsL[i] = ttk.Radiobutton(self, text = " {} Kč".format(options[0][i]),
                                                variable = self.variables[i], value = str(i+1) + "sure",
                                                command = self.checkAllFilled)
            self.rbuttonsL[i].grid(column = 1, row = row, sticky = W, padx = 30)
            self.rbuttonsR[i] = ttk.Radiobutton(self, variable = self.variables[i], value = str(i+1) + "risky",
                                                text = " {}% {} Kč".format(options[1][i], options[2][i]),
                                                command = self.checkAllFilled)
            self.rbuttonsR[i].grid(column = 2, row = row, sticky = W, padx = 30)

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")
        ttk.Style().configure("TButton", font = "helvetica 15")

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(3, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(9, weight = 1)
        self.rowconfigure(10, weight = 1)

        self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun)
        self.next.grid(row = 9, column = 0, columnspan = 4, pady = 15)
        self.next["state"] = "disabled"
        

    def checkAllFilled(self):
        if all([var.get() for var in self.variables.values()]):
            self.next["state"] = "!disabled"


    def write(self):
        selected = random.randint(1, 5)
        self.root.texts["lottery_selected"] = selected
        if "risky" in self.variables[selected - 1].get():
            self.root.texts["lottery_chosen"] = "risky"
            if random.random() * 100 < self.options[1][selected - 1]:
                win = self.options[2][selected - 1]
                self.root.texts["lottery_random"] = "won"
            else:
                win = 0
                self.root.texts["lottery_random"] = "lost"
        else:
            self.root.texts["lottery_chosen"] = "safe"
            win = self.options[0][selected - 1]
        self.file.write("Lottery\n")
        self.root.texts["lottery_win"] = win
        self.file.write("\t".join([self.id] + [var.get() for var in self.variables.values()] + [str(selected), str(win)]) + "\n")



class LotteryWin(InstructionsFrame):
    def __init__(self, root):
        self.root = root
        if self.root.texts["lottery_chosen"] == "risky":
            append = risky
        else:
            append = sure
        text = wintext.format(self.root.texts["lottery_selected"],
                              append.format(self.root.texts["lottery_win"]))       
        super().__init__(root, text = text, proceed = True, height = 5)  


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Lottery,
         LotteryWin])
