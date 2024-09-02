from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import perf_counter, sleep

import random
import os
import urllib.request
import urllib.parse

from common import ExperimentFrame, InstructionsFrame, Measure, MultipleChoice, InstructionsAndUnderstanding
from gui import GUI
from constants import TESTING, URL, TRUST
from questionnaire import Questionnaire
from cheating import Login


################################################################################
# TEXTS
instructionsT1 = """Vaše rozhodnutí v této úloze budou mít finanční důsledky pro Vás a pro dalšího přítomného účastníka v laboratoři. Pozorně si přečtěte pokyny, abyste porozuměli studii a své roli v ní. 

V rámci této úlohy jste spárováni s dalším účastníkem studie. Oba obdržíte {} Kč.

Bude Vám náhodně přidělena jedna ze dvou rolí: budete buď hráčem A, nebo hráčem B. Oba účastníci ve dvojici budou vždy informováni o rozhodnutích druhého hráče.

<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role.

Jakmile oba odešlete své odpovědi, dozvíte se jaká byla Vaše role a jaký je celkový výsledek rozhodnutí Vás a druhého účastníka. 

Tuto úlohu budete hrát v rámci studie celkem čtyřikrát a Vaše odměna za úlohu bude záviset na jedné, náhodně vylosované hře z těchto čtyř."""

instructionsT2 = """Nyní obdržíte opět úlohu, v které jste spárováni s jiným účastníkem studie a můžete si posílat peníze.

V tomto kole oba obdržíte {} Kč.

Podobně jako v předchozím kole úlohy:
<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role.

Jakmile oba odešlete své odpovědi, dozvíte se jaká byla Vaše role a jaký je celkový výsledek rozhodnutí Vás a druhého účastníka. 

Vaše odměna za úlohu bude záviset na jedné, náhodně vylosované hře z celkových čtyř, které budete hrát."""

instructionsT4 = instructionsT3 = instructionsT2


# to do
trustControl1 = "Jaká je role hráče A a hráče B ve studii?"
trustAnswers1 = ["Hráč A rozhoduje, kolik hráči B vezme peněz. Účastníci studie jsou v obou kolech buď hráčem A, nebo hráčem B (role se nemění).",
"Hráč A rozhoduje, kolik hráči B vezme peněz. Účastníci studie jsou nejprve hráčem A v druhém kole hráčem B (role se vymění).", "Hráč B rozhoduje, kolik hráči A vezme peněz. Účastníci studie jsou v obou kolech buď hráčem A, nebo hráčem B (role se nemění).", "Hráč B rozhoduje, kolik hráči A vezme peněz. Účastníci studie jsou nejprve hráčem A v druhém kole hráčem B (role se vymění)."]
trustFeedback1 = ["Správná odpověď.", "Chybná odpověď. Účastníci studie jsou v obou kolech buď hráčem A, nebo hráčem B (role se nemění).", "Chybná odpověď. Hráč A rozhoduje, kolik hráči B vezme peněz.", "Chybná odpověď. Hráč A rozhoduje, kolik hráči B vezme peněz. Účastníci studie jsou v obou kolech buď hráčem A, nebo hráčem B (role se nemění)."]



wait_text = "Prosím počkejte na druhého hráče."



trustResultTextA = """Náhodně Vám byla vybrána role hráče A.

<b>Rozhodl jste se poslat {} Kč.</b>
Tato částka byla ztrojnásobena na {} Kč.
<b>Ze svých {} Kč Vám poslal hráč B {} Kč.</b>

<b>V této úloze jste tedy získal(a) {} Kč a hráč B {} Kč.</b>
Tuto odměnu získáte, pokud bude toto kolo hry vylosováno pro vyplacení.
"""

