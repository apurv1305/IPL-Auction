# all the imports
from tkinter import *
from gtts import gTTS
from playsound import playsound
import threading
import serial
import pyttsx3
import time
import random
import os
from configparser import ConfigParser

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Starting up the GUI
root = Tk()

# Window title
root.wm_title("अपूर्वAUCTIONEER")
icon = PhotoImage(file = "images/Aesthetics/icons/Icon.png")
root.iconphoto(False, icon)
# FUll Screen Width Variable
width = root.winfo_screenwidth()
height = root.winfo_screenheight()

# defining Geometery of Tkinter window
# root.geometry("%dx%d" % (width, height))
root.attributes("-fullscreen", True)

#------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Reading Configuration file for settings 
configFile = ConfigParser()
configFile.read("settings.ini")

com_port = configFile.get("Controller", "Port")
baudrate = configFile.getint("Controller", "Baudrate")
Team_Count = configFile.getint("Team", "Team_count")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Important Function Definitions
def Image_Insert(img_name, folder_name):                 # To generate image location variables
    try:
        File = PhotoImage(file="images/{}/{}.png".format(folder_name, img_name))
    except:
        File = PhotoImage(file="images/{}/blank.png".format(folder_name))
    return File

def Player_Image_list():                    # TO generate list of image location variables
    image_list = []
    with open('database/Database.csv') as data:
        Read_list = []
        lines = data.readlines()
        for line in lines:
            Read_list.append(line.strip().split(","))
        Read_list = Read_list[1:]
        for players_name in Read_list:
            # image_list.append(Image_Insert(players_name[1]))
            image_list.append(Image_Insert(players_name[1], "Players"))
    return image_list

def Team_lst_generator():       # This generates a list of all the teams based on the team count nad team names in the config file
    teamList = []
    for i in range(1,(Team_Count + 1)):
        try:
            teamList.append(configFile.get("Team", "Team_{}".format(i)))
        except:
            teamList.append("Team{}".format(i))
    return teamList

# Function Calls
player_img_list = Player_Image_list()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Main Function

