def chi_square_minimization(directory,temp_directory='',observ=''):
    from interactive import ok_print
    import csv
    import os
    import pandas as pd
    import random
    random_number = random.randint(1,99999)
    print ""
    print "Applying Chi-Square Minimization on " + str(observ) + " ---> "
    print ""
    def cleaner(list,directory):
        for file in list:
            if os.name == 'nt':
                file = directory + "\\" + file
            else:
                file = directory + "/" + file
            if file.find(".csv") != -1:
                os.remove(file)
    #function to calculate chi square value for each file
    def mini(lista):
        min = lista[0]
        for element in lista:
            if element < min:
                min = element
            else:
                pass
        return min
    def chi_square(file, flag):
        sum_of_squares =[]
        #index =[]
        data = pd.read_csv(file, skiprows=1, header= None) #skipping first 2 rows
        col1= data.iloc[:,1]
        for x in range(3, data.shape[1]):
            col2= data.iloc[:,x]
            squares = (col1-col2) ** 2
            sum_of_squares.append(squares.sum())
            #index.append(x)

        minimum = mini(sum_of_squares)
        if flag == True:
            index_of_min = [i for i, x in enumerate(sum_of_squares) if x == minimum]
            return ([x+3 for x in index_of_min], minimum)   #+3 because range starts from 3rd column, and considering case where 2 columns give same minimum
            #min_col_index = index[index_of_min[0]]
            #col22= data.iloc[:,min_col_index]
            #squares22 = (col1-col22) ** 2
            #sum22 = squares22.sum()
            #return (index_of_min, index[index_of_min[0]], sum22, minimum)
        else:
            return (minimum)
    #function to find the header for the columns that provide minimum chi square value
    def header(n, col):
        d= pd.read_csv(n)
        s = float(d.iloc[:0, col-1].name.replace(',', ''))
        return s
    directoryy = ""
    if os.name == 'nt':
        directoryy = temp_directory + '\\' +'chi_sq_output_of_' + str(observ) + str(random_number) + '.txt'
    elif os.name != 'nt':
        directoryy = temp_directory + '/' +'chi_sq_output_of_' + str(observ) + str(random_number) + '.txt'
    with open(directoryy,'w+') as f:
        file_names=[]
        chi_sq_values = []
        i=0
        list = os.listdir(directory)
        minim_list = list
        #print list
        #print list
        for file in list:
            if (file.find("msp") == -1):
                list.remove(file)
        for file in list:
            if os.name == 'nt':
                filename = directory + "\\" + file
            else:
                filename = directory + "/" + file
            if filename[-4:] == ".txt":
                name = filename[:filename.rfind(".txt")]
                file_names.append(name + ".txt")
                newfile = "%s.csv" %name
                with open(filename) as fin, open(newfile, 'w+') as fout:
                    o=csv.writer(fout)
                    for line in fin:
                        o.writerow(line.split())
                    #print("Done", i)
                    ch = chi_square(newfile, False)
                    if os.name == 'nt':
                        print str(i+1) + ") Chi square minimization of " + str(filename[filename.rfind("\\")+1:]) + " is: " + str(ch)
                        f.write(str(i+1) + ") Chi square minimization of " + str(filename[filename.rfind("\\")+1:]) + " is: " + str(ch))
                    else:
                        print str(i+1) + ") Chi square minimization of " + str(filename[filename.rfind("/")+1:]) + " is: " + str(ch)
                        f.write(str(i+1) + ") Chi square minimization of " + str(filename[filename.rfind("\\")+1:]) + " is: " + str(ch))
                    print ""
                    f.write("\n")
                    chi_sq_values.append(ch)
                i= i+1
        #print len(chi_sq_values)
        chi_all_files= mini(chi_sq_values)
        print ""
        f.write("\n")
        print("Chi square minimization of all files: " + str(chi_all_files))
        f.write("Chi square minimization of all files: " + str(chi_all_files))
        print ""
        f.write("\n")
        index_of_min = [i for i, x in enumerate(chi_sq_values) if x == chi_all_files] #case where 2 files give the same minimum
        list = os.listdir(directory)
        result_ = []
        empty_string = ""
        for x in index_of_min:
            #print(file_names[x], "has the minimum chi square value of ", chi_all_files)

            n= file_names[x][:file_names[x].rfind(".txt")] + ".csv"  #file names with minimum chi value

            col, minim = chi_square(n, True) #finding the column which gave minimum chi value

            for y in col:                    #for each column that has a min in that file (in case there are more than 1 cols with same min)

                head = header(n, y)        #finding header for that column
                print ""
                f.write("\n")
                if os.name == 'nt':
                    empty_string = file_names[x][file_names[x].rfind("\\")+1:]
                else:
                    empty_string = file_names[x][file_names[x].rfind("/")+1:]
                try:
                    ok_print(empty_string + " has a minimum chi square value " + str(minim) + " and it is from column " + str(y) + " which has a header of " +  str(head))
                    f.write(empty_string + " has a minimum chi square value " + str(minim) + " and it is from column " + str(y) + " which has a header of " +  str(head))
                except Exception:
                    ok_print(empty_string + " has a minimum chi square value " + str(minim) + " and it is from column " + str(y) + " which has a header of " +  str(head))
                    f.write(empty_string + " has a minimum chi square value " + str(minim) + " and it is from column " + str(y) + " which has a header of " +  str(head))
                result_.append(file_names[x])

            #l, col, summ, minim = chi_square(n, True)
        print ""
        f.write("\n")
        #list = os.listdir(directory)
        cleaner(list,directory)
        #cleaner(minim_list,directory)
        #print result_
        f.close()
        return result_
            #print(l, col, summ, minim)
#dir = "C:\\Users\\hicha\\Desktop\\Error_Sample_Data\\1"
#chi_square_minimization(dir,"C:\\Users\\hicha\\Desktop\\Error_Sample_Data")
    #print "\n\n"
    #print res
