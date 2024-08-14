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
instructions = """Vítejte v druhé části dnešní studie. Pozorně si přečtěte pokyny, abyste porozuměli studii a své roli v ní. Vaše rozhodnutí budou mít finanční důsledky pro Vás a pro dalšího přítomného účastníka.

V této části studie Vám bude náhodně přidělena jedna ze dvou rolí: budete buď hráčem A, nebo hráčem B. Vaše role zůstane stejná po celou dobu úkolu a zároveň budete v obou kolech úkolu ve dvojici se stejným účastníkem. Oba účastníci ve dvojici budou vždy informováni o rozhodnutích toho druhého.

<b>První kolo:</b>
Každý z hráčů A a B obdrží 20 Kč. 
<i>Hráč A:</i> Má možnost vzít si od hráče B od 0 do 10 Kč (v krocích po 2 Kč).
<i>Hráč B:</i> Má k dispozici dvě možné reakce na rozhodnutí hráče A a bude moci vybrat zprávu, kterou pošle hráči A.
Reakce mohou být:{}{}
Hráč B zvolí svoji reakci a zprávu pro všechna možná rozhodnutí hráče A.

Jakmile oba účastníci odešlou své odpovědi, jejich rozhodnutí budou provedena a hráči se dozví, co se rozhodl udělat hráč A, jak na to reagoval hráč B a jakou zprávu hráči A poslal. Hra pak postoupí do druhého kola, které je velmi podobné – liší se pouze částkou, kterou hráč A může vzít hráči B: zatímco v prvním kole mohl vzít polovinu z úvodní částky, ve druhém kole může vzít celou úvodní částku.

<b>Druhé kolo:</b>
Každý z hráčů A a B obdrží 20 Kč.
<i>Hráč A:</i> Má možnost vzít si od hráče B od 0 do 20 Kč (v krocích po 2 Kč).
<i>Hráč B:</i> V druhém kole nedělá žádné rozhodnutí.

Jakmile hráč A odešle svoji odpověď, hráči se dozví o daném rozhodnutí a tato část studie končí.

Níže zodpovězte několik otázek, abyste si ověřili, že studii rozumíte."""

ignoreInfo = "\n<b>Neudělat nic</b>: Pokračovat ve studii bez jakékoli akce."
punishInfo = "\n<b>Potrestat</b>: Může hráče A potrestat od symbolické 0 až po 10 Kč. Za každou 1 Kč, kterou hráč B vynaloží na potrestání, ztratí hráč A také 1 Kč."
forgiveInfo = "\n<b>Odpustit</b>: Může hráči A odpustit a  poslat mu od symbolické 0 až po 10 Kč. Za každou 1 Kč, kterou ze svých peněz hráč B pošle, hráč A dostane 1 Kč." 

DictControl1 = "Jaká je role hráče A a hráče B ve studii?"
DictAnswers1 = ["Hráč A rozhoduje, kolik hráči B vezme peněz. Účastníci studie jsou v obou kolech buď hráčem A, nebo hráčem B (role se nemění).",
"Hráč A rozhoduje, kolik hráči B vezme peněz. Účastníci studie jsou nejprve hráčem A v druhém kole hráčem B (role se vymění).", "Hráč B rozhoduje, kolik hráči A vezme peněz. Účastníci studie jsou v obou kolech buď hráčem A, nebo hráčem B (role se nemění).", "Hráč B rozhoduje, kolik hráči A vezme peněz. Účastníci studie jsou nejprve hráčem A v druhém kole hráčem B (role se vymění)."]
DictFeedback1 = ["Správná odpověď.", "Chybná odpověď. Účastníci studie jsou v obou kolech buď hráčem A, nebo hráčem B (role se nemění).", "Chybná odpověď. Hráč A rozhoduje, kolik hráči B vezme peněz.", "Chybná odpověď. Hráč A rozhoduje, kolik hráči B vezme peněz. Účastníci studie jsou v obou kolech buď hráčem A, nebo hráčem B (role se nemění)."]

