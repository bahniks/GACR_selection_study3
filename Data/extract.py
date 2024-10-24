import os


studies = {"Login": ("id", "condition","reward_order", "token", "winning_block", "winning_trust", "roles", "pairs", "hexaco_id"),
           "Cheating Instructions Control Questions": ("id", "item", "answer"),
           "Cheating 1": ("id", "block", "trial", "version", "source", "condition", "roll", "prediction", "report", "reward", "time", "time1", "time2"), 
           "Cheating 2": ("id", "block", "trial", "version", "source", "condition", "roll", "prediction", "report", "reward", "time", "time1", "time2"), 
           "Selection": ("id", "block", "choice"),
           "Cheating 3": ("id", "block", "trial", "version", "source", "condition", "roll", "prediction", "report", "reward", "time", "time1", "time2"),
           "Trust Control Questions": ("id", "item", "answer"),  
           "Trust": ("id", "block", "pair", "role", "condition", "reward_order", "endowment", "return0", "return1", "return2", "return3", "return4", "return5", "sent"),
           "Trust Results": ("id", "block", "sent", "returned"),
           "Cheating Round 4 Control Questions": ("id", "item", "answer"),                      
           "Selection": ("id", "block", "choice"),
           "Cheating 4": ("id", "block", "trial", "version", "source", "condition", "roll", "prediction", "report", "reward", "time", "time1", "time2"),
           "Cheating Results": ("id", "block", "outcome", "wins", "reward", "version"),
           "Trust": ("id", "block", "pair", "role", "condition", "reward_order", "endowment", "return0", "return1", "return2", "return3", "return4", "return5", "sent"),
           "Trust Results": ("id", "block", "sent", "returned"),        
           "Selection": ("id", "block", "choice"),   
           "Cheating 5": ("id", "block", "trial", "version", "source", "condition", "roll", "prediction", "report", "reward", "time", "time1", "time2"),
           "Cheating Results": ("id", "block", "outcome", "wins", "reward", "version"),
           "Trust": ("id", "block", "pair", "role", "condition", "reward_order", "endowment", "return0", "return1", "return2", "return3", "return4", "return5", "sent"),
           "Trust Results": ("id", "block", "sent", "returned"),  
           "Token": ("id", "paid"),  
           "Selection": ("id", "block", "choice"),   
           "Cheating 6": ("id", "block", "trial", "version", "source", "condition", "roll", "prediction", "report", "reward", "time", "time1", "time2"),
           "Cheating Results": ("id", "block", "outcome", "wins", "reward", "version"),
           "Trust": ("id", "block", "pair", "role", "condition", "reward_order", "endowment", "return0", "return1", "return2", "return3", "return4", "return5", "sent"),
           "Trust Results": ("id", "block", "sent", "returned"),             
           "Lottery": ("id", "choice1", "choice2", "choice3", "choice4", "choice5", "chosen", "win"),
           "Dice Lottery": ("id", "rolls", "reward"),
           "Anchoring": ("id", "trial", "item", "true", "comparison1", "time1", "estimate1", "time2", "condition", "response", "time3", "estimate2", "time4"),
            "Political Skill": ("id", "item", "answer"),           
           "TDMS": ("id", "item", "answer"),
           "Demographics": ("id", "sex", "age", "language", "student", "field"),
           "Comments": ("id", "comment"),
           "Ending": ("id", "reward", "chosen_block")}

frames = ["Initial",
          "Login",
          "Intro",
          "HEXACOintro",
          "CheatingInstructions",
          "Cheating",
          "Instructions2",
          "Cheating",
          "Instructions3",
          "Cheating",
          "Info3",
          "InstructionsTrust",
          "Trust",
          "WaitTrust",
          "TrustResult",
          "Instructions4Check",
          "Cheating",
          "OutcomeWait",          
          "Trust",
          "WaitTrust",
          "TrustResult",
          "Instructions5",
          "Cheating",
          "OutcomeWait",
          "Trust",
          "WaitTrust",
          "TrustResult",
          "Instructions6",
          "Cheating",
          "OutcomeWait",
          "Trust",
          "WaitTrust",
          "TrustResult",
          "EndCheating",
          "Lottery",
          "LotteryWin",
          "LotteryInstructions",
          "DiceLottery",
          "AnchoringInstructions", 
          "Anchoring",
          "QuestInstructions",
          "PoliticalSkill",
          "TDMS",
          "HEXACOinfo",
          "Demographics",
          "Ending",
          "end"
         ]

read = False
compute = True

if read:
    for study in studies:
        with open("{} results.txt".format(study), mode = "w") as f:
            f.write("\t".join(studies[study]))

    with open("Time results.txt", mode = "w") as times:
        times.write("\t".join(["id", "order", "frame", "time"]))

    files = os.listdir()
    for file in files:
        if ".py" in file or "results" in file or "file.txt" in file or ".txt" not in file:
            continue

        with open(file, encoding = "utf-8") as datafile:
            #filecount += 1 #
            count = 1
            for line in datafile:

                study = line.strip()
                if line.startswith("time: "):
                    with open("Time results.txt", mode = "a") as times:
                        print(frames[count-1])
                        print(line.split()[1])
                        times.write("\n" + "\t".join([file, str(count), frames[count-1], line.split()[1]]))
                        count += 1
                        continue
                if study in studies:
                    with open("{} results.txt".format(study), mode = "a") as results:
                        for line in datafile:
                            content = line.strip()
                            if not content or content.startswith("time: "):
                                break
                            else:
                                results.write("\n" + content)

if compute:
    times = {frame: [] for frame in frames}
    with open("Time results.txt") as t:
        t.readline()
        for line in t:
            _, num, frame, time = line.split("\t")    
            if int(num) > 1:            
                times[frame0].append(float(time) - t0)            
            t0 = float(time)
            frame0 = frame

    total = 0
    for frame, ts in times.items():
        if ts:
            print(frame)        
            print(round(sum(ts)/len(ts), 2))
            if frame != "Ending":
                total += sum(ts)/len(ts)
    print("Total")
    print(round(total / 60, 2))

            
