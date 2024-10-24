#! python3

import sys
import os

sys.path.append(os.path.join(os.getcwd(), "Stuff"))


from gui import GUI

from quest import QuestInstructions
from intros import Initial, Intro, Ending, HEXACOintro
from demo import Demographics
from cheating import CheatingInstructions, Cheating, Instructions2, Instructions3, Instructions4Check, Instructions5, Instructions6
from cheating import EndCheating, Login, OutcomeWait, Info3
from lottery import Lottery, LotteryWin
from dicelottery import LotteryInstructions, DiceLottery
from trustgame import WaitTrust, Trust, TrustResult, InstructionsTrust
from questionnaire import PoliticalSkill, TDMS, HEXACOinfo
from anchoring import Anchoring, AnchoringInstructions
from comments import Comments

frames = [Initial,
          Login,
          Intro,       
          HEXACOintro,   
          CheatingInstructions,
          Cheating,
          Instructions2,
          Cheating,
          Instructions3, # selection
          Cheating,
          Info3,
          InstructionsTrust,
          Trust, # trust instructions + decision
          WaitTrust,
          TrustResult,
          Instructions4Check, # selection + info about trust
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
          EndCheating,
          Lottery,
          LotteryWin,
          LotteryInstructions,
          DiceLottery,
          AnchoringInstructions, 
          Anchoring,
          QuestInstructions,
          PoliticalSkill,
          TDMS,
          HEXACOinfo,
          Demographics,
          Comments,
          Ending
         ]

#frames = [Login, HEXACOinfo]

if __name__ == "__main__":
    GUI(frames, load = os.path.exists("temp.json"))