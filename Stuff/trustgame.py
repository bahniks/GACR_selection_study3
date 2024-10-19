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
from constants import TESTING, URL, TRUST, TOKEN
from questionnaire import Questionnaire
from cheating import Login


################################################################################
# TEXTS
instructionsT1 = """Vaše rozhodnutí v této úloze budou mít finanční důsledky pro Vás a pro dalšího přítomného účastníka v laboratoři. Pozorně si přečtěte pokyny, abyste porozuměl(a) studii a své roli v ní. 

V rámci této úlohy jste spárován(a) s dalším účastníkem studie. Oba obdržíte {} Kč.

Bude Vám náhodně přidělena jedna ze dvou rolí: budete buď hráčem A, nebo hráčem B. Oba účastníci ve dvojici budou vždy informováni o rozhodnutích druhého hráče.

<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí a obdrží ji hráč B.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze, tedy úvodních {} Kč a ztrojnásobenou částku poslanou hráčem A.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role.

Jakmile oba odešlete své odpovědi, dozvíte se jaká byla Vaše role a jaký je celkový výsledek rozhodnutí Vás a druhého účastníka. 

Tuto úlohu budete hrát v rámci studie celkem čtyřikrát, vždy s různými účastníky studie, a Vaše odměna za úlohu bude záviset na jedné, náhodně vylosované hře z těchto čtyř. Ostatní hry Vaší konečnou odměnu nijak neovlivní."""


instructionsT2 = """Nyní obdržíte opět úlohu, v které jste spárován(a) s jiným účastníkem studie a můžete si posílat peníze.
<b>{}</b>
V tomto kole oba obdržíte {} Kč.

Podobně jako v předchozím kole úlohy:
<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí a obdrží ji hráč B.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze, tedy úvodních {} Kč a ztrojnásobenou částku poslanou hráčem A.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role.

Jakmile oba odešlete své odpovědi, dozvíte se jaká byla Vaše role a jaký je celkový výsledek rozhodnutí Vás a druhého účastníka. 

Vaše odměna za úlohu bude záviset na jedné, náhodně vylosované hře z celkových čtyř, které budete hrát.

Svou volbu učiňte posunutím modrých ukazatelů níže."""


rewardTrustText = """
Tento účastník studie v minulém kole hry s házením kostkou dostal odměnu {} Kč za {} správných odhadů.
Tento účastník podobně ví, že jste v minulém kole hry s házením kostkou dostal(a) odměnu {} za {} správných odhadů.
"""
versionTrustText = """
Tento účastník studie si v minulém kole hry s házením kostkou vybral {}.
Tento účastník podobně ví, že jste si v minulém kole hry s házením kostkou vybral(a) verzi {}.
"""
after_text = "PO verzi hry, ve které se uvádí, zda byla předpověď správná, či nikoliv, až poté, co se zobrazí výsledek hodu kostkou"
before_text = "PŘED verzi hry, ve které se uvádí předpověď před tím, než se zobrazí výsledek hodu kostkou"
version_rewardTrustText = """
Tento účastník studie si v minulém kole hry s házením kostkou vybral {}, a dostal odměnu {} Kč za {} správných odhadů.
Tento účastník podobně ví, že jste si v minulém kole hry s házením kostkou vybral(a) verzi {} a dostal(a) odměnu {} za {} správných odhadů.
"""


instructionsT3 = instructionsT2


instructionsT4 = """Nyní obdržíte opět úlohu, v které jste spárováni s jiným účastníkem studie a můžete si posílat peníze.
<b>{}</b>
V tomto kole oba obdržíte {} Kč.

Podobně jako v předchozích kolech úlohy:
<i>Hráč A:</i> Má možnost poslat hráči B od 0 do {} Kč (po {} Kč). Poslaná částka se ztrojnásobí a obdrží ji hráč B.
<i>Hráč B:</i> Může poslat zpět hráči A jakékoli množství peněz získaných v této úloze, tedy úvodních {} Kč a ztrojnásobenou částku poslanou hráčem A.

Předem nebudete vědět, jaká je Vaše role a uvedete tedy rozhodnutí pro obě role.

Jakmile oba odešlete své odpovědi, dozvíte se jaká byla Vaše role a jaký je celkový výsledek rozhodnutí Vás a druhého účastníka. 

Vaše odměna za úlohu bude záviset na jedné, náhodně vylosované hře z celkových čtyř, které budete hrát.

Svou volbu učiňte posunutím modrých ukazatelů níže."""