def MainFunction():
    
    # Function Definitions
    def Speak_eng(text):                                    # Function for GTTS speaking English- Indian Accent
        language = 'en'
        obj1 = gTTS(text=text, tld="co.in", lang=language, slow=False)
        obj1.save("Temporary.mp3")
        playsound("Temporary.mp3")
        os.remove("Temporary.mp3")
    def Data_reading():                                     # Function to read data from the CSV file and return it
        with open('database/Database.csv') as data:
            Read_list = []
            lines = data.readlines()
            for line in lines:
                Read_list.append(line.strip().split(","))
            return Read_list
    def Auction_completion_checker():                       # Function to Check Auction status, is it complete or not
        counter = 0
        for player in Data_Read_list:
            if int(player[8]) == 0:
                counter = counter + 1
        if counter == 0:
            #Speak_eng("Thank you auctions are concluded")
            return False
        else:
            return True
    def List_Generator(main_list):                          # Function to generate type specific lists of 'x' players each
        marquee_list = []
        Batsmen_list = []
        Bowler_list = []
        AllRounder_list = []
        Wicketkeeper_list = []
        type_list = [marquee_list, Batsmen_list, Bowler_list, AllRounder_list, Wicketkeeper_list]

        unappeared_status = False
        for player in main_list:
            if int(player[8]) == 0:
                unappeared_status = True
            if int(player[8]) != 0:
                unappeared_status = False
            if unappeared_status == True:
                for playerType in range(0, len(player_Type_name)):
                    if player[6] == player_Type_name[playerType]:
                        type_list[playerType].append(player)

        for indice in range(0, len(player_Type_name)):
            random.shuffle(type_list[indice])
            if len(type_list[indice]) > 4:
                type_list[indice] = type_list[indice][0:4]

        return type_list
    def Repetability_Checker(input):                        # Function to prevent consecutive bids from same team
        if input == Bid_input_history[0] and input != "n":
            return True
        if input != Bid_input_history[0] and input != "n":
           Bid_input_history[0] = input
           return False

    # Functions for updating GUI
    def Player_Change(name):                                # Function to update Player info on the GUI wrt the Database
        # Name Change
        names = name.split(" ")
        first = " ".join(names[0:-1])
        canvas.itemconfig(player_last_name, text=names[-1].upper())
        canvas.itemconfig(player_first_name, text=first.upper())

        # Base Price change
        canvas.itemconfig(Bid_Team_text, text = "BASE PRICE")
        canvas.itemconfig(Base_price_text, text = Base_Price)
        canvas.itemconfig(currency_text, text = "LACS")
        # Base Price Frame Update
        canvas.coords(Bid_frame, width/2-80, 558, width/2+80, 673)

        # player photo border change
        canvas.coords(border, width/2-199, 15, width/2+198, 436,)
        # player photo change
        player_img = player_img_list[Player_index]
        canvas.itemconfig(player_image, image = player_img)

        # Player Detail Change
        canvas.itemconfig(player_hand_txt, text = Player_hand.upper())
        canvas.itemconfig(player_type_txt, text = Player_type.upper())

        # Logo Change
        canvas.coords(logo_1, width/2-199, 363)
        canvas.coords(logo_1_cp, width/2+199, 363)
        # Logo Image change
        canvas.itemconfig(logo_1, image = Unsold_logo)
        canvas.itemconfig(logo_1_cp, image = Unsold_logo)

        # Stamp Tag Removal
        canvas.itemconfig(stamp, image = TransparentTag)
    def Bidding_Team_Change(team_name, bid_amt):            # Function to update Bidding team logo flag and Bid Amount on GUI
        # text data
        canvas.itemconfig(Bid_Team_text, text=team_name.upper())
        canvas.itemconfig(Base_price_text, text=bid_amt)
        # logo Image
        canvas.itemconfig(logo_1, image=LOGO_Image_lst[indexes])
        canvas.itemconfig(logo_1_cp, image=LOGO_Image_lst[indexes])
    def Update_Purse(owner, sold_amt):                      # Function to Update Purse availbility data on  the GUI
        with open('database/Team Purse.csv') as Purse_Gui:
            Team_Purse_list = []
            lines = Purse_Gui.readlines()
            for line in lines:
                Team_Purse_list.append(line.strip().split(","))
            
            # Updating purse amount after the bid ends
            for team in Team_Purse_list:
                if owner == team[0]:
                    team[1] = str(int(team[1]) - int(sold_amt))
            
            # bringing comma "," in amt for personal visual  reasons
            for Team in Team_Purse_list:
                if len(Team[1]) == 4:
                    Team[1] = str(Team[1][0] + "," + Team[1][1:])

        # Writer File
        Write_Purse_data = Team_Purse_list

        # Updating Team Name
        canvas.itemconfig(Team_1_txt, text = Team_Purse_list[0][0].upper())
        canvas.itemconfig(Team_2_txt, text = Team_Purse_list[1][0].upper())
        canvas.itemconfig(Team_3_txt, text = Team_Purse_list[2][0].upper())
        canvas.itemconfig(Team_4_txt, text = Team_Purse_list[3][0].upper())
        canvas.itemconfig(Team_5_txt, text = Team_Purse_list[4][0].upper())
        canvas.itemconfig(Team_6_txt, text = Team_Purse_list[5][0].upper())
        
        #Updating Purse Amount
        canvas.itemconfig(Team_1_Purse, text = str(Team_Purse_list[0][1]))
        canvas.itemconfig(Team_2_Purse, text = str(Team_Purse_list[1][1]))
        canvas.itemconfig(Team_3_Purse, text = str(Team_Purse_list[2][1]))
        canvas.itemconfig(Team_4_Purse, text = str(Team_Purse_list[3][1]))
        canvas.itemconfig(Team_5_Purse, text = str(Team_Purse_list[4][1]))
        canvas.itemconfig(Team_6_Purse, text = str(Team_Purse_list[5][1]))

        # Removing comma "," added before so as to write it to the file
        for teams in Write_Purse_data:
            if "," in teams[1]:
                amount = teams[1]
                amt_lst = amount.split(",")
                str2 = ""
                teams[1] = str2.join(amt_lst)

        # Writing data back to file
        with open('database/Team Purse.csv', 'w') as purse_file:
            str1 = ","
            for purse_data in Write_Purse_data:
                str1 = ","
                purse_file.write(str1.join(purse_data))
                purse_file.write("\n")
    def Display_Purse():                                    # Function to display the updated Purse data on GUI
        with open('database/Team Purse.csv') as Purse_Gui:
            Team_Purse_list = []
            lines = Purse_Gui.readlines()
            for line in lines:
                Team_Purse_list.append(line.strip().split(","))
            for Team in Team_Purse_list:
                if len(Team[1]) == 4:
                    Team[1] = str(Team[1][0] + "," + Team[1][1:])


        # Updating Team Name
        canvas.itemconfig(Team_1_txt, text = Team_Purse_list[0][0].upper())
        canvas.itemconfig(Team_2_txt, text = Team_Purse_list[1][0].upper())
        canvas.itemconfig(Team_3_txt, text = Team_Purse_list[2][0].upper())
        canvas.itemconfig(Team_4_txt, text = Team_Purse_list[3][0].upper())
        canvas.itemconfig(Team_5_txt, text = Team_Purse_list[4][0].upper())
        canvas.itemconfig(Team_6_txt, text = Team_Purse_list[5][0].upper())
        
        #Updating Purse Amount
        canvas.itemconfig(Team_1_Purse, text = (Team_Purse_list[0][1]))
        canvas.itemconfig(Team_2_Purse, text = (Team_Purse_list[1][1]))
        canvas.itemconfig(Team_3_Purse, text = (Team_Purse_list[2][1]))
        canvas.itemconfig(Team_4_Purse, text = (Team_Purse_list[3][1]))
        canvas.itemconfig(Team_5_Purse, text = (Team_Purse_list[4][1]))
        canvas.itemconfig(Team_6_Purse, text = (Team_Purse_list[5][1]))
    def Ending_Auction():                                   # Function for showing the end screnn GUI after completing auctions
        # Erasing Name Text
        canvas.itemconfig(player_last_name, text="")
        canvas.itemconfig(player_first_name, text="")

        # Erasing Image Frame and Changing to logo
        # player photo border change
        canvas.coords(border, 0, 0, 1, 1)
        # player photo change
        canvas.itemconfig(player_image, image = Logo_main)
        
        # Logo coordiantes Change
        canvas.coords(logo_1, 0, 0)
        canvas.coords(logo_1_cp, width, 0)
        # Logo Image change
        canvas.itemconfig(logo_1, image = Unsold_logo)
        canvas.itemconfig(logo_1_cp, image = Unsold_logo)

        # Base Price change
        canvas.itemconfig(Bid_Team_text, text = "AUCTIONS ARE COMPLETE")
        canvas.itemconfig(Base_price_text, text = "THANK-YOU FOR JOINING")
        canvas.itemconfig(currency_text, text = "")
        # Base Price Frame Update
        canvas.coords(Bid_frame, 0, 0, 1, 1)

        # Player Detail Change
        canvas.itemconfig(player_hand_txt, text = "")
        canvas.itemconfig(player_type_txt, text = "")        

        # Stamp Tag Removal
        canvas.itemconfig(stamp, image = TransparentTag)

        # Removing Purse details
        # Removing Team Name
        canvas.itemconfig(Team_1_txt, text = "")
        canvas.itemconfig(Team_2_txt, text = "")
        canvas.itemconfig(Team_3_txt, text = "")
        canvas.itemconfig(Team_4_txt, text = "")
        canvas.itemconfig(Team_5_txt, text = "")
        canvas.itemconfig(Team_6_txt, text = "")
        #Updating Purse Amount
        canvas.itemconfig(Team_1_Purse, text = "")
        canvas.itemconfig(Team_2_Purse, text = "")
        canvas.itemconfig(Team_3_Purse, text = "")
        canvas.itemconfig(Team_4_Purse, text = "")
        canvas.itemconfig(Team_5_Purse, text = "")
        canvas.itemconfig(Team_6_Purse, text = "")

        # Changing Head Text



    #Speech Function Definitions
    def Auction_Intro():
        Speak_eng("A very warm welcome to all the Team Owners who have joined us for the GPL Player Auctions 2021")
        Speak_eng("The previous editions of the game turned out to be very succesfull and we hope the same this time around starting With today's auctions")
        Speak_eng("So without any further adoo let's get started with todays' Auctions")
        playsound("audio/clap.wav")
    def Auction_Rules():
        Speak_eng("Let me now recite the rules for today's bidding process")
        Speak_eng("Every team would have around " + str(Team_Purse) + " Lacs in there kitty to Build the best possible team")
        Speak_eng("No team shall be made to make two consecutive bids")
        Speak_eng("The Player would be sold to the Team making the highest bid")
        Speak_eng("Every Team can only buy up to" + str(Number_Foreign_Players) +" Foreign players")
        Speak_eng("Up till 100 lacs the bid increment would be 5 lacs per bid")
        Speak_eng("From 100 to 200 Lacs the increment shall be 10 lacs per bid")
        Speak_eng("There after from 200 to 1000 lacs it will be restricted to 20 Lacs")
        Speak_eng("Post 1000 Lacs the increment would be fixed at 50 Lacs per bid")
        time.sleep(3)
        Speak_eng("Okay! So its now time to get started with our first set of players")
    def Set_Announcement(Set_type, Set_number, indice):
        Set_profile = Set_type + " Set Number " + str(Set_number)
        #logic for first set speech
        if Set_number == 1 and indice == 0:
            Speak_eng("It's " + Set_profile)
        #Logic for Rest of the set announcements
        else:
        
            speech_list = []
            speech_list.append("The next set we have is " + Set_profile)
            speech_list.append("Okay. So we now have " + Set_profile)
            speech_list.append("Moving on to the next set, we have " + Set_profile)
            speech_list.append("Welcome back gentlemen after that short break. We now have " + Set_profile)
            random.shuffle(speech_list)
            Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
    def Player_Announcement(Name, Country, Base_price, Detail, players):
        basePrice = str(Base_price) + "Lacs"
        country = " from" + Country
        detail = " a " + Detail
        speech_list = []
        sec_speech = []
    
        #loop for the first player of the set
        if players == player_Type_list[indexx][0]:
            speech_list.append("The First Player in this set is " + Name + detail + " asking " + basePrice)
            speech_list.append("So, "+ Name + country + " is the first player in this set. A "+ Detail + " with a base price of "+ basePrice)
            random.shuffle(speech_list)
            Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
    
        #loop for rest of the players of set
        else:
            speech_list.append("The Next player in this set is " + Name + detail + country + " asking " + basePrice)
            speech_list.append("Okay. So, the player we have next up is " + detail + country + ", " + Name + " with a base price of " + basePrice)
            speech_list.append("Moving on to the next player we have "+ Name + country + detail + " hoping to get atleast " + basePrice)
            speech_list.append("Asking " + basePrice + " is our next player " + Name + ", " + detail + country)
            random.shuffle(speech_list)
            Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
    
        #Playing the intro sound
        playsound(Player_intro_Music)

        #logic for secondary speech synthesis
        sec_speech.append("Is anyone interested. Any one..")
        sec_speech.append("looking for an opening bid for " + Name + " Anyone interested")
        sec_speech.append(Name + " asking " + basePrice + ", anyone intrested")
        random.shuffle(sec_speech)
        Speak_eng(sec_speech[random.randint(0,(len(sec_speech) - 1))])
    def Bid_Announcement(BidCounter, CurrentTeam, CurrentBid, Name):
        currentbid = str(CurrentBid) + "Lacs"
        speech_list = []
        if BidCounter == 0:
            speech_list.append("Thank You, " + CurrentTeam + " for starting the Bid")
            speech_list.append("I have my opening bid for " + Name + "Thank you " + CurrentTeam)
            speech_list.append("It's " + CurrentTeam + "who's started the bid. Thank you sir")
            speech_list.append(CurrentTeam + " has made the opening bid for Mister " + Name)
            speech_list.append("Okay. I can see the opening from " + CurrentTeam + ". Thank you gentlemen!")
            speech_list.append("We have are first bidder! Thank you " + CurrentTeam + " for opening the bid")
            random.shuffle(speech_list)
            Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
            Speak_eng("Anyone interested, the bid is currrently with " + CurrentTeam + " at " + currentbid)
        else:
            speech_list.append("The bid now jumps to " + CurrentTeam + " at " + currentbid)
            speech_list.append("Okay so now i have a new bid for " + currentbid + " from " + CurrentTeam)
            speech_list.append("That's a new bid from " + CurrentTeam + " for " + currentbid)
            speech_list.append("I can smell a bidding war, it's " + CurrentTeam + "who hold the bid for " + currentbid)
            speech_list.append(Name + " is now bidded at " + currentbid + " by " + CurrentTeam)
            speech_list.append("I can see " + CurrentTeam + " making a bid for " + Name + " at " + currentbid)
            speech_list.append(currentbid + " is the bid made by " + CurrentTeam)
            speech_list.append(CurrentTeam + " have made a new " + currentbid + " bid")
            speech_list.append("The bid has now passed on to " + CurrentTeam + " at " + currentbid)
            random.shuffle(speech_list)
            Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
    def Alarm_Announcement(Counter, BidCounter, CurrentBid, Name, details):
        currentAmount = str(CurrentBid) + "Lacs"
        speech_list = []
        if player == player_Type_list[index][0]:
            if BidCounter == 0:       
                if Counter == 3800 or Counter == 5000:
                    speech_list.append("Please, asking an opening bid for " + Name + " at " + currentAmount)
                    speech_list.append("I see no bids in the room." + Name + " asking for an opening bid of " + currentAmount)
                    speech_list.append("Anyone. Any one interested, asking " + currentAmount + " for " + Name)
                    speech_list.append("Is anyone interested in " + Name + " at " + currentAmount + "I am seeing no opening bids")
                    speech_list.append(Name + " asking " + currentAmount + " Any one intereseted in this " + details)
                    speech_list.append("Mister " + Name + " waiting for an opening bid. Priced at " + currentAmount)
                    speech_list.append("A " + details + " asking " + currentAmount)
                    speech_list.append("Looks like no one is interested in this " + details + " asking " + currentAmount)
                    random.shuffle(speech_list)
                    Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
            elif Counter == 1800 or Counter == 3400 or Counter == 4500:
                speech_list.append("A " + details + " currently at " + currentAmount)
                speech_list.append(Name + " a " + details + " currently at " + currentAmount)
                speech_list.append("I am not seeing any more bids...Any one interested or I am selling it to " + Current_Team  + " for " + currentAmount)
                speech_list.append("I am not seeing any bids. This is the final warning. The bid is with " + Current_Team + " at " + currentAmount)
                speech_list.append("I am selling Mister " + Name + " to " + Current_Team + " for " + currentAmount + " Is anyone interested?")
                speech_list.append(Current_Team + " holding the bid for " + Name + " at " + currentAmount + "anyone interested in this " + details)
                speech_list.append("I am not seeing any more interest, i will sell this " + details + " to " + Current_Team)
                speech_list.append("Final Call for " + Name + " Currently with " + Current_Team + " at " + currentAmount)
                speech_list.append("Looks like no one is interested. Please make a bid or " + Name + " is sold to " + Current_Team + " for " + currentAmount)
                random.shuffle(speech_list)
                Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
        else:
            if BidCounter == 0:       
                if Counter == 3500 or Counter == 4800:
                    speech_list.append("Please, asking an opening bid for " + Name + " at " + currentAmount)
                    speech_list.append("I see no bids in the room." + Name + " asking for an opening bid of " + currentAmount)
                    speech_list.append("Anyone. Any one interested, asking " + currentAmount + " for " + Name)
                    speech_list.append("Is anyone interested in " + Name + " at " + currentAmount + "I am seeing no opening bids")
                    speech_list.append(Name + " asking " + currentAmount + " Any one intereseted in this " + details)
                    speech_list.append("Mister " + Name + " waiting for an opening bid. Priced at " + currentAmount)
                    speech_list.append("A " + details + " asking " + currentAmount)
                    speech_list.append("Looks like no one is interested in this " + details + " asking " + currentAmount)
                    random.shuffle(speech_list)
                    Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
            elif Counter == 1800 or Counter == 3400 or Counter == 4500:
                speech_list.append("A " + details + " currently at " + currentAmount)
                speech_list.append(Name + " a " + details + " currently at " + currentAmount)
                speech_list.append("I am not seeing any more bids...Any one interested or I am selling it to " + Current_Team  + " for " + currentAmount)
                speech_list.append("I am not seeing any bids. This is the final warning. The bid is with " + Current_Team + " at " + currentAmount)
                speech_list.append("I am selling Mister " + Name + " to " + Current_Team + " for " + currentAmount + " Is anyone interested?")
                speech_list.append(Current_Team + " holding the bid for " + Name + " at " + currentAmount + "anyone interested in this " + details)
                speech_list.append("I am not seeing any more interest, i will sell this " + details + " to " + Current_Team)
                speech_list.append("Final Call for " + Name + " Currently with " + Current_Team + " at " + currentAmount)
                speech_list.append("Looks like no one is interested. Please make a bid or " + Name + " is sold to " + Current_Team + " for " + currentAmount)
                random.shuffle(speech_list)
                Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
    def Sold_Unsold_Announcement(BidCounter, Name, details):
        playsound(Hammer_sound)
        speech_list = []
        if BidCounter == 0:
            canvas.itemconfig(stamp, image = Unsold_Tag)
            
            speech_list.append("Okay. so there are no bids for " + Name + "He goes unsold in this round of bidding")
            speech_list.append("I don't see " + Name + " getting an opening bid. So he goes unsold")
            speech_list.append("I don't see any buyers for Mr. " + Name + "So he goes unsold")
            speech_list.append("I don't see " + Name + " getting an opening bid. So he goes unsold")
            speech_list.append(Name + " doesn't seems to get a buyer and thus goes unsold")
            speech_list.append("This " + details + " doesn't seems to get a bid and therefore goes unsold")
            random.shuffle(speech_list)
            Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
        else:
            canvas.itemconfig(stamp, image = Sold_Tag)
            
            Money = str(Sold_Amount) + "Lacs"
            TeamOwner = Team_Owner
            speech_list.append("There seems to be no more bidding and hence "+ Name + " sold to " + TeamOwner + " for " + Money)
            speech_list.append("Congratulations " + TeamOwner + Name + " has been sold for " + Money)
            speech_list.append("I don't see any more bidings for this " + details + "Therefore "+Name+" sold to "+TeamOwner+" for " + Money)
            speech_list.append("And Sold. "+Name + " goes to "+TeamOwner+" for "+Money)
            speech_list.append("Sold. OMG! after such a ferocious bidding war finally "+TeamOwner+" manages to buy "+Name+" for "+Money)
            speech_list.append(Money+" is the the amount and "+Name+" sold to "+TeamOwner)
            speech_list.append(TeamOwner+" with "+Money+" and sold,"+Name+" goes to "+TeamOwner)
            speech_list.append(Name+" goes to "+TeamOwner+" for "+Money+"Congratulations to "+TeamOwner)
            random.shuffle(speech_list)
            Speak_eng(speech_list[random.randint(0,(len(speech_list) - 1))])
            playsound(Claps)
    
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Global Variables
    player_Type_name = ["Marquee Players", "Batsmen", "Bowlers", "All-Rounders", "Wicketkeepers"]       
    Arduino_Input = serial.Serial(com_port, baudrate)
    Data_Read_list = []
    Data_Write_list = []
    player_state = True
    Sold_Status_lst = ["Sold", "Unsold"]
    Team_List = Team_lst_generator()    # team list based on config file
    # Team state list for checking with arduino ["Team 1", "Team 2", "Team 3", "Team 4", "Team 5", "Team 6",...... ,"End"]
    Team_State_list = ["Team {}".format(i) if i < (Team_Count + 1) else "End" for i in range(1, Team_Count + 2)]
    str1 = ","
    Bid_input_history = ["0"]
    Team_Purse = configFile.getint("Team", "Team_Purse")
    Number_Foreign_Players = 8
    Set_Intro_Music = "audio/Hero_intro.mp3"
    Player_intro_Music = "audio/intro.wav"
    Hammer_sound = "audio/Bid done.mp3"
    Claps = "audio/clap.wav"

    # Calling Functions and making lists
    Data_Read_list = Data_reading()
    Data_Read_list = Data_reading()
    Header_Data = Data_Read_list[0]
    Data_Read_list = Data_Read_list[1:]
    Data_Write_list = Data_Read_list
    Auction_Check = Auction_completion_checker()
    Set_Counter = 1

    Auction_Intro()
    Auction_Rules()

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------

    # Main While Loop
    while Auction_Check:
    
        #Calling a function to generate List of list of specific type players and arrange them randomly
        player_Type_list = List_Generator(Data_Read_list)
        
        #Main FOR loop logic to iterate through individual Player types from the Player_type_list and to write it to file
        for index in range(0,len(player_Type_name)): 

            #To check if a type of players are finished and if so skip those to next set
            if len(player_Type_list[index]) == 0:
                continue
        
            #condition for speech synthesis for set announcements
            playsound(Set_Intro_Music)
            Set_Announcement(player_Type_name[index], Set_Counter, index)
        
            #Main loop for looping through all the players from a specific player type list and writing all the data to file
            for player in player_Type_list[index]:
            
                #Local Variable Definitions per player
                player_state = True                         # player active satus to help ending bid
                Base_Price = int(player[3])                 # Base Price of player from the list created by reading file
                Player_Name = str(player[1])                # Player name from the list Data_read file
                Player_Country = str(player[2])             # Player Country
                Player_index = int(player[0])
                Team_Owner = ""                             # initiation of a team owner string in order to use it
                Current_Bid = Base_Price                    # Curren bid variable to stire current bid amount
                Sold_Amount = 0                             # Sold Amount variable to store Sold amount data
                Sold_Status = ""                            # SOld status sores the sold status of the player form list
                Bid_Counter = 0                             # A Bid counter to count the no. of bids
                counter = 0                                 # To keep count of time for delayed ALARMS
                Delay_status = False                        # Delay Status to make the plsyer unsold if no bids are seen for some time
                Player_hand = player[7]
                Player_type = player[10]
                Player_Detail = Player_hand + " " + Player_type
                indexx = index

                Arduino_Input.flushInput()

                # Updating GUI Player Info
                Player_Change(Player_Name)

                # Display Purse amounts
                Display_Purse()

                #Function call for speech synthesis to introduce and announce player
                Player_Announcement(Player_Name, Player_Country, Base_Price, Player_Detail, player)


                #Loop to have bidding untill a player is sold or unsold and to write that data to file
                while player_state:                         
                    input_data = Arduino_Input.readline().decode().strip()  #Input from Arduino
                    Repeat_state = Repetability_Checker(input_data)         #Repeat_state ensures no one is able to make consecutive bids

                    #Logic to detect the team who had bided and keeping time
                    for indexes in range(0,(len(Team_State_list) - 1)):                                
                        #IF loop to detect which team bidded and is there a repeat case
                        if input_data == Team_State_list[indexes] and Repeat_state == False: 
                            Current_Team = Team_List[indexes]
                        
                            #for starting bid or opening bid
                            if Bid_Counter == 0:                            
                                # Update GUI Bid Info
                                Bidding_Team_Change(Current_Team, Current_Bid)

                                Bid_Announcement(Bid_Counter, Current_Team, Current_Bid, Player_Name)
                            # Logic For non opening bids and current bid price increment
                            else:
                                #Bid Increment Logic
                                if Current_Bid < 100 :
                                    Current_Bid = Current_Bid + 5
                                elif Current_Bid >= 100 and Current_Bid < 200:
                                    Current_Bid = Current_Bid + 10
                                elif Current_Bid >= 200 and Current_Bid < 1000:
                                    Current_Bid = Current_Bid + 20
                                elif Current_Bid >= 1000:
                                    Current_Bid = Current_Bid + 50
                            
                                # Update GUI Bid Info
                                Bidding_Team_Change(Current_Team, Current_Bid)

                                #Function call for bid announcements
                                Bid_Announcement(Bid_Counter, Current_Team, Current_Bid, Player_Name)
                        
                            Bid_Counter = Bid_Counter + 1                      
                            counter = 0

                        #For the case if no bidding is seen for some time and to 3 ALARM & terminate bids if no one bids
                        else:
                            #Function call for alarming teams if no bids are seen for some time
                            Alarm_Announcement(counter, Bid_Counter, Current_Bid, Player_Name, Player_Detail)
                        
                            #if even after 2 alarms no bid seen Delay status is made true to terminate the bid making it unsold
                            if Bid_Counter == 0:
                                #condition for counting different time for first player and rest of players in a set
                                if player == player_Type_list[index][0]:
                                    if counter == 6200:
                                        Delay_status = True
                                        break
                                else:
                                    if counter == 5700:
                                        Delay_status = True
                                        break
                            elif Bid_Counter != 0:
                                if counter == 5200:
                                    Delay_status = True
                                    break
                    
                        #Counter to keep time helping in alarmaing and delay status
                        counter = counter + 1           
                        print(counter)
                    #Logic to terminate a bidding via Unsold if no bid made (bid counter = 0) or sold if a bid was made,
                    # and also to Write the data onto the file
                    if (input_data == "End" and Repeat_state == False) or Delay_status == True:

                        #making the player_state false to terminate while loop of the player
                        player_state = False
                    
                        #Emptying bid_input history ti restart it in a new player loop
                        Bid_input_history = ["0"]

                        #logic for if no bid is made for the player, that is unsold and to wrtie that data onto file
                        if Bid_Counter == 0:                                
                            Sold_Status = Sold_Status_lst[-1]               #Assigning Sold status of UNSOLD 
                        
                            #Function call to synthesize Sold/Unsold Announcements
                            Sold_Unsold_Announcement(Bid_Counter, Player_Name, Player_Detail)

                            #opening and writing to file unsold and appearnce
                            with open('database/Database.csv', mode='w', newline='') as data_write_file:
                            
                                #writing appearance as "1" to state that it has appeaered once
                                player[8] = str(1) 
                            
                                #writing header data to the file
                                data_write_file.write(str1.join(Header_Data))   
                                data_write_file.write("\n")
                            
                                #writing list data to the file by joining elements with ","
                                for player_data in Data_Write_list:
                                    str1 = ","
                                    data_write_file.write(str1.join(player_data))
                                    data_write_file.write("\n")
                        
                            #making couner 0 so as to use it again in next player's loop
                            counter = 0            
                    
                        #case for if player has been sold & writing that data to file
                        else:                                               
                            Sold_Status = Sold_Status_lst[0]                #Assiginig UNSOLD sold status
                            Team_Owner = Current_Team                       #Assigning the buying team
                            Sold_Amount = Current_Bid                       #Assigning the sold amount

                            # Function call for updating Purse Details
                            Update_Purse(Team_Owner, Sold_Amount)
                            
                            #Function call to synthesize speech for Sold/unsold Announcement
                            Sold_Unsold_Announcement(Bid_Counter, Player_Name, Player_Detail)

                            #Writing the list data onto the file
                            with open('database/Database.csv', mode='w', newline='') as data_write_file:
                                player[4] = Sold_Status_lst[0]
                                player[5] = str(Sold_Amount)
                                player[9] = Team_Owner
                                player[8] = "1"
                            
                                #writing header data to the file
                                data_write_file.write(str1.join(Header_Data))
                                data_write_file.write("\n")
                            
                                #writing list data to the file by joining the elements with ","
                                for player_data in Data_Write_list:
                                    str1 = ","
                                    data_write_file.write(str1.join(player_data))
                                    data_write_file.write("\n")

                            #counter made zero to ensure its use in next loop cycle
                            counter = 0

            #To check the condition for Auction completion
            Auction_Check = Auction_completion_checker()
            if Auction_Check == True:
                Speak_eng("We will now take a 1 minute break")
                print("We will now take a 1 minute break")
                #time.sleep(20)
                print("Break over")
            Auction_Check = Auction_completion_checker()

        #Set Couter incrementation to keep the set counts
        Set_Counter = Set_Counter + 1
        print(Set_Counter)

    # Ending screen for Auctions
    Ending_Auction()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------


