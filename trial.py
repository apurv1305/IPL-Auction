# from configparser import ConfigParser

# configFile = ConfigParser()
# configFile.read("settings.ini")

# ard_port = configFile.get("Controller", "Port")
# Team_Count = configFile.getint("Team", "Team_count")

# def dummyFunc(name):
#     return name

# teamLst = []
# logoFuncLst = []
# for i in range(1,(Team_Count + 1)):
#     try:
#         teamLst.append(configFile.get("Team", "Team_{}".format(i)))
#         logoFuncLst.append(dummyFunc(configFile.get("Team", "Team_{}".format(i))))
#     except:
#         teamLst.append("Team{}".format(i))
#         logoFuncLst.append(dummyFunc("Team{}".format(i)))


# print(ard_port)
# print(teamLst)
lst = [1,2,3,4,5,6]
new = ["team {}".format(i) if i<7 else "end" for i in range(1,8)]
print(new)