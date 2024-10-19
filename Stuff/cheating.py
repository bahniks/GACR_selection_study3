#! python3
# -*- coding: utf-8 -*- 

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import perf_counter, sleep
from collections import defaultdict

import random
import os
import urllib.request
import urllib.parse

from common import ExperimentFrame, InstructionsFrame, Measure, MultipleChoice, InstructionsAndUnderstanding, OneFrame, Question, TextArea
from gui import GUI
from constants import TESTING, URL, TOKEN


################################################################################
# TEXTS

# PRVNÍ BLOK
intro_block_1 = """V následujícím úkolu budete hádat, jestli na virtuální kostce (generátor náhodných čísel) na Vašem počítači padne liché, nebo sudé číslo. Každé z čísel 1, 2, 3, 4, 5 a 6 může padnout se stejnou pravděpodobností. Lichá čísla jsou 1, 3 a 5. Sudá čísla jsou 2, 4 a 6. 

Úkol je rozdělen do šesti samostatných bloků a každý blok sestává z dvanácti kol. V každém kole budete hádat výsledek jednotlivých hodů kostkou. Bloky se odlišují pravidly, dle nichž budete hádat hody kostkou. Pravidla níže však platí pro všech šest bloků.

Uhodnete-li první hod v daném bloku, získáte 3 Kč, uhodnete-li další, získáte za něj dalších 6 Kč, uhodnete-li další hod, získáte za něj dalších 9 Kč a tak dále. Za každý další uhodnutý hod získáte navíc částku o 3 Kč vyšší, než byla předchozí odměna. Pokud tedy uhodnete všech 12 hodů v daném bloku, za poslední dvanáctý uhodnutý hod získáte 36 Kč a celkem získáte 264 Kč. Celkové odměny za různé množství správných odhadů jsou zobrazeny v této tabulce:
<c>
Správných odhadů |  0 |   1 |   2 |   3 |   4 |   5 |   6 |   7 |   8 |   9 |  10 |  11 |  12 |
-----------------------------------------------------------------------------------------------
Odměna v Kč      |  0 |   3 |   9 |  18 |  30 |  45 |  63 |  84 | 112 | 144 | 180 | 220 | 264 |
</c>
Po skončení studie bude jeden blok náhodně vylosován. Obdržíte peníze, které jste vydělali pouze v tomto vylosovaném bloku. Pokud správně uhodnete všech dvanáct hodů v daném bloku, a tento blok bude později vylosován, obdržíte 264 Kč. Vaše výsledky v ostatních blocích nijak neovlivní množství peněz, které obdržíte.

Abychom ověřili, že rozumíte instrukcím, odpovězte prosím na kontrolní otázky:"""


intro_control1 = 'Které tvrzení o úkolu je pravdivé?' 
intro_answers1 = ['Pravděpodobnost správného odhadu v každém kole je 50%.', 'V každém bloku úkolu učiníte deset odhadů.', 'Odměna za úkol je dána součtem správných odhadů v šesti blocích úkolu.', 'Jakmile úkol dokončíte, experimentátor Vám za něj vyplatí odměnu.'] 
intro_feedback1 = ['Ano, budete odhadovat jednu ze dvou stejně pravděpodobných možností.', 'Ne, každý blok sestává z dvanácti kol.', 'Ne, odměna závisí pouze na počtu správných odhadů v jednom náhodně vylosovaném bloku.', 'Ne, odměna bude vyplacena až za všechny části studie dohromady po jejím skončení.']

intro_control2 = 'Kolik obdržíte za úkol peněz, pokud bude vylosován blok, kde uhodnete dohromady 4 hody?' 
intro_answers2 = ['18 Kč (0 + 3 + 6 + 9)', '27 Kč (6 + 6 + 9 + 9)', '30 Kč (3 + 6 + 9 + 12)', '48 Kč (4 x 12)'] 
intro_feedback2 = ['Ne, obdželi byste 30 Kč. Za první hod 3 Kč a za každý další o 3 Kč více (tj. 3 + 6 + 9 + 12).', 'Ne, obdželi byste 30 Kč. Za první hod 3 Kč a za každý další o 3 Kč více (tj. 3 + 6 + 9 + 12).', 'Ano, obdželi byste 30 Kč.', 'Ne, obdželi byste 30 Kč. Za první hod 3 Kč a za každý další o 3 Kč více (tj. 3 + 6 + 9 + 12).']


# ÚLOHA
continuetext = "Pokračovat"
oddtext = "Liché (1, 3 nebo 5)"
eventext = "Sudé (2, 4 nebo 6)"
rolltext = "Hodit kostkou"
correcttext = "Správně"
incorrecttext = "Špatně"    
predictiontext = "Zvolil/a jsem, jestli na kostce padne liché, nebo sudé číslo"

