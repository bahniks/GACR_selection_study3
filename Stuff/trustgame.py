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
from constants import TESTING, URL
from questionnaire import Questionnaire
from cheating import Login


################################################################################
# TEXTS
instructions3 = """Vaše rozhodnutí v této úloze budou mít finanční důsledky pro Vás a pro dalšího přítomného účastníka. Pozorně si přečtěte pokyny, abyste porozuměli studii a své roli v ní. 

V rámci této úlohy jste spárováni s jiným účastníkem studie. Oba obržíte 100 Kč.

Bude Vám náhodně přidělena jedna ze dvou rolí: budete buď hráčem A, nebo hráčem B. Oba účastníci ve dvojici budou vždy informováni o rozhodnutích toho druhého.

<i>Hráč A:</i> Má možnost poslat hráči B od 0 do 100 Kč (v krocích po 20 Kč). Poslaná částka se ztrojnásobí.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role.

Jakmile oba odešlete své odpovědi, dozvíte se jaká byla Vaše role a jaký je celkový výsledek rozhodnutí Vás a druhého účastníka. 
Tuto úlohu budete hrát v rámci studie celkem čtyřikrát a Vaše odměna za úlohu bude záviset na jedné, náhodně vylosované hře z těchto čtyř."""


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
    def __init__(self, root, font = 15, maximum = 0):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.parent = root
        self.root = root.root
        self.rounding = maximum / 5

        self.valueVar = StringVar()
        self.valueVar.set("0")

        ttk.Style().configure("TScale", background = "white")

        self.value = ttk.Scale(self, orient = HORIZONTAL, from_ = 0, to = maximum, length = 500,
                            variable = self.valueVar, command = self.changedValue)

        self.totalText = "      Hráč A: {} Kč   Já: {} Kč"

        self.valueLab = ttk.Label(self, textvariable = self.valueVar, font = "helvetica {}".format(font), background = "white", width = 3, anchor = "e")
        self.currencyLab = ttk.Label(self, text = "Kč", font = "helvetica {}".format(font), background = "white")
        self.totalLab = ttk.Label(self, text = self.totalText.format(0,0), font = "helvetica {}".format(font), background = "white")

        self.value.grid(column = 1, row = 1, padx = 15)
        self.valueLab.grid(column = 3, row = 1)        
        self.currencyLab.grid(column = 4, row = 1)
        self.totalLab.grid(column = 5, row = 1, padx = 10)


    def changedValue(self, value):                
        self.valueVar.set(str(int(round(eval(self.valueVar.get())/self.rounding, 0)*self.rounding)))
        self.parent.checkAnswers()
              


class Trust(InstructionsFrame):
    def __init__(self, root):
        
        # to do
        text = instructions3 # updatovat dle kola, dodelat dalsi texty
        height = 20
        width = 100

        super().__init__(root, text = text, height = height, font = 15, width = width)

        self.labA = ttk.Label(self, text = "Pokud budu hráč A", font = "helvetica 15 bold", background = "white")
        self.labA.grid(column = 0, row = 2, columnspan = 3, pady = 10)

        self.labR = ttk.Label(self, text = "Odměna", font = "helvetica 15 bold", background = "white")
        self.labR.grid(column = 1, row = 2, pady = 10, sticky = E)

        self.frames = {}
        for i in range(7):
            if i != 6:
                text = "Pokud hráč A pošle {} Kč:".format(i*20)
                ttk.Label(self, text = text, font = "helvetica 15", background = "white").grid(column = 0, row = 6 + i, pady = 1, sticky = E)
            else:
                ttk.Label(self, text = "Pošlu:", font = "helvetica 15", background = "white").grid(column = 0, row = 3, pady = 1, sticky = E)
            maximum = i * 3 * 100 / 5 + 100 if i < 6 else 100
            self.frames[i] = ScaleFrame(self, maximum = maximum)
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

    def checkAnswers(self):        
        for frame in self.frames.values():
            pass
            # if not frame.messageVar.get():
            #     break
        else:
            self.next["state"] = "normal"

    def nextFun(self):
        self.send()        
        self.write()
        super().nextFun()

    def send(self):
        if self.root.status["dictatorRole"] == "A": 
            data = {'id': self.id, 'round': "dictator1A", 'offer': self.scaleFrame.valueVar.get()}
        else:            
            self.response = "_".join([frame.getData() for frame in self.frames.values()])
            data = {'id': self.id, 'round': "dictator1B", 'offer': self.response}
        self.sendData(data)

    def write(self):
        self.file.write("Dictator" + self.root.status["dictatorRole"] + "\n")
        if self.root.status["dictatorRole"] == "A":
            self.file.write(self.id  + "\t1\t" + self.scaleFrame.valueVar.get())
            if URL == "TEST":
                self.root.status["dictatorTestTook"] = self.scaleFrame.valueVar.get()
        else:
            self.file.write(self.id + "\t" + self.response.replace("_", "\t").replace("|", "\t"))
            if URL == "TEST":
                self.root.status["dictatorTestResponse"] = self.response
        self.file.write("\n\n")