trustResultTextB = """Náhodně Vám byla vybrána role hráče B.

<b>Hráč A se rozhodl poslat {} Kč.</b>
Tato částka byla ztrojnásobena na {} Kč.
<b>Ze svých {} Kč jste poslal(a) hráči B {} Kč.</b>

<b>V této úloze jste tedy získal(a) {} Kč a hráč A {} Kč.</b>
Tuto odměnu získáte, pokud bude toto kolo hry vylosováno pro vyplacení.
"""



################################################################################





class ScaleFrame(Canvas):
    def __init__(self, root, font = 15, maximum = 0, player = "A", returned = 0, endowment = 100):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.parent = root
        self.root = root.root
        self.rounding = maximum / 5 if player == "A" else 10
        self.player = player
        self.returned = returned
        self.font = font
        self.endowment = endowment

        self.valueVar = StringVar()
        self.valueVar.set("0")

        ttk.Style().configure("TScale", background = "white")

        self.value = ttk.Scale(self, orient = HORIZONTAL, from_ = 0, to = maximum, length = 500,
                            variable = self.valueVar, command = self.changedValue)

        self.playerText1 = "Já:" if player == "A" else "Hráč A:"
        self.playerText2 = "Hráč B:" if player == "A" else "Já:"
        self.totalText1 = "{0:3d} Kč" if player == "A" else "{0:3d} Kč"
        self.totalText2 = "{0:3d} Kč" if player == "A" else "{0:3d} Kč"

        self.valueLab = ttk.Label(self, textvariable = self.valueVar, font = "helvetica {}".format(font), background = "white", width = 3, anchor = "e")
        self.currencyLab = ttk.Label(self, text = "Kč", font = "helvetica {}".format(font), background = "white", width = 6)
        self.playerLab1 = ttk.Label(self, text = self.playerText1, font = "helvetica {}".format(font), background = "white", width = 6, anchor = "e") 
        self.playerLab2 = ttk.Label(self, text = self.playerText2, font = "helvetica {}".format(font), background = "white", width = 6, anchor = "e") 
        self.totalLab1 = ttk.Label(self, text = self.totalText1.format(0), font = "helvetica {}".format(font), background = "white", width = 6, anchor = "e")
        self.totalLab2 = ttk.Label(self, text = self.totalText2.format(0), font = "helvetica {}".format(font), background = "white", width = 6, anchor = "e")
        self.spaces = ttk.Label(self, text = " ", font = "helvetica {}".format(font), background = "white", width = 1)
        self.changedValue(0)

        self.value.grid(column = 1, row = 1, padx = 10)
        self.valueLab.grid(column = 3, row = 1)        
        self.currencyLab.grid(column = 4, row = 1)
        self.playerLab1.grid(column = 5, row = 1, padx = 3)
        self.totalLab1.grid(column = 6, row = 1, padx = 3, sticky = "ew")
        self.spaces.grid(column = 7, row = 1)
        self.playerLab2.grid(column = 8, row = 1, padx = 3)        
        self.totalLab2.grid(column = 9, row = 1, padx = 3, sticky = "ew")



    def changedValue(self, value):         
        newval = int(round(eval(self.valueVar.get())/self.rounding, 0)*self.rounding)
        self.valueVar.set("{0:3d}".format(newval))
        if self.player == "A":
            self.totalLab1["text"] = self.totalText1.format(self.endowment - newval)
            self.totalLab2["text"] = self.totalText2.format(self.endowment + newval * 3)
            self.totalLab1["font"] = "helvetica {} bold".format(self.font)
            self.playerLab1["font"] = "helvetica {} bold".format(self.font)
        else:
            self.totalLab1["text"] = self.totalText1.format(self.endowment - self.returned + newval)
            self.totalLab2["text"] = self.totalText2.format(self.returned * 3 + self.endowment - newval)
            self.totalLab2["font"] = "helvetica {} bold".format(self.font)
            self.playerLab2["font"] = "helvetica {} bold".format(self.font)
        #self.parent.checkAnswers()
              