treatmenttext = '''Blok {}, Kolo {}

Máte za úkol uhodnout, zda na kostce padne liché, nebo sudé číslo. Nyní prosím zvolte, zda v následujícím hodu padne liché, nebo sudé číslo, zapamatujte si svoji volbu a poté klikněte na tlačítko "Hodit kostkou".'''

treatmenttext2 = "Zvolte, zda jste hádal(a) správně a vydělal(a) v tomto kole {} Kč, nebo zda jste hádal(a) špatně a nevydělal(a) jste v tomto kole nic."


controltext = """Blok {}, Kolo {}

Máte za úkol uhodnout, zda na kostce padne liché, nebo sudé číslo. Nyní prosím zvolte, zda v následujícím hodu padne liché, nebo sudé číslo, a poté klikněte na tlačítko "Hodit kostkou"."""

controltext2 = "V tomto kole byla Vaše předpověď {}"
wintext = "správná a vydělal(a) jste {} Kč."
losstext = "špatná a nevydělal(a) jste možných {} Kč."


# DRUHÝ BLOK
intro_block_2 = """
Toto je konec prvního bloku. Pokud bude tento blok vylosován, obdržíte {} Kč. Nyní začne druhý blok s dvanácti koly.
"""


# TŘETÍ BLOK
intro_block_3 = """Toto je konec druhého bloku o dvanácti kolech. Pokud bude tento blok vylosován, obdržíte {} Kč.

Jak jste zaznamenal(a), úkol měl dvě verze:
<b>Verzi “PŘED”</b>, ve které uvádíte předpovědi před hodem kostkou. Po zvolení možnosti vidíte výsledek hodu a dozvíte se, zda jste uhodl(a), či nikoliv a kolik jste vydělal(a).
<b>Verzi “PO”</b>, ve které uvádíte, zda jste uhodl(a), či nikoliv a kolik jste vydělal(a), až poté, co vidíte výsledek hodu kostkou.

Nyní Vás čeká třetí blok s dvanácti koly. V tomto bloku si můžete vybrat, jestli budete hrát verzi “PŘED” nebo “PO”.

Chcete hrát verzi “PŘED” nebo “PO”?
"""

info_block_3 = """
Toto je konec třetího bloku. Pokud bude tento blok vylosován, obdržíte {} Kč. 

Nyní obdržíte jinou úlohu. Přečtěte si pozorně instrukce.

Tato úloha bude pokračovat následně čtvrtým blokem s dvanácti koly.
"""


# ČTVRTÝ BLOK
intro_block_4 = """Nyní Vás čeká čtvrtý blok s dvanácti koly. V tomto bloku si opět můžete vybrat, jestli budete hrát verzi “PŘED” nebo “PO”.

<b>Ve verzi “PŘED”</b> uvádíte předpovědi před hodem kostkou. Po zvolení možnosti vidíte výsledek hodu a dozvíte se, zda jste uhodl(a), či nikoliv a kolik jste vydělal(a).
<b>Ve verzi “PO”</b> uvádíte, zda jste uhodl(a), či nikoliv a kolik jste vydělal(a), až poté, co vidíte výsledek hodu kostkou.

<b>Po tomto čtvrtém bloku opět budete hrát úlohu s dělením peněz (mezi hráče A a hráče B), kterou jste zrovna dokončil(a). 
Částka přidělená oběma hráčům bude ovšem {} Kč</b> a budete spárován(a) s jiným účastníkem studie. 

{}

Chcete hrát verzi “PŘED” nebo “PO”?
"""

versionText = "<b>Před touto úlohou se tento účastník studie dozví, jakou verzi úlohy (“PŘED” nebo “PO”) jste si vybral(a) v tomto kole.</b> Vy budete podobně vědět, jakou verzi úlohy si vybral(a) on(a)."
rewardText = "<b>Před touto úlohou se tento účastník studie dozví, kolik správných odhadů jste učinil(a) v tomto kole (ve verzi “PŘED” nebo “PO”).</b> Vy budete podobně vědět, kolik správných odhadů učinil(a) on(a)."
version_rewardText = "<b>Před touto úlohou se tento účastník studie dozví, jakou verzi úlohy (“PŘED” nebo “PO”) jste si vybral(a) pro toto kolo a kolik správných odhadů jste v něm učinil(a).</b> Vy budete podobně vědět, jakou verzi úlohy si vybral(a) on(a) a kolik správných odhadů učinil(a)."
controlText = ""


