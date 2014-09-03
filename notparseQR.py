 searchString = '\"command\":\"'
    commandIndex = QRCode.find(searchString)
    commandString = ""def parseOutCommand(QRCode):
    # Find the command string from the QR Code
    # Example string {"command":"F88R6","....}
    searchString = '\"command\":\"'
    commandIndex = QRCode.find(searchString)
    commandString = ""

    # Did we find the string
    if (commandIndex != -1):
        # Yes, set commandIndex to be the START of the direction string part
        commandIndex = commandIndex+len(searchString)
        tempString = QRCode[commandIndex:] # tempString now equal to F88R6","...}

        commandIndex = tempString.find('\",')
        if (commandIndex != -1):
            commandString = tempString[0:commandIndex]
    return commandString


# Main
#temp = parseOutCommand('\"command\":\"F88R6\",\"....}')
#print(temp)