class Trust(InstructionsFrame):
    def __init__(self, root):

        if not "trustblock" in root.status:
            root.status["trustblock"] = 1
        else:
            root.status["trustblock"] += 1

        if not "endowments" in root.status:
            endowments = list(map(TRUST.__getitem__, [1,2,0,2])) if root.status["incentive_order"] == "high-low" else list(map(TRUST.__getitem__, [1,0,2,2]))
            root.status["endowments"] = endowments

        endowment = root.status["endowments"][root.status["trustblock"] - 1]

        text = eval("instructionsT" + str(root.status["trustblock"])).format(endowment, endowment, int(endowment/5))

        height = 20
        width = 100

        super().__init__(root, text = text, height = height, font = 15, width = width)

        self.labA = ttk.Label(self, text = "Pokud budu hráč A", font = "helvetica 15 bold", background = "white")
        self.labA.grid(column = 0, row = 2, columnspan = 3, pady = 10)        

        # ta x-pozice tady je hnusny hack, idealne by se daly texty odmen vsechny sem ze slideru
        self.labR = ttk.Label(self, text = "Odměna", font = "helvetica 15 bold", background = "white", anchor = "center", width = 28)
        self.labR.grid(column = 1, row = 2, pady = 10, sticky = E)

        self.frames = {}
        for i in range(7):            
            if i != 6:
                text = "Pokud hráč A pošle {} Kč, pošlu:".format(i*20)
                ttk.Label(self, text = text, font = "helvetica 15", background = "white").grid(column = 0, row = 6 + i, pady = 1, sticky = E)
                player = "B"
            else:
                ttk.Label(self, text = "Pošlu:", font = "helvetica 15", background = "white").grid(column = 0, row = 3, pady = 1, sticky = E)            
                player = "A"
            maximum = int(i * 3 * endowment / 5 + endowment) if i < 6 else endowment            
            self.frames[i] = ScaleFrame(self, maximum = maximum, player = player, returned = int(i*endowment/5), endowment = endowment)
            row = 6 + i if i < 6 else 3
            self.frames[i].grid(column = 1, row = row, pady = 1)
        
        self.labB = ttk.Label(self, text = "Pokud budu hráč B", font = "helvetica 15 bold", background = "white")
        self.labB.grid(column = 0, row = 5, columnspan = 3, pady = 10)

        self.next.grid(column = 0, row = 19, columnspan = 3, pady = 5, sticky = N)            
        #self.next["state"] = "disabled"
        
        self.text.grid(row = 1, column = 0, columnspan = 3)

        #self.rowconfigure(15, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 0)
        self.rowconfigure(2, weight = 0)
        self.rowconfigure(3, weight = 0)
        self.rowconfigure(4, weight = 1)
        self.rowconfigure(18, weight = 2)
        self.rowconfigure(20, weight = 2)

        self.columnconfigure(0, weight = 2)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 2)

    # def checkAnswers(self):        
    #     for frame in self.frames.values():
    #         pass
    #         # if not frame.messageVar.get():
    #         #     break
    #     else:
    #         self.next["state"] = "normal"

    def nextFun(self):
        self.send()
        self.write()
        super().nextFun()

    def send(self):        
        self.responses = [self.frames[i].valueVar.get() for i in range(7)]
        data = {'id': self.id, 'round': "trust" + str(self.root.status["trustblock"]), 'offer': "_".join(self.responses)}
        self.sendData(data)

    def write(self):
        block = self.root.status["trustblock"]
        self.file.write("Trust\n")
        d = [self.id, str(block + 2), self.root.status["trust_pairs"][block-1], self.root.status["trust_roles"][block-1], self.root.status["condition"], self.root.status["incentive_order"], self.root.status["endowments"][block-1]]
        self.file.write("\t".join(map(str, d + self.responses)))
        if URL == "TEST":
            if self.root.status["trust_roles"][block-1] == "A":                        
                self.root.status["trustTestSentA"] = int(self.frames[6].valueVar.get())
            else:
                self.root.status["trustTestSentB"] = [int(self.frames[i].valueVar.get()) for i in range(6)]       
        self.file.write("\n\n")