controlManipulation = 'Jaké informace se o Vás dozví účastník studie, s kterým budete spárováni pro úlohu s dělením peněz?' 
answersManipulation = ['Jakou verzi úlohy s kostkami jste si vybral(a) pro toto kolo a kolik správných odhadů jste v něm učinil(a).', 'Jakou verzi úlohy s kostkami jste si vybral(a) pro toto kolo.', 'Kolik správných odhadů jste učinil(a) v tomto kole úlohy s kostkami.', 'Nebude mít o Vás žádné informace.'] 

correctFeedback = "Ano, bude vědět, "
incorrectFeedback = "Ne, bude vědět, "
correctFeedbackControl = "Ano, "
incorrectFeedbackControl = "Ne, "


# PÁTÝ BLOK
intro_block_5 = """Nyní Vás čeká pátý blok s dvanácti koly. V tomto bloku si opět můžete vybrat, jestli budete hrát verzi “PŘED” nebo “PO”.

<b>Ve verzi “PŘED”</b> uvádíte předpovědi před hodem kostkou. Po zvolení možnosti vidíte výsledek hodu a dozvíte se, zda jste uhodl(a), či nikoliv a kolik jste vydělal(a).
<b>Ve verzi “PO”</b> uvádíte, zda jste uhodl(a), či nikoliv a kolik jste vydělal(a), až poté, co vidíte výsledek hodu kostkou.

<b>Po tomto pátém bloku opět budete hrát úlohu s dělením peněz (mezi hráče A a hráče B). Částka přidělená oběma hráčům bude ovšem {} Kč</b> a budete spárováni s jiným účastníkem studie. 

{}

Chcete hrát verzi “PŘED” nebo “PO”?
"""


# ŠESTÝ BLOK
intro_block_6 = """Nyní Vás čeká šestý blok s dvanácti koly. V tomto bloku si opět můžete vybrat, jestli budete hrát verzi “PŘED” nebo “PO”.

<b>Ve verzi “PŘED”</b> uvádíte předpovědi před hodem kostkou. Po zvolení možnosti vidíte výsledek hodu a dozvíte se, zda jste uhodl(a), či nikoliv a kolik jste vydělal(a).
<b>Ve verzi “PO”</b> uvádíte, zda jste uhodl(a), či nikoliv a kolik jste vydělal(a), až poté, co vidíte výsledek hodu kostkou.

Po tomto šestém bloku opět budete hrát úlohu s dělením peněz (mezi hráče A a hráče B). <b>Částka přidělená oběma hráčům bude 100 Kč</b> a budete spárováni opět s jiným účastníkem studie. 

{}"""

tokenConditionText = f"\n\n<b>Kromě toho máte nyní možnost věnovat ze své výhry {TOKEN} Kč charitě Člověk v tísni, což se druhý hráč dozví před úlohou s dělením peněz (mezi hráče A a hráče B).</b>\n"

tokenContribution = f"Chcete věnovat ze své výhry {TOKEN} Kč charitě Člověk v tísni?"

version_choice = "Chcete hrát verzi “PŘED” nebo “PO”?"


# ČEKÁNÍ
wait_text = "Prosím počkejte na druhého hráče."



# KONEC
endtext = """Toto je konec posledního bloku. 
{}
Toto je konec úkolu s kostkou.
"""


# buttons
controlchoicetext = "PŘED"
treatmentchoicetext = "PO"



################################################################################