DictControl2 = "Jaký je rozdíl mezi prvním a druhým kolem studie?"
DictAnswers2 = ["V druhém kole bude druhým hráčem jiný účastník studie.", "V druhém kole hráč B nemá možnost reakce.", "V druhém kole obdrží oba hráči více peněz na začátku.", "V druhém kole se mění role hráčů."]
DictFeedback2 = ["Chybná odpověď. V obou kolech studie budete ve dvojici se stejným účastníkem.", "Správná odpověď. V druhém kole hráč B pouze vyčkává rozhodnutí hráče A.", "Chybná odpověď. V obou kolech hráči obdrží na začátku 20 Kč.", "Chybná odpověď, v druhém kole zůstává role hráčů stejná."]

DictControl3 = 'Pokud se hráč B rozhodne “potrestat” hráče A v prvním kole částkou 6 Kč, kolik peněz ztratí hráč A?'
DictAnswers3 = ["0 Kč ", "6 Kč", "10 Kč", "12 Kč"]
DictFeedback3 = ["Chybná odpověď. Za každou 1 Kč trestu, ztratí hráč A také 1 Kč.", "Správná odpověď.", "Chybná odpověď. Za každou 1 Kč trestu, ztratí hráč A také 1 Kč.", "Chybná odpověď. Za každou 1 Kč trestu, ztratí hráč A také 1 Kč."]

DictControl4 = 'Pokud hráč B rozhodne "odpustit" a poslat hráči A 2 Kč v prvním kole, kolik peněz ztratí hráč B a kolik získá hráč A?'
DictAnswers4 = ["Hráč B ztratí 2 Kč, hráč A získá 0 Kč.", "Hráč B ztratí 6 Kč, hráč A získá 4 Kč.", "Hráč B ztratí 2 Kč, hráč A získá 2 Kč.", "Hráč B ztratí 0 Kč, hráč A získá 4 Kč."]
DictFeedback4 = ["Chybná odpověď. Hráč B ztratí 2 Kč, hráč A získá 2 Kč.", "Chybná odpověď. Hráč B ztratí 2 Kč, hráč A získá 2 Kč.", "Správná odpověď.", "Chybná odpověď. Hráč B ztratí 2 Kč, hráč A získá 2 Kč."]

DictControl5 = "Pokud se hráč B v prvním kole rozhodne “neudělat nic”, jaké jsou peněžní důsledky pro hráče A?" 
DictAnswers5 = ["Získá navíc 20 Kč a obdrží zprávu od hráče B.", "Žádné. Obdrží jen zprávu od hráče B.", "Získá navíc 1 Kč a obdrží zprávu od hráče B.", "Ztratí 20 Kč a obdrží zprávu od hráče B."]
DictFeedback5 = ["Chybná odpověď. Hráč A v prvním kole žádné další peníze nezíská, ani neztratí.\nObdrží jen zprávu od hráče B.", "Správná odpověď.", "Chybná odpověď. Hráč A v prvním kole žádné další peníze nezíská, ani neztratí.\nObdrží jen zprávu od hráče B.", "Chybná odpověď. Hráč A v prvním kole žádné další peníze nezíská, ani neztratí.\nObdrží jen zprávu od hráče B."]


wait_text = "Prosím počkejte na druhého hráče.  Můžete zatím vyplňovat vytištěný dotazník."



A1text = """Byla Vám náhodně přidělena role: <b>Hráč A</b> 
Vaše role zůstává po celou dobu studie stejná.

Vy i hráč B jste dostali v této části studie 20 Kč.
S hráčem B budete ve dvojici pro obě kola studie. Oba budete informováni o rozhodnutích toho druhého.

Nyní budete mít příležitost se rozhodnout, kolik (0-10 Kč, v krocích po 2 Kč) si od hráče B vezmete.
Hráč B bude na Vaše rozhodnutí reagovat. Bude mít k dispozici dvě možnosti reakce na Vaše rozhodnutí a vybere pro Vás zprávu:
{}

<b>Rozhodněte se, kolik si chcete od hráče B vzít (0-10 Kč)</b>:
"""

ignoreText = "\n<b>Neudělat nic</b>: Pokračovat ve studii bez jakékoli akce."
punishText = "\n<b>Potrestat</b>: Může Vás potrestat od symbolické 0 až po 10 Kč. Za každou 1 Kč, kterou vynaloží na potrestání, ztratíte 1 Kč."
forgiveText = "\n<b>Odpustit</b>: Může Vám odpustit a poslat Vám od symbolické 0 až po 10 Kč. Za každou 1 Kč, kterou Vám ze svých peněz pošle, dostanete 1 Kč." 