contributedText = f"Tento účastník se rozhodl nepřispět {TOKEN} Kč charitě, když měl možnost."
notContributedText = f"Tento účastník se rozhodl přispět {TOKEN} Kč charitě, když měl možnost."
controlText = ""


trustControl1 = "Jaká je role hráče A a hráče B ve studii?"
trustAnswers1 = ["Hráč A rozhoduje, kolik vezme hráči B peněz a hráč B se rozhoduje, kolik vezme hráči A peněz na oplátku.",
"Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči B\njakékoli množství dostupných peněz zpět.", 
"Hráči A a B se rozhodují, kolik si navzájem pošlou peněz. Transfer peněz mezi nimi je dán rozdílem poslaných peněz.", 
"Hráč A se rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí. Hráč B může vzít hráči A\njakékoli množství zbylých peněz."]
trustFeedback1 = ["Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči B jakékoli množství dostupných peněz zpět.", 
"Správná odpověď.", "Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči B jakékoli množství dostupných peněz zpět.", 
"Chybná odpověď. Hráč A rozhoduje, kolik hráči B pošle peněz. Poslané peníze se ztrojnásobí a hráč B může poslat hráči B jakékoli množství dostupných peněz zpět."]


trustControl2 = "Jakou odměnu obdrží hráč A, pokud hráči B pošle 40 Kč a ten mu pošle zpět 60 Kč?"
trustAnswers2 = ["40 Kč (100 - 3 × 40 + 60)", "120 Kč (100 - 40 + 60)", "160 Kč (100 + 3 × (60 - 40))", "240 Kč (100 - 40 + 3 × 60)"]
trustFeedback2 = ["Chybná odpověď. Hráč A obdrží 100 Kč, z kterých 40 Kč pošle hráči B, zbyde mu tedy 60 Kč, ke kterým obdrží od hráče B 60 Kč, tj. na konec obdrží 120 Kč (100 - 40 + 60).", "Správná odpověď.", "Chybná odpověď. Hráč A obdrží 100 Kč, z kterých 40 Kč pošle hráči B, zbyde mu tedy 60 Kč, ke kterým obdrží od hráče B 60 Kč, tj. na konec obdrží 120 Kč (100 - 40 + 60).", "Chybná odpověď. Hráč A obdrží 100 Kč, z kterých 40 Kč pošle hráči B, zbyde mu tedy 60 Kč, ke kterým obdrží od hráče B 60 Kč, tj. na konec obdrží 120 Kč (100 - 40 + 60)."]


trustControl3 = "Jakou odměnu obdrží hráč B, pokud hráč A pošle 40 Kč a hráč B mu pošle zpět 60 Kč?"
trustAnswers3 = ["80 Kč (100 + 40 - 60)", "160 Kč (100 + 3 × 40 - 60)", "240 Kč (100 + 3 × 60 - 40)", "280 Kč (100 + 3 × 40 + 60)"]
trustFeedback3 = ["Chybná odpověď. Hráč B obdrží 100 Kč, ke kterým obdrží 120 Kč od hráče A (poslaných 40 Kč se ztrojnásobí) a následně pošle hráči A 60 Kč, tj. na konec obdrží 160 Kč (100 + 3 × 40 - 60).", "Správná odpověď.", "Chybná odpověď. Hráč B obdrží 100 Kč, ke kterým obdrží 120 Kč od hráče A (poslaných 40 Kč se ztrojnásobí) a následně pošle hráči A 60 Kč, tj. na konec obdrží 160 Kč (100 + 3 × 40 - 60).", "Chybná odpověď. Hráč B obdrží 100 Kč, ke kterým obdrží 120 Kč od hráče A (poslaných 40 Kč se ztrojnásobí) a následně pošle hráči A 60 Kč, tj. na konec obdrží 160 Kč (100 + 3 × 40 - 60)."]



wait_text = "Prosím počkejte na druhého hráče."