class Cheating(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        #######################
        # adjustable parameters
        self.trials = 12 if not TESTING else 2
        self.pause_after_roll = 0.5
        self.pause_before_trial = 0.2
        self.displayNum = self.createDots # self.createDots or self.createText
        self.fakeRolling = not TESTING
        self.diesize = 240
        self.rewards = [i*3 + 3 for i in range(self.trials)]
        #######################

        if not "block" in self.root.status:
            self.root.status["block"] = 1
            conditions = ["treatment", "control"]
            random.shuffle(conditions)  
            self.root.status["conditions"] = conditions
        self.blockNumber = self.root.status["block"]      
        
        self.condition = self.root.status["conditions"][self.blockNumber - 1]

        self.width = self.root.screenwidth
        self.height = self.root.screenheight

        self.file.write("Cheating {}\n".format(self.blockNumber))

        self.upperText = Text(self, height = 5, width = 65, relief = "flat", font = "helvetica 15",
                              wrap = "word")
        self.upperButtonFrame = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                                       background = "white", height = 100)
        self.die = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                          background = "white", width = self.diesize, height = self.diesize)
        self.bottomText = Text(self, height = 3, width = 65, relief = "flat", font = "helvetica 15",
                               wrap = "word")
        self.bottomButtonFrame = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                                        background = "white", height = 100)

        self.infoWinnings = ttk.Label(self, text = "", font = "helvetica 15",
                                      background = "white", justify = "right")
        self.fillerLeft = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                                 background = "white", width = 200, height = 1)
        self.fillerRight = Canvas(self, highlightbackground = "white", highlightcolor = "white",
                                  background = "white", width = 200, height = 1)
        self.infoWinnings.grid(row = 1, column = 2, sticky = NW)
        self.fillerLeft.grid(column = 0, row = 0)
        self.fillerRight.grid(column = 2, row = 0)

        self.upperText.grid(column = 1, row = 1)
        self.upperButtonFrame.grid(column = 1, row = 2)
        self.die.grid(column = 1, row = 3, pady = 40)
        self.bottomText.grid(column = 1, row = 4)
        self.bottomButtonFrame.grid(column = 1, row = 5)
        self._createFiller()

        self["highlightbackground"] = "white"
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 3)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 1)
        self.rowconfigure(4, weight = 1)
        self.rowconfigure(5, weight = 1)
        self.rowconfigure(6, weight = 4)

        self.currentTrial = 0

        ttk.Style().configure("TButton", font = "helvetica 15")

        if not hasattr(self.root, "wins"):
            self.root.wins = defaultdict(int)    

        self.responses = []


    def run(self):
        self.bottomText["state"] = "disabled"
        self.upperText["state"] = "disabled"
        if self.currentTrial < self.trials:
            self.currentTrial += 1
            self.startTrial()
        else:
            self.root.texts["win" + str(self.blockNumber)] = sum(self.rewards[:self.root.wins[self.blockNumber]])
            self.nextFun()


    def startTrial(self):
        self.time = perf_counter()
        self.showWinnings()
        self.upperPart()


    def _createFiller(self):
        self.fillerFrame = Canvas(self.bottomButtonFrame, highlightbackground = "white",
                                  highlightcolor = "white", background = "white", height = 100, width = 1)
        self.fillerFrame.grid(column = 0, row = 0, sticky = NS)


    def upperPart(self):
        self.upperText["state"] = "normal"
        if "treatment" in self.condition:
            ttk.Style().configure("TCheckbutton", background = "white", font = "helvetica 15")
            self.predictionVar = BooleanVar()
            self.predictionVar.set(False)
            self.upperText.insert("1.0", treatmenttext.format(self.blockNumber, self.currentTrial))
            self.predictedCB = ttk.Checkbutton(self.upperButtonFrame, text = predictiontext,
                                               command = self.checkbuttoned, variable = self.predictionVar,
                                               onvalue = True, offvalue = False)
            self.predictedCB.grid(row = 0, column = 1, pady = 15)
        elif "control" in self.condition:
            ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")
            self.predictionVar = StringVar()
            self.upperText.insert("1.0", controltext.format(self.blockNumber, self.currentTrial))
            self.evenButton = ttk.Radiobutton(self.upperButtonFrame, text = eventext, value = "even",
                                              variable = self.predictionVar, command = self.checked)
            self.oddButton = ttk.Radiobutton(self.upperButtonFrame, text = oddtext, value = "odd",
                                             variable = self.predictionVar, command = self.checked)
            self.evenButton.grid(row = 0, column = 2, padx = 10, pady = 15)
            self.oddButton.grid(row = 0, column = 0, padx = 10, pady = 15)

        self.rollButton = ttk.Button(self.upperButtonFrame, text = rolltext, command = self.roll,
                                     state = "disabled")
        self.rollButton.grid(row = 1, column = 1)
        self.upperText["state"] = "disabled"


    def checked(self):
        self.rollButton["state"] = "!disabled"


    def checkbuttoned(self):
        self.rollButton["state"] = "!disabled"
        self.predictedCB["state"] = "disabled"


    def bottomPart(self):
        self.bottomText["state"] = "normal"
        if "treatment" in self.condition:
            reward = self.rewards[self.root.wins[self.blockNumber]]
            text = treatmenttext2.format(reward)
            self.bottomText.insert("1.0", text)
            ttk.Style().configure("Green.TButton", foreground = "green")
            ttk.Style().configure("Red.TButton", foreground = "red")
            self.winButton = ttk.Button(self.bottomButtonFrame, text = correcttext,
                                        command = lambda: self.answer("win"), width = 18, style = "Green.TButton")
            self.lossButton = ttk.Button(self.bottomButtonFrame, text = incorrecttext,
                                         command = lambda: self.answer("loss"), width= 18, style = "Red.TButton")
            self.winButton.grid(row = 0, column = 0, padx = 30)
            self.lossButton.grid(row = 0, column = 2, padx = 30)
        elif "control" in self.condition:
            win = (self.response == "odd" and self.currentRoll in (1,3,5)) or (
                self.response == "even" and self.currentRoll in (2,4,6))
            if win:
                text = wintext.format(self.rewards[self.root.wins[self.blockNumber]])
                self.root.wins[self.blockNumber] += 1
            else:
                text = losstext.format(self.rewards[self.root.wins[self.blockNumber]])
            self.bottomText.insert("1.0", controltext2.format(text))
            self.showWinnings()
            self.continueButton = ttk.Button(self.bottomButtonFrame, text = continuetext, command = self.answer)
            self.continueButton.grid(row = 0, column = 1)
        self.bottomText["state"] = "disabled"


    def roll(self):
        self.firstResponse = perf_counter()
        if "treatment" in self.condition:
            self.response = "NA"    
        else:
            self.response = self.predictionVar.get()
            self.oddButton["state"] = "disabled"
            self.evenButton["state"] = "disabled"
        self.rollButton["state"] = "disabled"
        self.die.create_rectangle((5, 5, self.diesize - 5, self.diesize - 5),
                                  fill = "white", tag = "die", outline = "black", width = 5)
        # fake rolling
        if self.fakeRolling:
            for roll in range(random.randint(4,6)):         
                self.displayNum(self.diesize/2, self.diesize/2, random.randint(1, 6))
                self.update()
                sleep(0.2)
                self.die.delete("dots")
        self.currentRoll = random.randint(1, 6)
        self.displayNum(self.diesize/2, self.diesize/2, self.currentRoll)
        self.update()
        if not TESTING:
            sleep(self.pause_after_roll)
        self.beforeSecondResponse = perf_counter()
        self.bottomPart()


    def createDots(self, x0, y0, num):
        positions = {"1": [(0,0)],
                     "2": [(-1,-1), (1,1)],
                     "3": [(-1,-1), (0,0), (1,1)],
                     "4": [(-1,-1), (-1,1), (1,-1), (1,1)],
                     "5": [(-1,-1), (-1,1), (0,0), (1,-1), (1,1)],
                     "6": [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0)]}
        for x, y in positions[str(num)]:
            d = self.diesize/4
            coords = [x0 + x*d + d/3, y0 - y*d + d/3,
                      x0 + x*d - d/3, y0 - y*d - d/3]
            self.die.create_oval(tuple(coords), fill = "black", tag = "dots")


    def createText(self, x0, y0, num):
        self.die.create_text(x0, y0, text = str(num), font = "helvetica 70", tag = "die")

    def showWinnings(self):
        wins = self.root.wins[self.blockNumber]        
        self.infoWinnings["text"] = "Počet správných odhadů:\n{}".format(wins)        
        self.infoWinnings["text"] += "\n\nVaše současná výhra:\n{} Kč".format(sum(self.rewards[:wins]))

    def answer(self, answer = "NA"):
        t = perf_counter()
        if answer == "win":
            self.root.wins[self.blockNumber] += 1
        self.responses.append([self.blockNumber, self.currentTrial, self.condition,
                               self.root.status["condition"], self.currentRoll, self.response, answer, 
                               sum(self.rewards[:self.root.wins[self.blockNumber]]), t - self.time, self.firstResponse - self.time,
                               t - self.beforeSecondResponse])
        self.bottomText["state"] = "normal"
        self.upperText["state"] = "normal"
        self.die.delete("die")
        self.die.delete("dots")
        self.upperText.delete("1.0", "end")
        self.bottomText.delete("1.0", "end")
        for child in self.upperButtonFrame.winfo_children():
            child.grid_remove()
        for child in self.bottomButtonFrame.winfo_children():
            child.grid_remove()
        self._createFiller()
        self.showWinnings()
        self.update()
        sleep(self.pause_before_trial)
        self.run()
        
                   
    def write(self):
        if self.root.status["block"] == int(self.root.status["winning_block"]):
            self.root.texts["dice"] = sum(self.rewards[:self.root.wins[self.blockNumber]])
        self.root.status["block"] += 1
        for response in self.responses:
            begin = [self.id]
            self.file.write("\t".join(map(str, begin + response)) + "\n")

    
    def nextFun(self):
        if self.blockNumber >= 3: # send the results in the third to sixth round           
            wins = self.root.wins[self.blockNumber]
            reward = sum(self.rewards[:self.root.wins[self.blockNumber]])
            outcome = "|".join(["outcome", str(wins), str(reward), self.condition])
            while True:
                data = urllib.parse.urlencode({'id': self.id, 'round': self.blockNumber, 'offer': outcome})
                data = data.encode('ascii')
                if URL == "TEST":
                    response = "ok"
                else:
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8")       
                    except Exception:
                        continue
                if response == "ok":                    
                    super().nextFun()  
                    return            
                sleep(0.1)
        else:
            super().nextFun()  


    def gothrough(self):
        # nefunguje :(
        self.run()
       
        if "treatment" in self.condition:
            self.predictedCB.invoke()
            self.after(200, self.rollButton.invoke)
            self.after(200, self.winButton.invoke)
            #self.root.update()
            #self.after(500, self.update)
            #answer = random.choice([self.winButton, self.lossButton])
            #self.after(700, answer.invoke)
        elif "control" in self.condition:
            answer = random.choice([self.evenButton, self.oddButton])
            answer.invoke()            
            self.after(200, self.rollButton.invoke)
            self.update()
            self.after(200, self.continueButton.invoke)
            #self.root.update()
            #self.after(700, self.continueButton.invoke)



