#! python3
from tkinter import *
from tkinter import ttk
from collections import deque
from time import perf_counter, sleep

import random
import os

from common import ExperimentFrame, InstructionsFrame
from gui import GUI
from constants import TESTING

NUMTRIALS = 6


items = [["subway", "vzdálenost tratě metra mezi stanicemi metra Muzeum a Hlavní nádraží"],
         ["soccer", "délka typického fotbalového hřiště"],
         ["tree", "výška nejvyššího stromu světa"],
         ["eiffel", "výška Eiffelovy věže"],
         ["vaclav", "délka Václavského náměstí"],
         ["ship", "délka nejdelší lodě"],
         ["skyscraper", "výška nejvyššího mrakodrapu Burj Khalifa"],
         ["waterfall", "výška nejvyššího vodopádu Salto Angel"],
         ["viaduct", "výška nejvyššího mostu, viaduktu Millau,"],
         ["bridge", "délka Nuselského mostu"],
         ["pyramid", "výška nejvyšší (Chufuovy) pyramidy v Gíze"],
         ["petrin", "délka lanové dráhy na Petřín"],
         ["strahov", "délka Velkého strahovského stadionu"],
         ["orlik", "délka betonové hráze vodní nádrže Orlík"],
         ["strelecky", "délka Střeleckého ostrova v Praze"],
         ["baikal", "průměrná hloubka jezera Bajkal"],
         ["skybridge", "délka nejdelšího pěšího visutého mostu v ČR Sky Bridge u obce Dolní Morava"],
         ["tocna", "délka vzletové a přistávací dráhy na letišti Točná"]
         ]


intro1 = """V následující úloze budete srovnávat vlastnosti {} různých objektů s náhodnými hodnotami a činit odhady týkajících se těchto vlastností.

Náhodné hodnoty jsou generovány po zmáčknutí tlačítka 'Znáhodnit' a jsou určeny hodnotami zobrazených na třech "kotoučích" s číslicemi (obrázek kotoučů lze vidět níže). Tyto hodnoty budou v rozsahu od 1 do 1000. S hodnotou 1000 budete srovnávat objekt, pokud bude na všech kotoučích zobrazeno '0'.
"""


againText = "Představte si, že Váš první odhad je špatný. Myslíte si, že v tom případě je {} menší nebo větší než Váš původní odhad {} m?"
bootstrappingText = "Nejprve předpokládejte, že je Váš první odhad zcela špatný. Za druhé přemýšlejte o několika důvodech, proč by to tak mohlo být. Které předpoklady a úvahy mohly být špatné? Za třetí co tyto nové úvahy naznačují? Na základě této nové perspektivy utvořte odlišnou odpověď."
absoluteQuestion2 = "Nyní bychom Vás rádi požádali, abyste uvedl(a) novou, odlišnou odpověď.\nPokud byste měl(a) uvést jiný odhad, jaká je podle Vás {} v metrech?"
warningText = "Odpověď musí být kladné číslo!"


