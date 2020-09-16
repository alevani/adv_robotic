corners = [[0,0],[3,0],[0,3],[3,3]]
edges = [[0,1],[0,2],[3,1],[3,2],[1,0],[2,0],[1,3],[2,3]]

postitionRobot = [0, 0]
oldPostitionRobot = [0, 0]
orientationRobot  = 'S'

input_planner = "SSSSSSEEEEEWNNWWWENNNSWWNNEEEEE"
# input_planner = alex
# postitionRobot = alex_pos
# orientationRobot = 'E'

string_length = len(input_planner)


def del_redundancy(input_planner):
    input_non_redundant = ""
    i = 0
    while (i < string_length):
        if i < string_length:
            if i <string_length-1:
                if input_planner[i] == input_planner[i+1]:
                    input_non_redundant=input_non_redundant+input_planner[i]
                    i = i+1
                else:
                    input_non_redundant=input_non_redundant+input_planner[i]
            else:
                input_non_redundant=input_non_redundant+input_planner[i]
        i+=1
    return input_non_redundant

 

#removed redundancies

cornerAdaptedInput = ""

controllOutput = ""

 

def adaptToCorners(input_non_redundant, postitionRobot):
    global cornerAdaptedInput
    print(input_non_redundant)  
    for c in list(input_non_redundant):
        if postitionRobot not in corners:
           cornerAdaptedInput = cornerAdaptedInput + c
        if c == "S":
            postitionRobot[0] += 1
        elif c == "N":
            postitionRobot[0] -= 1
        elif c == "O":
            postitionRobot[1] += 1
        elif c == "W":
            postitionRobot[1] -= 1
        else:
            "ERROR. This should not happen."

def update_robot_position(dir):
    global postitionRobot
    global oldPostitionRobot
    oldPostitionRobot = list(postitionRobot)
    if dir == "S":
        postitionRobot[0] += 1
    elif dir == "N":
        postitionRobot[0] -= 1
    elif dir == "E":
        postitionRobot[1] += 1
    elif dir == "W":
        postitionRobot[1] -= 1
    else:
        "ERROR. This should not happen."

 

def getCommand(lastDirection, currentDirection):

    if(lastDirection==currentDirection):

        # robot going straight -> no turn needed
        return 'S'


    elif(lastDirection == "S" and currentDirection == "W" or lastDirection == "N" and currentDirection == "E" or lastDirection == "W" and currentDirection == "N" or lastDirection == "E" and currentDirection == "S" ):
        # robot turns right and continues straight
        # controllOut=controllOut + "1" + "0"
        # return controllOut
        return 'R'

    elif(lastDirection == "S" and currentDirection == "E" or lastDirection == "N" and currentDirection == "W" or lastDirection == "W" and currentDirection == "S" or lastDirection == "E" and currentDirection == "N" ):
        # robot turns left and continues straight
        # controllOut=controllOut+ "2" + "0"
        # return controllOut
        return 'L'

    elif(lastDirection == "S" and currentDirection == "N" or lastDirection == "N" and currentDirection == "S" or lastDirection == "W" and currentDirection == "E" or lastDirection == "E" and currentDirection == "W" ):
        # robot turns 180 degrees and continues straight
        # controllOut=controllOut + "3" + "0"
        # return controllOut
        return 'B'

    else:
        print("Debug: ", lastDirection, currentDirection)




#TODO: Initialize robot orientation , especially if first move is to turn around!!!



if __name__== "__main__":
    input_non_redundant = del_redundancy(input_planner)
    print("input_non_redundant", input_non_redundant)
    string_length = len(input_non_redundant)
    # input_planner = "SSWWSSSSWWNNNN"
    # output = "lrsls"
    i = 0
    lastChar = "" 
    sol = ''
    c = input_non_redundant[0]
    update_robot_position(c)
    trajet_final = ''
    if not c == orientationRobot:
        print('need to change robot orientation to ' + c )
    else:
        for i in range(1, len(input_non_redundant)):  # start at 1 cause we already managed frist case
            c = input_non_redundant[i]
            update_robot_position(c)
            print(postitionRobot)
            if postitionRobot in corners:
                output = ''
            elif postitionRobot in edges and oldPostitionRobot in edges + corners:
                print('in edge')
                print(oldPostitionRobot, corners + edges)
                output = getCommand(input_non_redundant[i-1],
                                    input_non_redundant[i])
                if output == 'S':
                    print('translating edge ouput to..', end='')
                    if postitionRobot[0] == 1:
                        output = 'R'
                    elif postitionRobot[0] == 3:
                        output = 'L'
                    elif postitionRobot[1] == 1:
                        output = 'R'
                    elif postitionRobot[1] == 3:
                        output = 'L'

            else:
                output = getCommand(input_non_redundant[i-1], c)

            print("output", output)
            sol += output
        trajet_final += sol

    print(trajet_final.replace('S', '0').replace('L', '2').replace('R','1').replace('B', '3'))
    