# Assignments
Logo_main = Image_Insert("LOGO1", "Aesthetics")   # Logo Image

Unsold_logo = Image_Insert("unsold", "TeamLogos")    # Intializing variable for starting logo flag of no bids

# Flag logo variables for stamp tags
Unsold_Tag = Image_Insert("unsoldTag", "FlagTags")  
Sold_Tag = Image_Insert("soldTag", "FlagTags")
TransparentTag = Image_Insert("transparent", "FlagTags")

# Team Logo Flags variable and list
RCB_logo = Image_Insert("Royal Challengers Bangalore", "TeamLogos")
CSK_logo = Image_Insert("Chennai Super Kings", "TeamLogos")
RR_logo = Image_Insert("Rajasthan Royals", "TeamLogos")
BH_logo = Image_Insert("Brisbane Heat", "TeamLogos")
SS_logo = Image_Insert("Sydney Sixers", "TeamLogos")
MI_logo = Image_Insert("Mumbai Indians", "TeamLogos")

LOGO_Image_lst = [RCB_logo, CSK_logo, RR_logo, BH_logo, SS_logo, MI_logo]
Team_List = ["Royal Challengers Bangalore", "Chennai Super Kings", "Rajasthan Royals", "Brisbane Heat", "Sydney Sixers", "Mumbai Indians"]
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Creating Canvas for background
canvas = Canvas(root, width=width, height=height)
canvas.pack(fill="both", expand=True)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Background Image on Canvas
bg = Image_Insert("Background", "Aesthetics")
background_img = canvas.create_image(0, 0, image=bg, anchor="nw")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# border of the image
border = canvas.create_rectangle(0, 0, 1, 1, fill="black")
# width/2-199, 15, width/2+198, 436

