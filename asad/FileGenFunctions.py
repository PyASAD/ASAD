#Function to calculate the new columns derived from the input file.
from __future__ import division
import os.path
import re
import sys

##input_path = '../data/models/'
##output_path = '../data/models/'

#####FUNCTIONS#####

#Creates the Main output file.
def calculateFirstColumns(input_path,column,inputAge,output_path,choice=0,printer=0,random_number=0,headers=[6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,8.0,8.1,8.2,8.3,8.4,8.5,8.6,8.7,8.8,8.9,9.0,9.1,9.2,9.3,9.4,9.5]):
    if choice == 0 or choice == 1:#Choice|----------------------------------------------------
        inputFiles = []
        inputFiles.append(open(input_path, 'r'))
        for inputFile in inputFiles:
            listElements = inputFile.readlines()
            outputFileName = os.path.basename(inputFile.name)
            outputFileName = outputFileName[:-4] + '_msp_' + str(inputAge) + '.txt' #+ '_' + "id" + str(random_number) +  '.txt'
            outputFile = open(os.path.join(output_path,outputFileName), 'w')
            outputFile.write('# ')       #Creating the Main File Header
            #print(headers)
            #print('\n')
            the_list = []
            for f in headers:
                the_list.append(float(float(f)*10))
            #print(the_list)
            for index in the_list:
            #for index in range(68, 96):
                z = 0
                if index != inputAge:
                    for k in range(1, 101):
                        outputFile.write("{}, ".format(float(index + z)))
                        z += 0.001
            outputFile.write(str(inputAge) + '\n')

            if printer == 0:
                print("\nGenerating File: " + outputFileName + ". Please wait...")
            else:
                pass

            if listElements[0].split()[0][0] == '#':    #Checking if File contains a header
                listElements = listElements[1:]
            for x in listElements:
                outputFile.write("{} ".format(x.split()[0]))
                for j in range(1,len(headers)+2):
                    for i in range(0,100):
                        if column-1 != j and j < len(x.split()):
                            #Makes sure the equation is not done on the column chosen by the user. #Also makes sure the index is within the range.
                            try:
                                calcNumber = (float(x.split()[column-1])*(i/100)) + ( (1-(i/100))*(float(x.split()[j])) )
                                outputFile.write("{0:.8f} ".format(calcNumber))
                            except IndexError:
                                print('\n\n\n\n\n\n\n')
                                print('inputAge ---> ' + str(inputAge))
                                #print(listElements)
                                print('\n')
                                print(x)
                                print('\n')
                                print(x.split())
                                print('\n')
                                print('column ---> ' + str(column))
                                print('column - 1 ---> ' + str(column-1))
                                print('j ---> ' + str(j))
                                print('j - 1 ---> ' + str(j-1))
                                print('i ---> ' + str(i))
                                print('i - 1 ---> ' + str(i-1))
                                print('len( x.split() ) ---> ' + str(len(x.split())))
                                print('\n\n\n\n\n\n\n')
                                sys.exit(15)
                                #print('\n\n\t!\t!\t!\n\n')
                                #pass
                if x is listElements[-1]:
                    pass
                else:
                    outputFile.write("\n")
        outputFile.close()
        inputFile.close()
        return os.path.abspath(outputFile.name) , outputFileName


#Creates the Fine Tuned File.
def calculateColumns(inputFile, startRange, endRange, columnNumber, columnNumber2, pasteFileName):
    listElements = inputFile.readlines()
    outputFile = open(os.path.join(output_path,pasteFileName), 'w')
    startIndex = int(startRange * 1000)
    endIndex = int(endRange * 1000) + 1  #Exclusive
    print("\nGenerating...")
    for x in listElements:
        outputFile.write("{} ".format(x.split(' ')[0]))
        for i in range(startIndex, endIndex):
            calcNumber = (float(x.split()[columnNumber-1])*(i/1000)) + ((1-(i/1000))*float(x.split()[columnNumber2-1]))
            outputFile.write("{0:.8f} ".format(calcNumber))
        outputFile.write('\n')
    outputFile.close()

