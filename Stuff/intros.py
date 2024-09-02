#! python3

import os
import urllib.request
import urllib.parse

from math import ceil
from time import sleep

from common import InstructionsFrame
from gui import GUI

from constants import BONUS, PARTICIPATION_FEE, URL
from cheating import Login


################################################################################
# TEXTS
intro = """
Studie se skládá z několika různých úkolů a otázek. Níže je uveden přehled toho, co Vás čeká:
1) Hod kostkou: Vaším úkolem bude uhodnout, zda na kostce padne liché nebo sudé číslo. Budete hádat v šesti blocích, každém po dvanácti kolech. V tomto úkolu můžete vydělat peníze.
2) Dělení peněz: Budete se rozhodovat, jak dělit peníze v páru s jiným účastníkem studie. V tomto úkolu můžete vydělat peníze.
3) Loterie: můžete se rozhodnout zúčastnit se loterie a získat další peníze v závislosti na výsledcích loterie.
4) Dotazníky: budete odpovídat na otázky ohledně Vašich vlastností a postojů. 
5) Konec studie a platba: poté, co skončíte, půjdete do vedlejší místnosti, kde podepíšete pokladní dokument, na základě kterého obdržíte vydělané peníze v hotovosti. <b>Jelikož v dokumentu bude uvedena pouze celková suma, experimentátor, který Vám bude vyplácet odměnu, nebude vědět, kolik jste vydělali v jednotlivých částech studie.</b>

V případě, že máte otázky nebo narazíte na technický problém během úkolů, zvedněte ruku a tiše vyčkejte příchodu výzkumného asistenta.

Všechny informace, které v průběhu studie uvidíte, jsou pravdivé a nebudete za žádných okolností klamáni či jinak podváděni."""


ending = """
V úloze s házením kostek byl náhodně vybrán blok {}. V úkolu s kostkou jste tedy vydělali {} Kč. V úkolu, kde se dělily peníze s dalším účastníkem studie byl náhodně vybrán blok {} a získali jste tedy {} Kč. V loteriích jste vydělali {} Kč. Za účast na studii dostáváte {} Kč. Vaše odměna za tuto studii je tedy dohromady {} Kč, zaokrouhleno na desítky korun nahoru získáváte {} Kč. Napište prosím tuto (zaokrouhlenou) částku do příjmového dokladu na stole před Vámi. 

Výsledky experimentu budou volně dostupné na stránkách Centra laboratorního a experimentálního výzkumu FPH VŠE, krátce po vyhodnocení dat a publikaci výsledků. Žádáme Vás, abyste nesdělovali detaily této studie možným účastníkům, aby jejich volby a odpovědi nebyly ovlivněny a znehodnoceny.
  
Můžete si vzít všechny svoje věci, vyplněný příjmový doklad a záznamový arch, a aniž byste rušili ostatní účastníky, odeberte se do vedlejší místnosti za výzkumným asistentem, od kterého obdržíte svoji odměnu. 

Toto je konec experimentu. Děkujeme za Vaši účast!
 
Centrum laboratorního a experimentálního výzkumu FPH VŠE""" 


login = """
Vítejte na výzkumné studii pořádané Fakultou podnikohospodářskou Vysoké školy ekonomické v Praze! 

Za účast na studii obdržíte {} Kč. Kromě toho můžete vydělat další peníze v průběhu studie. 

Studie bude trvat cca 50-70 minut.

Děkujeme, že jste vypnuli své mobilní telefony, a že nebudete s nikým komunikovat v průběhu studie. Pokud s někým budete komunikovat, nebo pokud budete nějakým jiným způsobem narušovat průběh studie, budete požádáni, abyste opustili laboratoř, bez nároku na vyplacení peněz.

Pokud jste již tak neučinili, přečtěte si informovaný souhlas a pokud s ním budete souhlasit, podepište ho. 

Počkejte na pokyn experimentátora.""".format(PARTICIPATION_FEE)


# hexacointrotext = """
# Před sebou máte na papíře vytištěný dotazník a záznamový arch. Do záznamového archu vyplňte do pole vlevo dole své identifikační číslo <b>{}</b>. Samotný dotazník ještě nevyplňujte.

# Jelikož probíhá v některých částech studie interakce s ostatními účastníky studie, může se stát, že na ně budete muset chvíli čekat. Během případného čekání můžete vyplňovat odpovědi na vytištěný dotazník do přiloženého záznamového archu. Aby nemuseli ostatní účastníci studie čekat na Vás, nevyplňujte dotazník, když je možné pokračovat ve studii na počítači.

# Po vyplnění identifikačního čísla do záznamového archu klikněte na tlačítko Pokračovat."""
################################################################################





class Ending(InstructionsFrame):
    def __init__(self, root):
        dice = int(str(root.texts["dice"]).split(" ")[0])
        root.texts["reward"] = dice + int(root.texts["trust"]) + int(root.texts["lottery_win"]) + PARTICIPATION_FEE
        root.texts["rounded_reward"] = ceil(root.texts["reward"] / 10) * 10
        root.texts["participation_fee"] = str(PARTICIPATION_FEE)
        updates = ["block", "dice", "trustblock", "trust", "lottery_win", "participation_fee", "reward", "rounded_reward"]
        super().__init__(root, text = ending, keys = ["g", "G"], proceed = False, height = 20, update = updates)
        self.file.write("Ending\n")
        self.file.write(self.id + "\t" + "\t".join([str(root.texts["rounded_reward"]), str(root.texts["block"])]) + "\n\n")

    def run(self):
        self.sendInfo()

    def sendInfo(self):
        while True:
            self.update()    
            data = urllib.parse.urlencode({'id': self.root.id, 'round': -99, 'offer': self.root.texts["rounded_reward"]})
            data = data.encode('ascii')
            if URL == "TEST":
                response = "ok"
            else:
                try:
                    with urllib.request.urlopen(URL, data = data) as f:
                        response = f.read().decode("utf-8") 
                except Exception:
                    pass
            if "ok" in response:                     
                break              
            sleep(5)







Intro = (InstructionsFrame, {"text": intro, "proceed": True, "height": 22})
Initial = (InstructionsFrame, {"text": login, "proceed": False, "height": 15, "keys": ["g", "G"]})
# HEXACOintro = (InstructionsFrame, {"text": hexacointrotext, "height": 11, "update": ["idNumber"]})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,
         Initial, 
         Intro,
        #  HEXACOintro,
         Ending])