class WaitTrust(InstructionsFrame):
    def __init__(self, root, what = "pairing"):
        super().__init__(root, text = wait_text, height = 3, font = 15, proceed = False, width = 45)
        self.what = what
        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def checkUpdate(self):
        count = 0
        while True:
            self.update()
            if count % 50 == 0:                
                data = urllib.parse.urlencode({'id': self.id, 'round': "dictator", 'offer': self.what})                
                data = data.encode('ascii')
                if URL == "TEST":
                    if self.what == "pairing":
                        condition = random.choice(["forgive-ignore", "ignore-punish", "forgive-punish"])
                        condition = "forgive-punish" # for testing
                        role = "B" # for testing
                        role = random.choice(["A", "B"])                        
                        pair = random.randint(1,20)
                        response = str(pair) + "_" + role + "_" + condition
                    elif self.what == "decision1":                                                                        
                        pair = random.randint(1,20)
                        if self.root.status["dictatorRole"] == "A":
                            took = self.root.status["dictatorTestTook"]
                            decision = random.choice(self.root.status["dictatorCondition"].split("-"))
                            message = str(random.randint(1,2))
                            money = 0 if decision == "ignore" else random.randint(0,5) * 2                       
                        else:
                            took = random.randint(0, 5) * 2
                            _, decision, message, money = self.root.status["dictatorTestResponse"].split("_")[took//2].split("|")
                        response = "_".join(map(str, [pair, took, decision, message, money]))    
                    elif self.what == "decision2":     
                        pair = random.randint(1,20)
                        if self.root.status["dictatorRole"] == "A":
                            took = self.root.status["dictatorTestTook2"]
                        else:
                            took = random.randint(0, 10) * 2                
                        response = "_".join(map(str, [pair, took]))
                else:
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8")       
                    except Exception as e:
                        continue
                if response:                  
                    if self.what == "pairing":
                        pair, role, condition = response.split("_")                                 
                        self.root.status["dictatorCondition"] = condition
                        self.root.texts["firstOption"] = eval(condition.split("-")[0] + "Info")
                        self.root.texts["secondOption"] = eval(condition.split("-")[1] + "Info")
                        self.root.status["dictatorRole"] = role
                        self.root.status["dictatorPair"] = pair                 
                    elif self.what == "decision1":   
                        pair, took, decision, message, money = response.split("_")
                        message = eval(decision + "Message" + message)
                        took, money = int(took), int(money)
                        result = eval(decision + "Result")
                        a = 20 + took
                        b = 20 - took
                        if decision == "ignore":
                            result = result.format(message)
                        elif decision == "punish":
                            result = result.format(eval(decision + self.root.status["dictatorRole"]), message, money)
                            a -= money
                            b -= money
                        elif decision == "forgive":
                            result = result.format(eval(decision + self.root.status["dictatorRole"]), money, message)
                            a += money
                            b -= money
                        self.root.status["dictatorRound1AReward"] = a
                        self.root.status["dictatorRound1BReward"] = b
                        if self.root.status["dictatorRole"] == "A":
                            text = dictatorResultTextA.format(took, result, a, b)
                        else:
                            text = dictatorResultTextB.format(took, result, b, a)
                        self.root.texts["dictatorResult"] = text
                    elif self.what == "decision2":   
                        pair, took = response.split("_")
                        took = int(took)                        
                        a = 20 + took
                        b = 20 - took                        
                        aTotal = self.root.status["dictatorRound1AReward"] + a
                        bTotal = self.root.status["dictatorRound1BReward"] + b
                        if self.root.status["dictatorRole"] == "A":
                            text = finalTextA.format(took, a, b, aTotal, bTotal)
                            self.root.texts["dictator"] = aTotal
                        else:                            
                            text = finalTextB.format(took, b, a, bTotal, aTotal)
                            self.root.texts["dictator"] = bTotal
                        self.root.texts["dictatorEnd"] = text
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
        if self.what == "pairing":
            self.file.write("Pairing" + "\n")
        elif self.what == "decision1":
            self.file.write("Dictator Results 1" + "\n")
        elif self.what == "decision2":
            self.file.write("Dictator Results 2" + "\n")
        self.file.write(self.id + "\t" + response.replace("_", "\t") + "\n\n") 

       

               

class TrustResult(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = "{}", height = 19, update = ["dictatorResult"])

        if self.root.status["dictatorRole"] == "A":
            self.scaleFrame = ScaleFrame(self, round = 2)       
            self.scaleFrame.grid(column = 1, row = 3, pady = 10, sticky = N)        
            self.next.grid(column = 1, row = 4)
            self.rowconfigure(0, weight = 1)        
            self.rowconfigure(1, weight = 0) 
            self.rowconfigure(2, weight = 0) 
            self.rowconfigure(3, weight = 0) 
            self.rowconfigure(4, weight = 1)       

    def checkAnswers(self):
        pass 

    def send(self):        
        if self.root.status["dictatorRole"] == "A": 
            data = {'id': self.id, 'round': "dictator2A", 'offer': self.scaleFrame.valueVar.get()}        
            self.sendData(data)

    def nextFun(self):
        self.send()      
        self.write()  
        super().nextFun()

    def write(self):
        if self.root.status["dictatorRole"] == "A":
            self.file.write("Dictator2\n")
            self.file.write(self.id  + "\t2\t" + self.scaleFrame.valueVar.get())
            self.file.write("\n\n")
            if URL == "TEST":
                self.root.status["dictatorTestTook2"] = self.scaleFrame.valueVar.get()        
            


# class InstructionsDictator(InstructionsAndUnderstanding):
#     def __init__(self, root):
#         out = ["forgive-ignore", "ignore-punish", "forgive-punish"].index(root.status["dictatorCondition"]) + 2
#         controlTexts = controlTexts1
#         controlTexts.pop(out)
        
#         super().__init__(root, text = instructions, height = 31, width = 110, name = "Dictator Control Questions", randomize = False, controlTexts = controlTexts, update = ["firstOption", "secondOption"])    






# controlTexts1 = [[DictControl1, DictAnswers1, DictFeedback1], [DictControl2, DictAnswers2, DictFeedback2], [DictControl3, DictAnswers3, DictFeedback3], [DictControl4, DictAnswers4, DictFeedback4], [DictControl5, DictAnswers5, DictFeedback5]]
# WaitResult1 = (WaitDictator, {"what": "decision1"})
# WaitResult2 = (WaitDictator, {"what": "decision2"})
# DictatorEnd = (InstructionsFrame, {"text": "{}", "height": 8, "update": ["dictatorEnd"]})
# DictatorFeelings2 = (DictatorFeelings, {"round": 2})



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,         
         Trust,
         WaitTrust,
         TrustResult
         ])