B1text = """Byla vám náhodně přidělena role: <b>Hráč B</b> 
Vaše role zůstává po celou dobu studie stejná.
Vy i hráč A jste dostali v této části studie 20 Kč.
S hráčem A budete ve dvojici pro obě kola studie. Oba budete informováni o rozhodnutích toho druhého.

Hráč A Vám může vzít 0 až 10 Kč (v krocích po 2 Kč). Níže uveďte, jak budete reagovat v případě všech možných rozhodnutí hráče A. Máte na výběr z těchto dvou možností:	
{}

<b>Níže uveďte v Kč Vaše reakce na možná rozhodnutí hráče A (posuňte posuvníkem) a rozhodněte, kterou ze dvou textových zpráv chcete hráči A poslat:</b>"""

ignoreResponse = '''<b>- Neudělat nic</b>: Pokračovat ve studii bez jakékoli akce a poslat jednu ze zpráv.'''
punishResponse = '''<b>- Potrestat</b>: Můžete hráče A potrestat od symbolické 0 až po 10 Kč. Za každou 1 Kč, kterou vynaložíte na potrestání, ztratí hráč A 1 Kč. Navíc pošlete jednu ze zpráv.'''
forgiveResponse = '''<b>- Odpustit</b>: Můžete hráči A odpustit a poslat mu od symbolické 0 až po 10 Kč. Za každou 1 Kč, kterou ze svých peněz pošlete, hráč A dostane 1 Kč. Navíc pošlete jednu ze zpráv.'''

ignoreMessage1 = '"V reakci na Vaše rozhodnutí neudělám nic a jen pokračuji ve studii."'
ignoreMessage2 = '"Volím možnost: Neudělat nic."'
punishMessage1 = '"V reakci na Vaše rozhodnutí Vás tímto trestám."'
punishMessage2 = '"Volím možnost: Potrestat."'
forgiveMessage1 = '"Je mi líto, že jste mi vzal/a peníze. Takto by se k sobě lidé chovat neměli. Já Vám ale odpouštím."'
forgiveMessage2 = '"Volím možnost: Odpustit."'


followup = "Jak se cítíte poté, co jste učinil/a Vaši volbu?"
scale = ["Nepatrně\nnebo vůbec", "Velmi mírně", "Mírně", "Docela dost", "Extrémně"]
dimensions = ["Naštvaně", "Rozrušeně", "Provinile", "Nepřátelsky", "Hrdě", "Nadšeně", "Zahanbeně", "Odhodlaně", "Bojácně"]

expectText = "Jaké chování očekáváte od hráče B v reakci na Vaši volbu:"
expectAnswers = {"ignore": "Nebude dělat nic.", "punish": "Potrestá mne (přijdeme oba o 0-10 Kč).", "forgive": "Odpustí mi (pošle mi 0-10 Kč a sám/sama ztratí 0-10 Kč)."}

followupB2 = """Hráč A Vám může vzít 0 až 20 Kč. Vyčkejte na rozhodnutí hráče A.

Jak se cítíte?"""


dictatorResultTextA = """Rozhodl/a jste se Hráči B vzít {} Kč.

Jako reakci Hráč B:
<b>{}
Vy máte tedy po prvním kole {} Kč a Hráč B {} Kč.</b> 
Nyní přistoupíme k druhému kolu.


<b>Druhé kolo</b>
Máte stejnou roli: Hráč A
Vy i Hráč B jste dostali 20 Kč.

Rozhodněte se, kolik (0-20 Kč) si od hráče B vezmete.
Hráč B čeká na Vaše rozhodnutí.

<b>Rozhodněte se nyní, kolik si chcete od hráče B vzít (0-20 Kč):</b>"""

dictatorResultTextB = """Hráč A se rozhodl Vám vzít {} Kč.

Jako reakci jste:
{}
<b>Vy máte tedy po prvním kole {} Kč a Hráč A {} Kč.</b> 
Nyní přistoupíme k druhému kolu.


<b>Druhé kolo</b>
Máte stejnou roli: Hráč B
Vy i Hráč A jste dostali 20 Kč.

Hráč A se rozhodne, kolik (0-20 Kč) si od Vás vezme.
Vy čekáte na rozhodnutí Hráče A."""

