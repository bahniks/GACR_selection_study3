#! python3

import sys
import os

sys.path.append(os.path.join(os.getcwd(), "Stuff"))


from gui import GUI

from quest import QuestInstructions #, Hexaco
from intros import Initial, Intro, Ending #, HEXACOintro
from demo import Demographics
from cheating import CheatingInstructions, Cheating, Instructions2, Instructions3, Instructions4, Instructions5, Instructions6
from cheating import EndCheating, Login, OutcomeWait, VotingResult, Perception, Debrief, FinalWait
from lottery import Lottery, LotteryWin
from dicelottery import LotteryInstructions, DiceLottery
from trustgame import Wait, Trust, TrustResult
#from trustgame import DictatorFeelings2, WaitResult2, DictatorEnd
#from questionnaire import TEQ, RSMS, PoliticalWill
#from tosca import TOSCA

frames = [Initial,
          Login,
          Intro,          
          CheatingInstructions,
          Cheating,
          Instructions2,
          Cheating,
          Instructions3, # selection
          Cheating,
          OutcomeWait,
          Trust, # trust instructions + decision
          Wait,
          TrustResult,
          Instructions4, # selection + info about trust
          Cheating,
          OutcomeWait,
          Trust,
          Wait,
          TrustResult,
          Instructions5, # selection + info about trust
          Cheating,
          OutcomeWait,
          Trust,
          Wait,
          TrustResult,
          Instructions6, # selection + info about trust and payment for info
          Cheating,
          OutcomeWait,
          Trust,
          Wait,
          TrustResult,
          #Debrief,    
          EndCheating,
          Lottery,
          LotteryWin,
          LotteryInstructions,
          DiceLottery,
          #QuestInstructions,
          #RSMS,
          #TEQ,
          #TOSCA,
          #PoliticalWill,
          #HEXACOinfo,
          Demographics,
          Ending
         ]

#frames = [Login, HEXACOinfo]

if __name__ == "__main__":
    GUI(frames, load = os.path.exists("temp.json"))