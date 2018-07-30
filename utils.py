'''
Functions
'''

#Checks if player exists. If json is empty, then player doesn't exist
def isPlayer(playerFile):
    if len(playerFile) == 0:
        return False
    else:
        return True

#Checks if just first or last name entered by counting
def nameCheck(nameInput):
    number_of_names = len(nameInput)
    #print(number_of_names)
    return number_of_names