ignoreResult = 'Neudělal nic a poslal zprávu "{}"'
punishResult = '{} a poslal zprávu "{}" Oba ztrácíte {} Kč.'
forgiveResult = '{} {} Kč a poslal zprávu "{}"'

punishA = "Vás potrestal/a"
punishB = "Hráče A potrestal/a"
forgiveA = "Vám odpustil/a, daroval/a Vám"
forgiveB = "Hráči A odpustil/a, daroval/a Hráči A"


finalTextA = """Rozhodl/a jste se Hráči B vzít {} Kč.
V tomto kole jste získal/a {} Kč a Hráč B {} Kč.
<b>Z této úlohy si dohromady odnášíte {} Kč a Hráč B {} Kč.</b> 

Tímto tato část studie končí.
Ve studii pokračujte kliknutím na tlačítko "Pokračovat"."""

finalTextB = """Hráč A se rozhodl Vám vzít {} Kč.
V tomto kole jste získal/a {} Kč a Hráč A {} Kč.
<b>Z této úlohy si dohromady odnášíte {} Kč a Hráč A {} Kč.</b> 

Tímto tato část studie končí.
Ve studii pokračujte kliknutím na tlačítko "Pokračovat"."""


################################################################################




class ScaleFrame(Canvas):
    def __init__(self, root, round = 1, font = 15, rounding = 2):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white")

        self.parent = root
        self.root = root.root
        self.rounding = rounding

        self.valueVar = StringVar()
        self.valueVar.set("0")

        ttk.Style().configure("TScale", background = "white")

        self.value = ttk.Scale(self, orient = HORIZONTAL, from_ = 0, to = 10*round, length = 500,
                            variable = self.valueVar, command = self.changedValue)

        self.actionLab = ttk.Label(self, text = "Beru", font = "helvetica {}".format(font), background = "white", anchor = "w")
        self.valueLab = ttk.Label(self, textvariable = self.valueVar, font = "helvetica {}".format(font), background = "white", width = 3, anchor = "e")
        self.currencyLab = ttk.Label(self, text = "Kč", font = "helvetica {}".format(font), background = "white")

        self.value.grid(column = 1, row = 1, padx = 15)
        self.actionLab.grid(column = 2, row = 1)
        self.valueLab.grid(column = 3, row = 1)
        self.currencyLab.grid(column = 4, row = 1)


    def changedValue(self, value):                
        self.valueVar.set(str(int(round(eval(self.valueVar.get())/self.rounding, 0)*self.rounding)))
        if self.root.status["dictatorRole"] == "B":
            self.parent.changedValue()
        else:
            self.parent.checkAnswers()
        