class Anchoring(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        self.file.write("Anchoring\n")

        self.items = items
        random.shuffle(self.items)

        self.number = 0
        self.numTrials = NUMTRIALS

        self.conditions = ["control", "bootstrapping", "comparison"]*(self.numTrials//3)
        random.shuffle(self.conditions)

        self.firstAnswerVar = StringVar()
        self.secondAnswerVar = StringVar()

        ttk.Style().configure("Selected.TButton", font = "helvetica 15 underline")

        self.trialIndicator = ttk.Label(self, text = "", font = "helvetica 15", background = "white")
        self.indicateTrial()
        self.trialIndicator.grid(row = 1, column = 2, sticky = NW)

        # comparison question
        self.comparisonFrame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.comparisonFrame.grid(row = 1, column = 1)
        self.comparisonFrame.rowconfigure(5, weight = 1)

        self.random = ttk.Button(self.comparisonFrame, text = "Znáhodnit", command = self.randomize)
        self.random.grid(row = 1, column = 1, columnspan = 2, pady = 10)

        self.slotwidth = 300
        self.slotheight = 150
        self.slot = Canvas(self.comparisonFrame, width = self.slotwidth+2, height = self.slotheight, background = "white",
                           highlightbackground = "black")
        self.slot.grid(row = 2, column = 1, columnspan = 2)

        self.instruction = 'Zmáčkněte tlačítko "Znáhodnit" pro výběr náhodného čísla'
        self.upper = Text(self.comparisonFrame, font = "helvetica 15", relief = "flat", background = "white",
                          width = 80, height = 1, pady = 7, wrap = "word")
        self.upper.grid(row = 0, column = 1, columnspan = 2, sticky = S)
        self.upper.tag_configure("center", justify = "center")
        self.upper.insert("1.0", self.instruction, "center")
        self.upper["state"] = "disabled"

        self.comparisonQuestion = "Je {} menší nebo větší než {} m?"
        self.comparisonText = Text(self.comparisonFrame, font = "helvetica 15", relief = "flat", background = "white",
                         width = 95, height = 1, pady = 7, wrap = "word")
        self.comparisonText.grid(row = 3, column = 1, columnspan = 2, sticky = S, pady = 10)
        self.comparisonText.tag_configure("center", justify = "center")

        ttk.Style().configure("TButton", font = "helvetica 15")
        
        self.lower = ttk.Button(self.comparisonFrame, text = "Menší", command = self.lowerResponse)
        self.higher = ttk.Button(self.comparisonFrame, text = "Větší", command = self.higherResponse)

        self.blank = Canvas(self.comparisonFrame, height = 340, width = 1, background = "white",
                           highlightbackground = "white")
        self.blank.grid(row = 0, column = 0, rowspan = 6)

        # first absolute question
        self.absoluteFrame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.absoluteFrame.grid(row = 2, column = 1)

        self.absoluteQuestion = "Jaká je {} v metrech?"
        self.absoluteText = Text(self.absoluteFrame, font = "helvetica 15", relief = "flat", background = "white", foreground = "white",
                         width = 80, height = 1, pady = 7, wrap = "word")
        self.absoluteText.grid(row = 1, column = 1, columnspan = 2, sticky = S)
        self.absoluteText.tag_configure("center", justify = "center")

        self.absoluteEntry1 = ttk.Entry(self.absoluteFrame, textvariable = self.firstAnswerVar, font = "helvetica 15", width = 8)

        self.meters = ttk.Label(self.absoluteFrame, text = "m", font = "helvetica 15", background = "white", foreground = "white")
        self.meters.grid(row = 2, column = 2, sticky = W, pady = 10, padx = 5)

        self.warning = ttk.Label(self.absoluteFrame, text = warningText, font = "helvetica 15",
                                 background = "white", foreground = "white", justify = "center", state = "disabled")
        self.warning.grid(row = 4, column = 1, columnspan = 2, padx = 5)
  
        self.next = ttk.Button(self.absoluteFrame, text = "Pokračovat", command = self.absoluteAnswered)

        self.blank2 = Canvas(self.absoluteFrame, height = 220, width = 1, background = "white",
                           highlightbackground = "white")
        self.blank2.grid(row = 0, column = 0, rowspan = 5)   

        # intervention
        self.interventionFrame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.interventionFrame.grid(row = 3, column = 1)

        self.interventionText = Text(self.interventionFrame, font = "helvetica 15", relief = "flat", background = "white",
                          width = 95, height = 3, wrap = "word", pady = 7)
        self.interventionText.grid(row = 0, column = 1, columnspan = 2, sticky = S)
        self.interventionText.tag_configure("center", justify = "center")
        self.interventionText["state"] = "disabled"

        self.lower2 = ttk.Button(self.interventionFrame, text = "Menší", command = self.lowerResponse2)
        self.higher2 = ttk.Button(self.interventionFrame, text = "Větší", command = self.higherResponse2)
        self.interventionNext = ttk.Button(self.interventionFrame, text = "Pokračovat", command = self.bootstrappingResponse)

        self.blank3 = Canvas(self.interventionFrame, height = 150, width = 1, background = "white",
                           highlightbackground = "white")
        self.blank3.grid(row = 0, column = 0, rowspan = 6)        

        # second absolute question
        self.absoluteFrame2 = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.absoluteFrame2.grid(row = 4, column = 1)
      
        self.absoluteText2 = Text(self.absoluteFrame2, font = "helvetica 15", relief = "flat", background = "white", foreground = "white",
                         width = 80, height = 3, pady = 7, wrap = "word")
        self.absoluteText2.grid(row = 1, column = 1, columnspan = 2, sticky = S)
        self.absoluteText2.tag_configure("center", justify = "center")

        self.absoluteEntry2 = ttk.Entry(self.absoluteFrame2, textvariable = self.secondAnswerVar, font = "helvetica 15", width = 8)

        self.meters2 = ttk.Label(self.absoluteFrame2, text = "m", font = "helvetica 15", background = "white", foreground = "white")
        self.meters2.grid(row = 2, column = 2, sticky = W, pady = 10, padx = 5)

        self.warning2 = ttk.Label(self.absoluteFrame2, text = warningText, font = "helvetica 15",
                                 background = "white", foreground = "white", justify = "center", state = "disabled")
        self.warning2.grid(row = 3, column = 1, columnspan = 2, pady = 5)
  
        self.next2 = ttk.Button(self.absoluteFrame2, text = "Pokračovat", command = self.absoluteAnswered2)

        self.blank4 = Canvas(self.absoluteFrame2, height = 250, width = 1, background = "white",
                           highlightbackground = "white")
        self.blank4.grid(row = 0, column = 0, rowspan = 5)   


        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        
        self.rowconfigure(0, weight = 5)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 1)
        self.rowconfigure(4, weight = 1)        
        self.rowconfigure(5, weight = 5)
      
        self.createSlots()


    def indicateTrial(self):
        self.trialIndicator["text"] = "{}/{}".format(self.number + 1, self.numTrials)


    def createSlots(self):          
        self.slot.create_rectangle((3, 3, self.slotwidth/3 + 3, self.slotheight), width = 3)
        self.slot.create_rectangle((self.slotwidth/3 + 3, 3, 2*self.slotwidth/3 + 3, self.slotheight), width = 3)
        self.slot.create_rectangle((2*self.slotwidth/3 + 3, 3, self.slotwidth + 3, self.slotheight), width = 3)

        self.slot.create_polygon((0, self.slotheight/2 + 10,
                                  0, self.slotheight/2 - 10,
                                  15, self.slotheight/2), fill = "black")
        self.slot.create_polygon((self.slotwidth + 5, self.slotheight/2 + 10,
                                  self.slotwidth + 5, self.slotheight/2 - 10,
                                  self.slotwidth - 10, self.slotheight/2), fill = "black")

        self.numbers = []
        
        self.one = random.randint(0, 9)
        self.two = random.randint(0, 9)
        self.three = random.randint(0, 9)

        for i in range(-4, 6):
            self.numbers.append((self.slot.create_text((self.slotwidth/6 + 5, 13*i*self.slotheight/30 + self.slotheight/2),
                                                       text = (self.one+i) % 10, font = "helvetica 45"), 1, (self.one+i) % 10))
            self.numbers.append((self.slot.create_text((3*self.slotwidth/6 + 5, 13*i*self.slotheight/30 + self.slotheight/2),
                                                       text = (self.two+i) % 10, font = "helvetica 45"), 2, (self.two+i) % 10))
            self.numbers.append((self.slot.create_text((5*self.slotwidth/6 + 5, 13*i*self.slotheight/30 + self.slotheight/2),
                                                       text = (self.three+i) % 10, font = "helvetica 45"), 3, (self.three+i) % 10))

    def randomize(self):
        self.random["state"] = "disabled"
        self.upper["state"] = "normal"
        self.upper.delete("1.0", "end")
        self.upper["state"] = "disabled"
        
        self.starttime = perf_counter()
        self.time0 = self.starttime
        self.time = self.time0
        duration = random.randint(5, 6) if not TESTING else 0.2
        self.endtime = self.time + duration

        ends = [1,2,3]
        random.shuffle(ends)
        self.anchor = random.randint(1, 1000)
        stranchor = "{:03d}".format(self.anchor)
        ends[0] += (int(stranchor[-3]) - self.one)/20
        ends[1] += (int(stranchor[-2]) - self.two)/20
        ends[2] += (int(stranchor[-1]) - self.three)/20

        distances = [(duration - ends[i])*1300 for i in range(3)]
        endPositions = {}
        endPositions[1] = [((i - int(stranchor[-3]) + 9)%10 - 8)*self.slotheight*13/30 + self.slotheight/2 for i in range(10)]
        endPositions[2] = [((i - int(stranchor[-2]) + 9)%10 - 8)*self.slotheight*13/30 + self.slotheight/2 for i in range(10)]
        endPositions[3] = [((i - int(stranchor[-1]) + 9)%10 - 8)*self.slotheight*13/30 + self.slotheight/2 for i in range(10)]
        
        while self.time < self.endtime:
            self.time = perf_counter()
            for obj in self.numbers:
                x, y = self.slot.coords(obj[0])
                if distances[obj[1]-1] < 0:
                    y = endPositions[obj[1]][obj[2]-1]
                else:
                    y += (self.time - self.time0) * 1300
                    if y > 1.2*self.slotheight:
                        y -= self.slotheight*13*10/30
                self.slot.coords(obj[0], x, y)
            distances = [i - (self.time - self.time0) * 1300 for i in distances]
            self.time0 = self.time
            self.update()
        
        self.one = int(stranchor[-3])
        self.two = int(stranchor[-2])
        self.three = int(stranchor[-1])
            
        self.displayComparisonQuestion()
        

    def displayComparisonQuestion(self):        
        self.comparisonText["state"] = "normal"
        self.comparisonText.insert("end", self.comparisonQuestion.format(self.items[self.number][1], self.anchor), "center")
        self.comparisonText["state"] = "disabled"

        self.lower.grid(row = 5, column = 1, sticky = E, padx = 20)
        self.higher.grid(row = 5, column = 2, sticky = W, padx = 20)
        self.lower["state"] = "!disabled"
        self.higher["state"] = "!disabled"
        self.t0 = perf_counter()


    def lowerResponse(self):
        self.lower["state"] = "disabled"
        self.higher["state"] = "disabled"
        self.lower["style"] = "Selected.TButton"
        self.response("lower")

    def higherResponse(self):
        self.lower["state"] = "disabled"
        self.higher["state"] = "disabled"
        self.higher["style"] = "Selected.TButton"
        self.response("higher")

    def response(self, answer):
        self.t1 = perf_counter()
        self.comparisonJudgment = answer
        self.next["state"] = "!disabled"

        self.absoluteEntry1.grid(row = 2, column = 1, sticky = E, pady = 10)
        self.next.grid(row = 3, column = 1, columnspan = 2)
        self.absoluteText["foreground"] = "black"
        self.meters["foreground"] = "black"

        self.absoluteText["state"] = "normal"
        self.absoluteText.insert("1.0", self.absoluteQuestion.format(self.items[self.number][1]), "center")
        self.absoluteText["state"] = "disabled"


    def absoluteAnswered(self):
        try:
            answer = float(self.firstAnswerVar.get().replace(",", "."))
            if answer <= 0:
                self.warning["foreground"] = "red"
                return
        except:
            self.warning["foreground"] = "red"     
            return
        else:
            self.warning["foreground"] = "white"     

        self.t2 = perf_counter()
        self.next["state"] = "disabled"

        if self.conditions[self.number] == "control":
            self.interventionResponse()
        elif self.conditions[self.number] == "bootstrapping":
            self.interventionText["state"] = "normal"
            self.interventionText.insert("1.0", bootstrappingText, "center")
            self.interventionText["state"] = "disabled"
            self.interventionNext.grid(row = 5, column = 1, columnspan = 2, sticky = N)
            self.interventionNext["state"] = "disabled"
            if TESTING:
                self.enableInterventionNext()
            else:
                self.root.after(8000, self.enableInterventionNext)
        elif self.conditions[self.number] == "comparison":            
            self.interventionText["state"] = "normal"
            self.interventionText.insert("1.0", againText.format(self.items[self.number][1], self.firstAnswerVar.get()), "center")
            self.interventionText["state"] = "disabled"
            self.lower2.grid(row = 5, column = 1, sticky = E, padx = 20)
            self.higher2.grid(row = 5, column = 2, sticky = W, padx = 20)
            self.lower2["state"] = "!disabled"
            self.higher2["state"] = "!disabled"

    def enableInterventionNext(self):
        self.interventionNext["state"] = "!disabled"

    def lowerResponse2(self):
        self.lower2["state"] = "disabled"
        self.higher2["state"] = "disabled"
        self.lower2["style"] = "Selected.TButton"
        self.interventionResponse("lower")

    def higherResponse2(self):
        self.lower2["state"] = "disabled"
        self.higher2["state"] = "disabled"
        self.higher2["style"] = "Selected.TButton"
        self.interventionResponse("higher")

    def bootstrappingResponse(self):
        self.interventionNext["state"] = "disabled"                
        self.interventionResponse()       

    def interventionResponse(self, answer = "NA"):
        self.interventionAnswer = answer
        self.t3 = perf_counter()
        self.absoluteEntry2.grid(row = 2, column = 1, sticky = E, pady = 10)
        self.next2.grid(row = 4, column = 1, columnspan = 2, pady = 10, sticky = N)
        self.absoluteText2["foreground"] = "black"
        self.meters2["foreground"] = "black"
        self.absoluteText2["state"] = "normal"
        self.absoluteText2.insert("1.0", absoluteQuestion2.format(self.items[self.number][1]), "center")
        self.absoluteText2["state"] = "disabled"


    def absoluteAnswered2(self):
        try:
            answer = float(self.secondAnswerVar.get().replace(",", "."))
            if answer <= 0:
                self.warning2["text"] = warningText
                self.warning2["foreground"] = "red"
                return
            elif abs(answer - float(self.firstAnswerVar.get().replace(",", "."))) < 0.1:
                self.warning2["text"] = "Váš druhý odhad musí být odlišný od prvního."
                self.warning2["foreground"] = "red"
                return
        except:
            self.warning2["text"] = warningText
            self.warning2["foreground"] = "red"
            return
        else:
            self.warning2["foreground"] = "white"  

        self.t4 = perf_counter()

        self.file.write("\t".join([self.id, str(self.number + 1), self.items[self.number][0], str(self.anchor), self.comparisonJudgment, str(self.t1 - self.t0), self.firstAnswerVar.get().replace(",", "."), str(self.t2 - self.t1), self.conditions[self.number], self.interventionAnswer, str(self.t3 - self.t2), self.secondAnswerVar.get().replace(",", "."), str(self.t4 - self.t3)]) + "\n")

        self.number += 1        
        self.proceed()


    def proceed(self):        
        if self.number == self.numTrials:
            self.nextFun()
        else:
            self.indicateTrial()
            self.comparisonText["state"] = "normal"
            self.comparisonText.delete("1.0", "end")
            self.comparisonText["state"] = "disabled"
            self.absoluteText["state"] = "normal"
            self.absoluteText.delete("1.0", "end")
            self.absoluteText["state"] = "disabled"
            self.absoluteText2["state"] = "normal"
            self.absoluteText2.delete("1.0", "end")
            self.absoluteText2["state"] = "disabled"
            self.interventionText["state"] = "normal"
            self.interventionText.delete("1.0", "end")
            self.interventionText["state"] = "disabled"
            self.lower.grid_forget()
            self.higher.grid_forget()
            self.lower2.grid_forget()
            self.higher2.grid_forget()
            self.interventionNext.grid_forget()
            self.lower["state"] = "disabled"
            self.higher["state"] = "disabled"
            self.lower["style"] = "TButton"
            self.higher["style"] = "TButton"
            self.lower2["state"] = "disabled"
            self.higher2["state"] = "disabled"
            self.lower2["style"] = "TButton"
            self.higher2["style"] = "TButton"
            self.random["state"] = "normal"
            self.upper["state"] = "normal"
            self.upper.insert("1.0", self.instruction, "center")
            self.upper["state"] = "disabled"
            self.meters["foreground"] = "white"
            self.meters2["foreground"] = "white"
            self.firstAnswerVar.set("")
            self.secondAnswerVar.set("")
            self.next.grid_forget()
            self.next2.grid_forget()
            self.absoluteEntry1.grid_forget()
            self.absoluteEntry2.grid_forget()
            









class SlotInstructions(InstructionsFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.slotwidth = 300
        self.slotheight = 150
        self.slot = Canvas(self, width = self.slotwidth+2, height = self.slotheight, background = "white",
                           highlightbackground = "black")
        self.slot.grid(row = 2, column = 1)

        self.next.grid(row = 3, column = 1)

        self.createSlots()

        self.rowconfigure(4, weight = 2)


    def createSlots(self):          
        self.slot.create_rectangle((3, 3, self.slotwidth/3 + 3, self.slotheight), width = 3)
        self.slot.create_rectangle((self.slotwidth/3 + 3, 3, 2*self.slotwidth/3 + 3, self.slotheight), width = 3)
        self.slot.create_rectangle((2*self.slotwidth/3 + 3, 3, self.slotwidth + 3, self.slotheight), width = 3)

        self.slot.create_polygon((0, self.slotheight/2 + 10,
                                  0, self.slotheight/2 - 10,
                                  15, self.slotheight/2), fill = "black")
        self.slot.create_polygon((self.slotwidth + 5, self.slotheight/2 + 10,
                                  self.slotwidth + 5, self.slotheight/2 - 10,
                                  self.slotwidth - 10, self.slotheight/2), fill = "black")

        self.numbers = []
        
        self.number = random.randint(1, 999)

        self.text.config(state = "normal")
        self.text.insert("end", "\nKotouče níže například ukazují číslo {}.".format(self.number))
        self.text.config(state = "disabled")

        self.number = "{:03d}".format(self.number)

        for i in range(-4, 6):
            self.numbers.append((self.slot.create_text((self.slotwidth/6 + 5, 13*i*self.slotheight/30 + self.slotheight/2),
                                                       text = (int(str(self.number)[0])+i) % 10, font = "helvetica 45"), 1, (int(str(self.number)[0])+i) % 10))
            self.numbers.append((self.slot.create_text((3*self.slotwidth/6 + 5, 13*i*self.slotheight/30 + self.slotheight/2),
                                                       text = (int(str(self.number)[1])+i) % 10, font = "helvetica 45"), 2, (int(str(self.number)[1])+i) % 10))
            self.numbers.append((self.slot.create_text((5*self.slotwidth/6 + 5, 13*i*self.slotheight/30 + self.slotheight/2),
                                                       text = (int(str(self.number)[2])+i) % 10, font = "helvetica 45"), 3, (int(str(self.number)[2])+i) % 10))



    

AnchoringInstructions = (SlotInstructions, {"text": intro1.format(NUMTRIALS), "height": 10, "font": 16})

      

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([AnchoringInstructions, 
         Anchoring])