class Selection(InstructionsFrame):
    def __init__(self, root, text, update = [], height = 24):
        super().__init__(root, text = text, proceed = False, update = update, height = height)

        ttk.Style().configure("TButton", font = "helvetica 15", width = 16)

        self.control = ttk.Button(self, text = controlchoicetext,
                                  command = lambda: self.response("control"))
        self.treatment = ttk.Button(self, text = treatmentchoicetext,
                                    command = lambda: self.response("treatment"))

        self.control.grid(row = 2, column = 0)
        self.treatment.grid(row = 2, column = 2)        

        if self.root.status["block"] == 6 and self.root.status["tokenCondition"]:
            self.control.grid_forget()
            self.treatment.grid_forget()
            
            self.question = ttk.Label(self, text = tokenContribution, font = "helvetica 15", background = "white")
            self.question.grid(row = 2, column = 0, columnspan = 3)
            
            self.question2 = ttk.Label(self, text = version_choice, font = "helvetica 15", background = "white", foreground = "white")   
            self.question2.grid(row = 4, column = 0, columnspan = 3)    
            
            self.yes = ttk.Button(self, text = "Ano", command = lambda: self.token(True))
            self.no = ttk.Button(self, text = "Ne", command = lambda: self.token(False))
            self.yes.grid(row = 3, column = 0)
            self.no.grid(row = 3, column = 2)  
                    
            self.filler = Canvas(self, background = "white", width = 1, height = 40,
                                 highlightbackground = "white", highlightcolor = "white")
            self.filler.grid(column = 0, row = 5, sticky = W)

            self.rowconfigure(2, weight = 1)
            self.rowconfigure(3, weight = 1)
            self.rowconfigure(4, weight = 1)
            self.rowconfigure(5, weight = 1)
            self.rowconfigure(6, weight = 3)


    def token(self, response):
        self.root.status["tokenContributed"] = response
        self.sendData({'id': self.id, 'round': "paidtoken", 'offer': str(response)})        
        self.yes["state"] = "disabled"
        self.no["state"] = "disabled"
        self.question2["foreground"] = "black"
        self.control.grid(row = 5, column = 0)
        self.treatment.grid(row = 5, column = 2)   


    def response(self, choice):
        self.choice = choice
        self.root.status["conditions"].append(choice)
        self.nextFun()

    def write(self):        
        self.file.write("Selection\n" + "\t".join([self.id, str(self.root.status["block"]), self.choice]))

    
    