class ResponseFrame(Canvas):
    def __init__(self, root, value):
        super().__init__(root, background = "white", highlightbackground = "white", highlightcolor = "white", width = 1200, height = 300)        
        self.root = root.root
        self.parent = root

        conditions = {"ignore": ["Neudělám nic", ignoreMessage1, ignoreMessage2], 
                      "punish": ["Potrestám", punishMessage1, punishMessage2],
                      "forgive": ["Odpustím", forgiveMessage1, forgiveMessage2]}
        self.conditions = conditions
        self.value = value

        c1, c2 = self.root.status["dictatorCondition"].split("-")

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 14")

        valueText = str(value*2) + "Kč:  " if value < 5 else "10 Kč:  "
        self.valueLab = ttk.Label(self, text = "Hráč A vezme " +  valueText, font = "helvetica 14", background = "white", anchor = "e", width = 18)

        self.responseVar = StringVar()
        self.responseBut1 = ttk.Radiobutton(self, text = conditions[c1][0], value = c1, command = self.response1, variable = self.responseVar)
        self.responseBut2 = ttk.Radiobutton(self, text = conditions[c2][0], value = c2, command = self.response2, variable = self.responseVar)

        self.filler = Canvas(self, background = "white", width = 1250, height = 1,
                                highlightbackground = "white", highlightcolor = "white")
        self.filler.grid(column = 0, row = 0, columnspan = 4, sticky = EW)

        self.filler2 = Canvas(self, background = "white", width = 1, height = 100,
                                highlightbackground = "white", highlightcolor = "white")
        self.filler2.grid(column = 0, row = 0, rowspan = 4, sticky = NS)

        self.valueLab.grid(column = 1, row = 1)
        self.responseBut1.grid(column = 2, row = 1, sticky = W)
        self.responseBut2.grid(column = 2, row = 2, sticky = W)

        self.columnconfigure(3, weight = 2)
        self.rowconfigure(0, weight = 0)
        self.rowconfigure(1, weight = 0)
        self.rowconfigure(2, weight = 0)
        self.rowconfigure(3, weight = 2)

        self.s= ttk.Style()
        self.s.configure('Grey.TRadiobutton', foreground='grey')
        self.s.configure('Black.TRadiobutton', foreground='black')

        self.messageVar = StringVar()        
        self.messageBut1 = ttk.Radiobutton(self, text = " ", value = "1", command = self.message1, variable = self.messageVar)
        self.messageBut2 = ttk.Radiobutton(self, text = " ", value = "2", command = self.message2, variable = self.messageVar)
        self.scale = ScaleFrame(self, font = 14, rounding = 1)

        self.messageBut1.grid(column = 3, row = 1, sticky = W, padx = 10)
        self.messageBut2.grid(column = 3, row = 2, sticky = W, padx = 10)
        self.scale.grid(column = 2, row = 3, columnspan = 2, sticky = W)

        self.messageBut1.grid_remove()
        self.messageBut2.grid_remove()
        self.scale.grid_remove()

        self.scaleResponses = {c1: 0, c2: 0}
        self.messageResponses = {c1: 0, c2: 0}

    def changedValue(self):
        self.scaleResponses[self.responseVar.get()] = self.scale.valueVar.get()

    def response1(self):
        self.responseBut1["style"] = "Black.TRadiobutton"
        self.responseBut2["style"] = "Grey.TRadiobutton"
        self.response()

    def response2(self):
        self.responseBut1["style"] = "Grey.TRadiobutton"
        self.responseBut2["style"] = "Black.TRadiobutton"
        self.response()

    def response(self):
        c1, c2 = self.root.status["dictatorCondition"].split("-")

        if self.responseVar.get() != "ignore":
            self.scale.grid(column = 2, row = 3, columnspan = 2, sticky = W)
            if self.responseVar.get() == "punish":
                self.scale.actionLab["text"] = "Trestám"
            else:
                self.scale.actionLab["text"] = "Dávám"
            self.scale.valueVar.set(self.scaleResponses[self.responseVar.get()])
        else:
            self.scale.grid_remove()

        self.messageBut1["text"] = self.conditions[self.responseVar.get()][1]
        self.messageBut2["text"] = self.conditions[self.responseVar.get()][2]

        if self.messageResponses[self.responseVar.get()]:
            self.messageVar.set(self.messageResponses[self.responseVar.get()])
            if self.messageVar.get() == "1":
                self.message1()
            else:
                self.message2()
        else:
            self.messageVar.set("")
            self.messageBut1["style"] = "Black.TRadiobutton"
            self.messageBut2["style"] = "Black.TRadiobutton"
            self.parent.next["state"] = "disabled"

        self.messageBut1.grid(column = 3, row = 1, sticky = W, padx = 20)
        self.messageBut2.grid(column = 3, row = 2, sticky = W, padx = 20)

    def message1(self):
        self.messageBut1["style"] = "Black.TRadiobutton"
        self.messageBut2["style"] = "Grey.TRadiobutton"
        self.message()

    def message2(self):
        self.messageBut1["style"] = "Grey.TRadiobutton"
        self.messageBut2["style"] = "Black.TRadiobutton"
        self.message()

    def message(self):
        self.messageResponses[self.responseVar.get()] = self.messageVar.get()
        self.parent.checkAnswers()
    
    def getData(self):
        money = "0" if self.responseVar.get() == "ignore" else self.scale.valueVar.get()
        return "|".join([str(self.value * 2), self.responseVar.get(), self.messageVar.get(), money])
        


