def main_plotter(fileofwork , format , title , output ,headers=[6.8,6.9,7.0,7.1,7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,8.0,8.1,8.2,8.3,8.4,8.5,8.6,8.7,8.8,8.9,9.0,9.1,9.2,9.3,9.4,9.5]):
    #np.loadtxt('balmer_air.txt',unpack=True,usecols=[0])
    #print(len(headers))
    import numpy as np
    from pandas import DataFrame
    import matplotlib.pyplot  as plt
    import matplotlib         as mpl
    import itertools
    import matplotlib.cm      as cm
    import matplotlib.markers as markers
    import os.path, re, sys
    import random
    from itertools import cycle

    def chunks(l, n):
        return [l[i:i+n] for i in range(0, len(l), n)]

    def findgen(start,stop,step):
    	size=int((stop-start)/step)+1
    	arr=np.zeros(size)
    	arr[0]=start
    	for i in range(1,size):
    		arr[i]=arr[i-1]+step
    	return arr

    def file_row(fileofwork):
        with open(fileofwork) as f:
            for i , l in enumerate(f):
                pass
            f.close()
        return i

    def first_row_catcher(fileofwork):
        with open(fileofwork,'r') as f:
            ages_list = []
            file_lines = [f.readlines()]
            first_one = file_lines[0][0]
            ndxx = first_one.find(', ')

            #print ages_list
            lenn = 0
            for i in range(ndxx,len(file_lines[0][0])+2):
                if first_one.find(', ' , i) != -1:
                    lenn += 1
            lenn += 1
            #print lenn
            ttemp = []
            for i in range(0,lenn):
                #print i
                ttemp.append(first_one[ ndxx + 2 :first_one.find(',  ' , ndxx + 1) ])
                ndxx = first_one.find(', ' , ndxx + i )

            temp_string = ttemp[0].split(', ')

            [temp_string[0].split(',') for ele in xrange(0,lenn)]

            ages_list.append(first_one[first_one.rfind('#')+2:ndxx])

            #print(ages_list[1][:ages_list[1].find(', ')])
            for t in temp_string:
                ages_list.append(t)

            final_ages_list = []
            final_ages_list.append(0.0)
            var = float(ages_list[0][:ages_list[0].find(',')])
            ages_list.remove(ages_list[0])
            [float(i) for i in ages_list]
            for j in ages_list:
                final_ages_list.append(j)
            final_ages_list[0] = float(var)
            [float(j) for j in final_ages_list]
            #print final_ages_list
            #print ages_list[0]
            rows_num = file_row(fileofwork)
            f.close()
        #z = 0.0
        usage_list = []

        columns_num = 0
        for i in range(1,len(final_ages_list)):
            usage_list.append(len(final_ages_list[i]))
        for i in range(0,len(usage_list)):
            if usage_list[i] == 6 or usage_list == 5 or usage_list == 4:
                columns_num += 1
        return final_ages_list , columns_num , rows_num

    n1 = headers[0]*10
    n2 = (headers[-1]*10) + 1
    #print('n1--->' + str(n1))
    #print('n2--->' + str(n2))
    temp=np.arange(n1,n2)
    q_a = 0
    no_age = 0
    data=np.loadtxt(fileofwork,unpack=True)

    ages_list , columns_num , rows_num  = first_row_catcher(fileofwork)
    #print columns_num
    #print rows_num
    last_age = float(ages_list[-1])

    flux_observed= data[0:][1]
    flux_model=data[0:][3:]
    last=[94]
    mm=flux_model.transpose()
    x_axis=[i for i in np.arange(0.0,0.1,0.001)]
    temp_test= [x for x in temp if x !=int(last_age)]
    temp_test.append(int(last_age))
    chi=np.zeros((len(data[0]),len(data)-3))

    for i in range(0,len(flux_observed)):
    	for j in range(3,len(data)):
    		flux_e=data[0:][j]
    		chi[i,j-3]=((flux_observed[i]-flux_e[i])**2)
    sum_matrix= np.sum(chi, axis=0)
    final_matrix= np.full((len(headers),100),0,dtype=float)
    #new= np.full((28,100),None,dtype=float)

    #new= sum_matrix[~np.isnan(sum_matrix)]
    f=0
    for i in range(0,len(headers)):
        for j in range(0,100):
            #print('i---> ' + str(i))
            #print('j---> ' + str(j))
            try:
                final_matrix[i][j]=sum_matrix[f]
                f+=1
                if (f==2701):
                    break
            except:
                pass

    new=np.ma.masked_equal(final_matrix,0)
    mini=1.0/sum_matrix.min()
    di=1.0/new
    for i in range(0,len(headers)):
        for j in range(0,100):
            if di[i][j] == mini:
                no_age = i
                q_a= j
    #print q_a
    """print no_age, q_a
    print di[no_age, q_a]
    print ('x: ',x_axis[q_a], '  ', 'Y: ',temp_test[no_age])
    print ('age is: ', temp_test[no_age])
    print ('-----------------------------------------')
    print ('minimum chi_squared is: ',sum_matrix.min())
    print ('-----------------------------------------')
    print ('1.0/minimum chi_squared is: ',mini)
    print ('-----------------------------------------')"""


    np.savetxt("chi_sum_squared.txt",new)
    #np.savetxt("chi_squared.txt",chi)
    np.savetxt("1.0_di_minimum chi_squared.txt",di)

    #-----------------------------------------
    options = {
        'xtick.labelsize'         : 28,
        'ytick.labelsize'         : 28,
        'xtick.major.size'        : 20,
        'xtick.major.width'       : 1,
        'xtick.minor.size'        : 10,
        'xtick.minor.width'       : 0.5,
        'ytick.major.size'        : 20,
        'ytick.major.width'       : 1,
        'ytick.minor.size'        : 10,
        'ytick.minor.width'       : 0.5,
        'figure.max_open_warning' : 100
    }

    font = {
        'fontname' : 'Sans',
        'fontsize' : 36
    }

    small_font = {
        'fontname' : 'Sans',
        'fontsize' : 28
    }

    mpl.rcParams = dict(mpl.rcParams, **options)
    levels=15
    NL = levels
    y  = temp_test #ages 28
    x  = x_axis #100
    z  = di


    fig = plt.figure(figsize=(20,14))
    border_width = 0.10
    border_height = 0.09
    ax_size = [0.10, 0.15, 0.90, 0.75]
    ax = fig.add_axes(ax_size)

    C  = plt.contour(x, y,z, NL, colors=['k'], linewidths=0.10, zorder=2)
    #plt.clabel(C, inline=1, linewidths=0.10, **small_font)
    CF = plt.contourf(x, y, z, NL, alpha=0.85, cmap=cm.jet, zorder=1)
    CF.cmap.set_under('k')
    CF.cmap.set_over('w')
    cb = fig.colorbar(CF)
    cb.ax.tick_params(labelsize=26)
    plt.scatter([x_axis[q_a]], [temp_test[no_age]], c='w',s=350, marker="*", zorder=3)

    plt.xlim(min(x_axis), max(x_axis))
    plt.ylim( min(temp_test), max(temp_test))

    plt.tick_params(labelsize=26)
    plt.minorticks_on()
    plt.grid(which='both')

    plt.xlabel("fx")
    plt.ylabel("log(Age/Year)")
    #plt.show()

    #print("\nSaving the plot as " + format + ' ...\n')
    full_path = ''
    fformat = '.' + format
    if os.name == 'nt':
        da_file = fileofwork[fileofwork.rfind('\\')+1:fileofwork.rfind('.')]
        ndx1 = da_file[da_file.rfind("-") + 1:]
        #print("ndx1:      " + ndx1)
        ndx2 = ndx1[ndx1.find("_")+1:]
        #print("ndx2:      " + ndx2)
        """ndx3 = ndx2[ndx2.find("_")+1:]"""
        print("\nSaving " + ndx2 + " as " + format + ' ...\n')
        full_path = output + '\\' + 'surface_' + ndx2 + fformat
    else:
        da_file = fileofwork[fileofwork.rfind('/')+1:fileofwork.rfind('.')]
        ndx1 = da_file[da_file.rfind("-") + 1:]
        #print("ndx1:      " + ndx1)
        ndx2 = ndx1[ndx1.find("_")+1:]
        #print("ndx2:      " + ndx2)
        """ndx3 = ndx2[ndx2.find("_")+1:]"""
        print("\nSaving " + ndx2 + " as " + format + ' ...\n')
        full_path = output + '/' + 'surface_' + ndx2 + fformat
    plt.savefig( full_path , bbox_inches='tight')
    #plt.show()
    return ('surface_' + ndx2 + fformat)
#[6.8,6.9,7.0,7.1,7.2,7.3,
#fileofwork = raw_input("\t\tENTER----->   ")
#main_plotter(fileofwork ,'pdf',None,"C:\\Users\\hicha\\Desktop")