class WaitTrust(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = wait_text, height = 3, font = 15, proceed = False, width = 45)
        #self.what = what
        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def checkUpdate(self):
        count = 0
        while True:
            self.update()
            if count % 50 == 0:                
                block = self.root.status["trustblock"]
                endowment = self.root.status["endowments"][block - 1] 

                data = urllib.parse.urlencode({'id': self.id, 'round': block, 'offer': "trust"})                
                data = data.encode('ascii')
                if URL == "TEST":                    
                    if self.root.status["trust_roles"][block - 1] == "A":                        
                        sentA = self.root.status["trustTestSentA"]
                        sentB = random.randint(0, int((sentA * 3 + endowment) / 10)) * 10
                    else:
                        chose = random.randint(0,5)
                        sentA = int(chose * 2 * endowment / 10)
                        sentB = self.root.status["trustTestSentB"][chose]
                    response = "_".join(map(str, [self.root.status["trust_pairs"][block - 1], sentA, sentB]))
                else:
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8")       
                    except Exception as e:
                        continue

                if response:               
                    pair, sentA, sentB = response.split("_")
                    sentA, sentB = int(sentA), int(sentB)
                    
                    if int(self.root.status["winning_trust"]) == block + 2:
                        reward = endowment - sentA + sentB if self.root.status["trust_roles"][block] == "A" else endowment + sentA*3 - sentB    
                        self.root.texts["trust"] = str(reward)                        

                    if self.root.status["trust_roles"][block - 1] == "A": 
                        text = trustResultTextA.format(sentA, sentA*3, endowment + sentA*3, sentB, endowment - sentA + sentB, endowment + sentA*3 - sentB)
                    else:
                        text = trustResultTextB.format(sentA, sentA*3, endowment + sentA*3, sentB, endowment + sentA*3 - sentB, endowment - sentA + sentB)
                    self.root.texts["trustResult"] = text

                    self.write(response)
                    self.progressBar.stop()
                    self.nextFun()  
                    return
            count += 1
            sleep(0.1)

    def run(self):
        self.progressBar.start()
        self.checkUpdate()

    def write(self, response):
        pass
        # if self.what == "pairing":
        #     self.file.write("Pairing" + "\n")
        # elif self.what == "decision1":
        #     self.file.write("Dictator Results 1" + "\n")
        # self.file.write(self.id + "\t" + response.replace("_", "\t") + "\n\n") 

       

# class InstructionsDictator(InstructionsAndUnderstanding):
#     def __init__(self, root):
#         out = ["forgive-ignore", "ignore-punish", "forgive-punish"].index(root.status["dictatorCondition"]) + 2
#         controlTexts = controlTexts1
#         controlTexts.pop(out)
        
#         super().__init__(root, text = instructions, height = 31, width = 110, name = "Dictator Control Questions", randomize = False, controlTexts = controlTexts, update = ["firstOption", "secondOption"])    



# controlTexts1 = [[DictControl1, DictAnswers1, DictFeedback1], [DictControl2, DictAnswers2, DictFeedback2], [DictControl3, DictAnswers3, DictFeedback3], [DictControl4, DictAnswers4, DictFeedback4], [DictControl5, DictAnswers5, DictFeedback5]]
# DictatorEnd = (InstructionsFrame, {"text": "{}", "height": 8, "update": ["dictatorEnd"]})
# DictatorFeelings2 = (DictatorFeelings, {"round": 2})


TrustResult = (InstructionsFrame, {"text": "{}", "update": ["trustResult"]})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,         
         Trust,
         WaitTrust,
         TrustResult,         
         Trust,
         WaitTrust,
         TrustResult
         ])