class DictatorDecision(InstructionsFrame):
    def __init__(self, root):
        if root.status["dictatorRole"] == "A":
            text = A1text
            text = text.format({"forgive-ignore": forgiveText + "\n" + ignoreText, 
                                "ignore-punish": ignoreText + "\n" + punishText, 
                                "forgive-punish": forgiveText + "\n" + punishText}[root.status["dictatorCondition"]])
            height = 20
            width = 80
        else:
            text = B1text
            text = text.format({"forgive-ignore": forgiveResponse + "\n" + ignoreResponse, 
                    "ignore-punish": ignoreResponse + "\n" + punishResponse, 
                    "forgive-punish": forgiveResponse + "\n" + punishResponse}[root.status["dictatorCondition"]])
            height = 15
            width = 100

        super().__init__(root, text = text, height = height, font = 15, width = width)

        if self.root.status["dictatorRole"] == "A":
            self.scaleFrame = ScaleFrame(self)       
            self.scaleFrame.grid(column = 1, row = 3, pady = 10, sticky = NSEW)        
            self.next.grid(column = 1, row = 4)
            self.rowconfigure(4, weight = 1)
        else:
            self.next["state"] = "disabled"
            self.frames = {}
            for i in range(6):
                self.frames[i] = ResponseFrame(self, i)
                self.frames[i].grid(column = 0, row = 3 + i, pady = 1, columnspan = 3)
            self.next.grid(column = 1, row = 15, pady = 5, sticky = N)            
            #self.rowconfigure(15, weight = 1)
      
       
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 0)
        self.rowconfigure(2, weight = 0)
        self.rowconfigure(3, weight = 0)
        self.rowconfigure(16, weight = 2)

    def checkAnswers(self):
        if self.root.status["dictatorRole"] == "B":            
            for frame in self.frames.values():
                if not frame.messageVar.get():
                    break
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


class WaitDictator(InstructionsFrame):
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



class DictatorFeelings(Questionnaire):
    def __init__(self, root, round = 1):

        question = followupB2 if root.status["dictatorRole"] == "B" and round == 2 else followup

        super().__init__(root, words = dimensions, question = question, labels = scale, values = 5, labelwidth = 12, text = False,
                         fontsize = 14, blocksize = len(dimensions), filetext = "Dictator Feelings" + str(round))

        self.round = round

        if self.root.status["dictatorRole"] == "A" and self.round == 1:
            answers = [expectAnswers[condition] for condition in self.root.status["dictatorCondition"].split("-")]
            self.expectation = MultipleChoice(self, text = expectText, answers = answers, feedback = [""]*2, randomize = False, callback = self.clicked)
            self.expectation.grid(row = 2, column = 1)
            self.next.grid(row = 3, column = 1)
        
    def clicked(self):
        super().clicked()     
        if self.root.status["dictatorRole"] == "A" and self.round == 1:            
            if self.expectation.answer.get():
                for word in self.words:
                    if not self.variables[word].get():
                        self.next["state"] = "disabled"
                        break
                else:
                    self.next["state"] = "!disabled"

    def write(self):
        super().write()        
        if self.root.status["dictatorRole"] == "A" and self.round == 1:            
            self.file.write("\nDictator Expectation\n")
            self.file.write(self.id + "\t" + self.expectation.answer.get() + "\n")
        

               

class DictatorResult(InstructionsFrame):
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
            


class InstructionsDictator(InstructionsAndUnderstanding):
    def __init__(self, root):
        out = ["forgive-ignore", "ignore-punish", "forgive-punish"].index(root.status["dictatorCondition"]) + 2
        controlTexts = controlTexts1
        controlTexts.pop(out)
        
        super().__init__(root, text = instructions, height = 31, width = 110, name = "Dictator Control Questions", randomize = False, controlTexts = controlTexts, update = ["firstOption", "secondOption"])    






controlTexts1 = [[DictControl1, DictAnswers1, DictFeedback1], [DictControl2, DictAnswers2, DictFeedback2], [DictControl3, DictAnswers3, DictFeedback3], [DictControl4, DictAnswers4, DictFeedback4], [DictControl5, DictAnswers5, DictFeedback5]]
WaitResult1 = (WaitDictator, {"what": "decision1"})
WaitResult2 = (WaitDictator, {"what": "decision2"})
DictatorEnd = (InstructionsFrame, {"text": "{}", "height": 8, "update": ["dictatorEnd"]})
DictatorFeelings2 = (DictatorFeelings, {"round": 2})



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,         
         WaitDictator,
         InstructionsDictator,
         DictatorDecision,
         DictatorFeelings,
         WaitResult1,
         DictatorResult,
         DictatorFeelings2,
         WaitResult2,
         DictatorEnd
         ])