# Player Image Label
player_image = canvas.create_image(width/2, 225, image = Logo_main)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Current team Bid
Bid_Team_text = canvas.create_text(width/2, 500, text="GPL PLAYER AUCTION - 2021", font=("Bahnschrift SemiBold Condensed", "50", "bold"), fill="white")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Base Price and currency and current bid
Base_price_text = canvas.create_text(width/2, 588, text="", font=("Bison Light", "52"), fill="white")
currency_text = canvas.create_text(width/2, 638, text="", font=("Bahnschrift Condensed", "40"), fill="white")
# Frame
Bid_frame = canvas.create_rectangle(0, 0, 1, 1, outline="white")
# width/2-80, 558, width/2+80, 673

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Team Purse Available
Team_1_txt = canvas.create_text(width/2+230, 40, anchor="w", text="",
                                font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_2_txt = canvas.create_text(width/2+230, 80, anchor="w", text="",
                                font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_3_txt = canvas.create_text(width/2+230, 120, anchor="w", text="",
                                font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_4_txt = canvas.create_text(width/2+230, 160, anchor="w", text="",
                                font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_5_txt = canvas.create_text(width/2+230, 200, anchor="w", text="",
                                font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_6_txt = canvas.create_text(width/2+230, 240, anchor="w", text="",
                                font=("Cambria (Headings)", "13", "bold"), fill="white")
# Variable Purse Amount
Team_1_Purse = canvas.create_text(
    width - 35, 40, anchor="e", text="", font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_2_Purse = canvas.create_text(
    width - 35, 80, anchor="e", text="", font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_3_Purse = canvas.create_text(
    width - 35, 120, anchor="e", text="", font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_4_Purse = canvas.create_text(
    width - 35, 160, anchor="e", text="", font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_5_Purse = canvas.create_text(
    width - 35, 200, anchor="e", text="", font=("Cambria (Headings)", "13", "bold"), fill="white")
Team_6_Purse = canvas.create_text(
    width - 35, 240, anchor="e", text="", font=("Cambria (Headings)", "13", "bold"), fill="white")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Player First Name
player_first_name = canvas.create_text(
    width/2 - 220, 70, anchor="e", text="", font=("Bison Light", "44"), fill="white")
# Player Last Name
player_last_name = canvas.create_text(
    width/2 - 216, 145, anchor="e", text="", font=("Nexa Black", "70", "bold"), fill="white")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Player Details
player_hand_txt = canvas.create_text(
    width/2 - 220, 200, anchor="e", text="", font=("Bison Light", "28"), fill="light blue")
player_type_txt = canvas.create_text(
    width/2 - 220, 240, anchor="e", text="", font=("Nexa Black", "32"), fill="light blue")

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Team Logos
logo_1 = canvas.create_image(
    0,0, image=LOGO_Image_lst[0], anchor="e")
# width/2-199, 363

logo_1_cp = canvas.create_image(
    width, 363, image=LOGO_Image_lst[0], anchor="w")
# width/2+199, 363

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Sold/Unsold stamp tag
stamp = canvas.create_image(width/2, height/2)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Threading the Main Loop on a seperate thread to prevent deadlock of UI 
MainLoop_Thread = threading.Thread(target=MainFunction)
MainLoop_Thread.start()

root.mainloop()
