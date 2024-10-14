#! python3

import sys
import os

sys.path.append(os.path.join(os.getcwd(), "Stuff"))


from gui import GUI

from quest import QuestInstructions #, Hexaco
from intros import Initial, Intro, Ending #, HEXACOintro
from demo import Demographics
from cheating import CheatingInstructions, Cheating, Instructions2, Instructions3, Instructions4, Instructions5, Instructions6
from cheating import EndCheating, Login, OutcomeWait, Info3 #, VotingResult, Perception, Debrief, FinalWait
from lottery import Lottery, LotteryWin
from dicelottery import LotteryInstructions, DiceLottery
from trustgame import WaitTrust, Trust, TrustResult, InstructionsTrust
#from trustgame import DictatorFeelings2, WaitResult2, DictatorEnd
from questionnaire import PoliticalSkill, TDMS

frames = [Initial,
          Login,
          Intro,          
          CheatingInstructions,
          Cheating,
          Instructions2,
          Cheating,
          Instructions3, # selection
          Cheating,
          Info3,
          #OutcomeWait, # tady asi neni nutne?
          InstructionsTrust,
          Trust, # trust instructions + decision
          WaitTrust,
          TrustResult,
          Instructions4, # selection + info about trust
          Cheating,
          OutcomeWait,          
          Trust,
          WaitTrust,
          TrustResult,
          Instructions5, # selection + info about trust
          Cheating,
          OutcomeWait,
          Trust,
          WaitTrust,
          TrustResult,
          Instructions6, # selection + info about trust and token contribution to charity
          Cheating,
          OutcomeWait,
          Trust,
          WaitTrust,
          TrustResult,
          #Debrief,    
          EndCheating,
          Lottery,
          LotteryWin,
          LotteryInstructions,
          DiceLottery,
          QuestInstructions,
          PoliticalSkill,
          TDMS,
          Demographics,
          Ending
         ]

#frames = [Login, HEXACOinfo]

if __name__ == "__main__":
    GUI(frames, load = os.path.exists("temp.json"))