# class Debrief(InstructionsFrame):
#     def __init__(self, root):
#         super().__init__(root, text = perception_intro, height = 2, font = 15)

#         self.Q1 = TextArea(self, d1, alines = 5, qlines = 2, width = 60)
#         self.Q2 = Measure(self, d2, values = scale, questionPosition = "above", left = "", right = "", labelPosition = "next", filler = 700)  
#         self.Q3 = Measure(self, d3, values = scale, questionPosition = "above", left = "", right = "", labelPosition = "next", filler = 700)
#         self.Q4 = Measure(self, d4, values = scale, questionPosition = "above", left = "", right = "", labelPosition = "next", filler = 700)
#         self.Q5 = TextArea(self, d5, alines = 5, width = 60)

#         self.Q1.grid(row = 2, column = 1)
#         self.Q2.grid(row = 3, column = 1)
#         self.Q3.grid(row = 4, column = 1)
#         self.Q4.grid(row = 5, column = 1)
#         self.Q5.grid(row = 6, column = 1)

#         self.warning = ttk.Label(self, text = "Odpovězte prosím na všechny otázky.",
#                                  background = "white", font = "helvetica 15", foreground = "white")
#         self.warning.grid(row = 7, column = 1)

#         self.next.grid(row = 8, column = 1)

#         self.rowconfigure(0, weight = 2)
#         self.rowconfigure(1, weight = 1)
#         self.rowconfigure(2, weight = 1)
#         self.rowconfigure(3, weight = 1)
#         self.rowconfigure(4, weight = 1)
#         self.rowconfigure(5, weight = 1)
#         self.rowconfigure(6, weight = 1)
#         self.rowconfigure(7, weight = 1)
#         self.rowconfigure(8, weight = 1)
#         self.rowconfigure(9, weight = 2)