#Getting the name of the file.
def getInputFile(input_path):

    indir = input_path
    inputFiles = []
    while True:
##        print("To choose all the input files starting with a specific number type:\nYour number followed by a star (Example: 4*)")
##        fileName = str(raw_input("Enter the input file name: "))
##        if fileName[-1] == '*':
##            for root, dirs, filenames in os.walk(indir):
##                for f in filenames:
##                    if f[0] == fileName[0]:
##                        try:
##                            inputFiles.append(open(os.path.join(root, f), 'r'))
##                            print("\nFile: " + f + " opened successfully!\n")
##                        except Exception as e:
##                            print("Error! ----- There are no files that start with " + fileName[0] + " in the directory!")
##            break
##        elif not fileName.endswith('.txt'[:]):
##            fileName = fileName + '.txt'
        try:
            inputFiles.append(open(input_path,'r'))
            print("\nFile: "+inputFiles[0].__name__ + " opened successfully!\n")
            break
        except Exception as e:
            print(e)
    if len(inputFiles) == 0:
        return False
    else:
        return inputFiles


#Getting one column number.
def getColumn(inputAge=0.0,choice=0,headers=[6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,8.0,8.1,8.2,8.3,8.4,8.5,8.6,8.7,8.8,8.9,9.0,9.1,9.2,9.3,9.4,9.5]):
    if choice == 0:
        inputAge = float(raw_input("For multiple stellar population, enter the Age ("+ str(headers[0]) +' - ' + str(headers[-1]) + '): ') )

        while inputAge < headers[0] or inputAge > headers[-1]:

            print("\nError! ----- Age is out of range!\n")

            inputAge = float(raw_input("Enter the Age ("+ str(headers[0]) +' - ' + str(headers[-1]) + '): '))

        inputAge = inputAge * 10

        column = 2

        the_list = []
        for f in headers:
            the_list.append(float(f)*10)
        #print(the_list)
        for i in the_list:

            if i == inputAge:

                return column, inputAge

            column += 1
    elif choice == 1:
        inputAge = inputAge * 10

        column = 2

        the_list = []
        for f in headers:
            the_list.append(float(f)*10)
        #print(the_list)
        for i in the_list:

            if i == inputAge:

                return column, inputAge

            column += 1

##    column = int(raw_input("Enter the column number: "))
##    while column < 2 or column > 16:
##        print("\nError! ----- Number out of range!\n")
##        column = int(raw_input("Enter the column number: "))
##    return column


#Getting two column numbers.
def getColumnNumbers():
    columnNumber, columnNumber2 = int(raw_input("Enter the first column number (2-16): ")), int(raw_input("Enter the second column number (2-16): "))
    while columnNumber < 2 or columnNumber > 16 or columnNumber2 < 2 or columnNumber2 > 16:
        print("\nError! ----- Number out of range.\n")
        columnNumber, columnNumber2 = int(raw_input("Enter the first column number (2-16): ")), int(raw_input("Enter the second column number (2-16): "))
    return columnNumber, columnNumber2

#Getting the range.
def getRange():
    startRange, endRange = float(raw_input("Start of range: ")), float(raw_input("End of range: "))
    while startRange < 0 or startRange > endRange or endRange < 0:
        print("\nError! ----- Invalid ranges entered.\n")
        startRange, endRange = float(raw_input("Start of range: ")), float(raw_input("End of range: "))
    return startRange, endRange

#Getting the name of the PasteFile.
def getOutputFileName():
    pasteFileName = str(raw_input("Enter the name of the Output File: "))
    if not pasteFileName.endswith('.txt'[:]):
        pasteFileName = pasteFileName + '.txt'

    #calculateColumns(inputFile, startRange, endRange, columnNumber, columnNumber2, pasteFileName)
    return pasteFileName