trustResultTextA = """Náhodně Vám byla vybrána role hráče A.

<b>Rozhodl(a) jste se poslat {} Kč.</b>
Tato částka byla ztrojnásobena na {} Kč.
<b>Ze svých {} Kč Vám poslal hráč B {} Kč.</b>

<b>V této úloze jste tedy získal(a) {} Kč a hráč B {} Kč.</b>
Tuto odměnu získáte, pokud bude toto kolo hry vylosováno pro vyplacení.{}
"""

trustResultTextB = """Náhodně Vám byla vybrána role hráče B.

<b>Hráč A se rozhodl(a) poslat {} Kč.</b>
Tato částka byla ztrojnásobena na {} Kč.
<b>Ze svých {} Kč jste poslal(a) hráči B {} Kč.</b>

<b>V této úloze jste tedy získal(a) {} Kč a hráč A {} Kč.</b>
Tuto odměnu získáte, pokud bude toto kolo hry vylosováno pro vyplacení.{}
"""

diceText = "\n\nNyní budete pokračovat v úloze s odhadováním hodů kostky."

checkButtonText = "Rozhodl(a) jsem se u všech možností"


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
        self.maximum = maximum

        self.valueVar = StringVar()
        self.valueVar.set("0")

        ttk.Style().configure("TScale", background = "white")

        self.value = ttk.Scale(self, orient = HORIZONTAL, from_ = 0, to = maximum, length = 400,
                            variable = self.valueVar, command = self.changedValue)
        self.value.bind("<Button-1>", self.onClick)

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


    def onClick(self, event):
        click_position = event.x
        newValue = int((click_position / self.value.winfo_width()) * self.value['to'])
        self.changedValue(newValue)
        self.update()


    def changedValue(self, value):           
        value = str(min([max([eval(str(value)), 0]), self.maximum]))
        self.valueVar.set(value)
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
            endowments = list(map(TRUST.__getitem__, [1,2,0,1])) if root.status["incentive_order"] == "high-low" else list(map(TRUST.__getitem__, [1,0,2,1]))
            root.status["endowments"] = endowments

        endowment = root.status["endowments"][root.status["trustblock"] - 1]

        if root.status["trustblock"] == 1:            
            text = eval("instructionsT" + str(root.status["trustblock"])).format(endowment, endowment, int(endowment/5), endowment)
            text += "\n\nSvou volbu učiňte posunutím modrých ukazatelů níže."
        else:
            _, otherwins, otherreward, otherversion = root.status["outcome" + str(root.status["trustblock"] + 2)].rstrip("_True").split("|") 
            selectedVersion = after_text if "treatment" in otherversion else before_text
            prevblock = root.status["block"] - 1
            yourversion = "PO" if "treatment" in root.status["conditions"][prevblock-1] else "PŘED"
            if root.status["condition"] == "version":
                conditionText = versionTrustText.format(selectedVersion, yourversion)
            elif root.status["condition"] == "reward":
                reward = sum([i*3 + 3 for i in range(12)][:root.wins[prevblock]])
                conditionText = rewardTrustText.format(otherreward, otherwins, reward, root.wins[prevblock])
            elif root.status["condition"] == "version_reward":
                wins = root.wins[prevblock]
                reward = sum([i*3 + 3 for i in range(12)][:wins])                
                conditionText = version_rewardTrustText.format(selectedVersion, otherreward, otherwins, yourversion, reward, wins)
            elif root.status["condition"] == "control":
                conditionText = ""
            if root.status["trustblock"] == 4:
                conditionText += eval(otherversion.split("_")[1] + "Text")
            text = eval("instructionsT" + str(root.status["trustblock"])).format(conditionText, endowment, endowment, int(endowment/5), endowment)

        height = 24
        width = 100

        super().__init__(root, text = text, height = height, font = 15, width = width)

        self.labA = ttk.Label(self, text = "Pokud budu hráč A", font = "helvetica 15 bold", background = "white")
        self.labA.grid(column = 0, row = 2, columnspan = 3, pady = 10)        

        # ta x-pozice tady je hnusny hack, idealne by se daly texty odmen vsechny sem ze slideru
        self.labR = ttk.Label(self, text = "Rozdělení odměn po tomto kroku", font = "helvetica 15 bold", background = "white", anchor = "center", width = 30)
        self.labR.grid(column = 1, row = 2, pady = 5, sticky = E)

        self.labX = ttk.Label(self, text = "Finální rozdělení odměn", font = "helvetica 15 bold", background = "white", anchor = "center", width = 28)
        self.labX.grid(column = 1, row = 5, pady = 5, sticky = E)

        self.frames = {}
        for i in range(7):            
            if i != 6:
                text = "Pokud hráč A pošle {} Kč, pošlu hráči A zpět:".format(i*20)
                ttk.Label(self, text = text, font = "helvetica 15", background = "white").grid(column = 0, row = 6 + i, pady = 1, sticky = E)
                player = "B"
            else:
                ttk.Label(self, text = "Pošlu hráči B:", font = "helvetica 15", background = "white").grid(column = 0, row = 3, pady = 1, sticky = E)            
                player = "A"
            maximum = int(i * 3 * endowment / 5 + endowment) if i < 6 else endowment            
            self.frames[i] = ScaleFrame(self, maximum = maximum, player = player, returned = int(i*endowment/5), endowment = endowment)
            row = 6 + i if i < 6 else 3
            self.frames[i].grid(column = 1, row = row, pady = 1)
        
        self.labB = ttk.Label(self, text = "Pokud budu hráč B", font = "helvetica 15 bold", background = "white")
        self.labB.grid(column = 0, row = 5, columnspan = 3, pady = 10)

        self.checkVar = BooleanVar()
        ttk.Style().configure("TCheckbutton", background = "white", font = "helvetica 15")
        self.checkBut = ttk.Checkbutton(self, text = checkButtonText, command = self.checkbuttoned, variable = self.checkVar, onvalue = True, offvalue = False)
        self.checkBut.grid(row = 18, column = 0, columnspan = 3)

        self.next.grid(column = 0, row = 19, columnspan = 3, pady = 5, sticky = N)            
        self.next["state"] = "disabled"
        
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

    def checkbuttoned(self):
        self.next["state"] = "normal" if self.checkVar.get() else "disabled"

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
        d = [self.id, str(block + 2), self.root.status["trust_pairs"][block-1], list(self.root.status["trust_roles"])[block-1], self.root.status["condition"], self.root.status["incentive_order"], self.root.status["endowments"][block-1]]
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
        t0 = perf_counter() - 4
        #count = 0
        while True:
            self.update()
            if perf_counter() - t0 > 5:
                t0 = perf_counter()
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
                        reward = endowment - sentA + sentB if self.root.status["trust_roles"][block-1] == "A" else endowment + sentA*3 - sentB    
                        self.root.texts["trust"] = str(reward)

                    dice = "" if block == 4 else diceText

                    if self.root.status["trust_roles"][block - 1] == "A": 
                        text = trustResultTextA.format(sentA, sentA*3, endowment + sentA*3, sentB, endowment - sentA + sentB, endowment + sentA*3 - sentB, dice)
                    else:
                        text = trustResultTextB.format(sentA, sentA*3, endowment + sentA*3, sentB, endowment + sentA*3 - sentB, endowment - sentA + sentB, dice)
                    self.root.texts["trustResult"] = text

                    self.write(response)
                    self.progressBar.stop()
                    self.nextFun()  
                    return
            #count += 1
            #sleep(0.1)

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

       

# DictatorEnd = (InstructionsFrame, {"text": "{}", "height": 8, "update": ["dictatorEnd"]})
# DictatorFeelings2 = (DictatorFeelings, {"round": 2})


TrustResult = (InstructionsFrame, {"text": "{}", "update": ["trustResult"]})

controlTexts = [[trustControl1, trustAnswers1, trustFeedback1], [trustControl2, trustAnswers2, trustFeedback2], [trustControl3, trustAnswers3, trustFeedback3]]
InstructionsTrust = (InstructionsAndUnderstanding, {"text": instructionsT1.format(TRUST[1], TRUST[1], int(TRUST[1]/5), TRUST[1]) + "\n\n", "height": 23, "width": 100, "name": "Trust Control Questions", "randomize": False, "controlTexts": controlTexts, "fillerheight": 300, "finalButton": "Pokračovat k volbě"})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    from cheating import OutcomeWait
    GUI([Login,    
         OutcomeWait,
         InstructionsTrust,
         Trust,
         WaitTrust,
         TrustResult,
         OutcomeWait,
         Trust,
         WaitTrust,
         TrustResult
         ])