#     def check(self):
#         ok = all([self.Q1.check(), self.Q2.check(), self.Q3.check(), self.Q4.check(), self.Q5.check()])
#         if ok:
#             self.write()
#         return ok

#     def back(self):
#         self.warning.config(foreground = "red")

#     def write(self):
#         self.file.write("Debrief\n" + "\t".join([self.id, self.Q2.answer.get(), self.Q3.answer.get(), self.Q4.answer.get()]))
#         self.file.write("\t")
#         self.Q1.write(False)        
#         self.file.write("\t")
#         self.Q5.write() 
#         self.file.write("\n") 



class OutcomeWait(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = wait_text, height = 3, font = 15, proceed = False, width = 45)
        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def checkOffers(self):
        t0 = perf_counter() - 4
        #count = 0
        while True:
            self.update()
            if perf_counter() - t0 > 5:
                t0 = perf_counter()
            #if count % 50 == 0:
                data = urllib.parse.urlencode({'id': self.id, 'round': self.root.status["block"] - 1, 'offer': "outcome"})                
                data = data.encode('ascii')
                if URL == "TEST":            
                    otherversion = random.choice(["treatment", "control"])
                    if otherversion == "control":
                        chance = 0.5
                    else:
                        chance = random.random() / 2
                    otherwins = sum([1 if random.random() > chance else 0 for i in range(12)])
                    otherreward = sum([i*3 + 3 for i in range(12)][:otherwins])        
                    if self.root.status["block"] == 7:
                        if self.root.status["tokenCondition"]:
                            contributed = random.choice(["contributed", "notContributed"])
                        else:
                            contributed = "control"
                        otherversion += "_" + contributed
                    response = "|".join(["outcome", str(otherwins), str(otherreward), otherversion]) + "_True"
                else:
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8")       
                    except Exception as e:
                        continue
                if response:              
                    if not response.endswith("True"):
                        continue
                    else:                                                
                        if URL == "TEST":
                            if "trustblock" in self.root.status:
                                self.root.status["outcome" + str(self.root.status["trustblock"] + 3)] = response
                        else:
                            self.root.status["outcome" + str(self.root.status["block"] - 1)] = response                         
                    self.progressBar.stop()
                    self.nextFun()  
                    return
            #count += 1
            #sleep(0.1)

    def run(self):
        self.progressBar.start()
        self.checkOffers()

    def write(self, response):
        pass



class Login(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = "Počkejte na spuštění experimentu", height = 3, font = 15, width = 45, proceed = False)

        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def login(self):       
        count = 0
        while True:
            self.update()
            if count % 50 == 0:            
                data = urllib.parse.urlencode({'id': self.root.id, 'round': 0, 'offer': "login"})
                data = data.encode('ascii')
                if URL == "TEST":
                    condition = random.choice(["control", "version", "reward", "version_reward"])
                    incentive_order = random.choice(["high-low", "low-high"])
                    tokenCondition = random.choice([True, False])                    
                    winning_block = str(random.randint(1,6))
                    winning_trust = str(random.randint(3,6))
                    trustRoles = "".join([random.choice(["A", "B"]) for i in range(4)])
                    trustPairs = "_".join([str(random.randint(1, 10)) for i in range(4)])                    
                    response = "|".join(["start", condition, incentive_order, str(tokenCondition), winning_block, winning_trust, trustRoles, trustPairs])
                else:
                    response = ""
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8") 
                    except Exception:
                        self.changeText("Server nedostupný")
                if "start" in response:
                    info, condition, incentive_order, tokenCondition, winning_block, winning_trust, trustRoles, trustPairs = response.split("|")              
                    self.root.status["condition"] = condition   
                    self.create_control_question(condition)
                    self.root.status["incentive_order"] = incentive_order                    
                    self.root.status["tokenCondition"] = eval(tokenCondition)
                    self.root.texts["block"] = self.root.status["winning_block"] = winning_block
                    self.root.texts["trustblock"] = self.root.status["winning_trust"] = winning_trust
                    self.root.status["trust_roles"] = list(trustRoles)
                    self.root.status["trust_pairs"] = trustPairs.split("_")                 
                    self.update_intros(condition, incentive_order)
                    self.progressBar.stop()
                    self.write(response)
                    self.nextFun()                      
                    break
                elif response == "login_successful" or response == "already_logged":
                    self.changeText("Přihlášen")
                    self.root.status["logged"] = True
                elif response == "ongoing":
                    self.changeText("Do studie se již nelze připojit")
                elif response == "no_open":
                    self.changeText("Studie není otevřena")
                elif response == "closed":
                    self.changeText("Studie je uzavřena pro přihlašování")
                elif response == "not_grouped":
                    self.changeText("V experimentu nezbylo místo. Zavolejte prosím experimentátora zvednutím ruky.")
            count += 1                  
            sleep(0.1)        

    def run(self):
        self.progressBar.start()
        self.login()

    def update_intros(self, condition, incentive_order):
        self.root.texts["incentive_4"] = 50 if incentive_order == "low-high" else 200
        self.root.texts["incentive_5"] = 200 if incentive_order == "low-high" else 50
        self.root.texts["add_block_4"] = eval(condition + "Text")
        self.root.texts["add_block_5"] = eval(condition + "Text")
        self.root.texts["add_block_6"] = eval(condition + "Text")
        self.root.texts["add_block_6"] += tokenConditionText if self.root.status["tokenCondition"] else "\n\n" + version_choice

    def create_control_question(self, condition):        
        feedbackManipulation = []
        conditions = ["version_reward", "version", "reward", "control"]
        cf = correctFeedback if condition != "control" else correctFeedbackControl
        inf = incorrectFeedback if condition != "control" else incorrectFeedbackControl
        for i, cond in enumerate(conditions):
            f = cf if condition == cond else inf
            feedbackManipulation.append(f + answersManipulation[conditions.index(condition)].lower())
        self.root.texts["controlTexts2"] = [[controlManipulation, answersManipulation, feedbackManipulation]]        

    def write(self, response):
        self.file.write("Login" + "\n")
        self.file.write(self.id + response.replace("|", "\t").lstrip("start") + "\n\n")        

    def gothrough(self):
        self.run()



class Instructions4Check(InstructionsAndUnderstanding):
    def __init__(self, root):
        text = intro_block_4.replace("Chcete hrát verzi “PŘED” nebo “PO”?", "")        
        super().__init__(root, text = text, height = 20, update = ["incentive_4", "add_block_4"], name = "Cheating 4 Control Question", randomize = False, controlTexts = "controlTexts2", fillerheight = 300, finalButton = "Pokračovat k volbě")
        self.next.grid_forget()
        self.next = ttk.Button(self.controlFrame, text = "Pokračovat", command = self.nextFun)
        self.next.grid(row = 4, column = 0)

    def nextFun(self):
        if self.controlstate == "feedback":
            self.file.write(self.id + "\t" + str(self.controlNum) + "\t" + self.controlQuestion.getAnswer() + "\n\n")
            self.controlQuestion.grid_forget()
            self.control = ttk.Button(self, text = controlchoicetext,
                                    command = lambda: self.response("control"))
            self.treatment = ttk.Button(self, text = treatmentchoicetext,
                                        command = lambda: self.response("treatment"))
            self.control.grid(row = 2, column = 0)
            self.treatment.grid(row = 2, column = 2)        
            self.next.grid_forget()
            self.text["state"] = "normal"
            self.text.insert("end", "Chcete hrát verzi “PŘED” nebo “PO”?")
            self.text["state"] = "disabled"    
        else:
            super().nextFun()
    
    def response(self, choice):
        self.root.status["conditions"].append(choice)
        self.file.write("Selection\n" + "\t".join([self.id, str(self.root.status["block"]), choice]))
        InstructionsFrame.nextFun(self)    
    
        



controlTexts1 = [[intro_control1, intro_answers1, intro_feedback1], [intro_control2, intro_answers2, intro_feedback2]]


CheatingInstructions = (InstructionsAndUnderstanding, {"text": intro_block_1, "height": 24, "width": 105, "name": "Cheating Instructions Control Questions", "randomize": False, "controlTexts": controlTexts1})
Instructions2 = (InstructionsFrame, {"text": intro_block_2, "height": 5, "update": ["win1"]})
Instructions3 = (Selection, {"text": intro_block_3, "update": ["win2"]})
Info3 = (InstructionsFrame, {"text": info_block_3, "height": 7, "update": ["win3"]})
#Instructions4 = (Selection, {"text": intro_block_4, "update": ["incentive_4", "add_block_4"]})
Instructions5 = (Selection, {"text": intro_block_5, "update": ["incentive_5", "add_block_5"]})
Instructions6 = (Selection, {"text": intro_block_6, "height": 19, "update": ["add_block_6"]})

EndCheating = (InstructionsFrame, {"text": endtext, "height": 10, "update": ["trust6"]}) # to do update




if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,
          CheatingInstructions,
          Cheating,
          Instructions2,
          Cheating,
          Instructions3, # selection
          Cheating,
          Info3,
          #OutcomeWait,
          Instructions4Check, # selection + info about trust
          #Instructions4,
          Cheating,
          OutcomeWait,
          Instructions5, # selection + info about trust
          Cheating,
          OutcomeWait,
          Instructions6, # selection + info about trust and payment for info
          Cheating,
          OutcomeWait,
          #Debrief,    
          EndCheating
         ])
