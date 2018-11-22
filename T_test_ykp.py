# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 18:42:50 2018
Python 3.6.2 (Spyder)
@author: 308-11
"""

import os
import pandas as pd
import numpy as np
import copy
from scipy import stats
import datetime


def significance_level_mark( df, case ):
    """
    Input:
        df —— dataframe with only 1 row, 1 column['P_Value']
    """
    if case=="General":
        if df["P_Value"][0]>=0.05:
            df["Significance_Level"] = ["Not sigificant"]
            df["Star_Mark"] = [""]
        elif df["P_Value"][0]>=0.01:
            df["Significance_Level"] = ["95% confidence level"]
            df["Star_Mark"] = ["*"]
        elif df["P_Value"][0]>=0.001:
            df["Significance_Level"] = ["99% confidence level"]
            df["Star_Mark"] = ["**"]
        else:
            df["Significance_Level"] = ["99.9% confidence level"]
            df["Star_Mark"] = ["***"]
    elif case=="Economy":
        if df["P_Value"][0]>=0.10:
            df["Significance_Level"] = ["Not sigificant"]
            df["Star_Mark"] = [""]
        elif df["P_Value"][0]>=0.05:
            df["Significance_Level"] = ["90% confidence level"]
            df["Star_Mark"] = ["*"]
        elif df["P_Value"][0]>=0.01:
            df["Significance_Level"] = ["95% confidence level"]
            df["Star_Mark"] = ["**"]
        else:
            df["Significance_Level"] = ["99% confidence level"]
            df["Star_Mark"] = ["***"]
    else:
        print("Error: No such case!\n")
    return df
        

def significance_ykp( X, case ):
    columns_list = X.columns.tolist()
    level_list = list(set(X[columns_list[0]]))
    level_num_label_dict = { str(level_list[j]):j+1 for j in list(range( len(level_list) )) }
    X["Category2Num"] = X.apply(lambda x: level_num_label_dict[x[0]] , axis=1)
    """ OneSample T-test """
    single_t_test_mean = np.mean( X.iloc[:,1] )
    single_t_test_out = pd.DataFrame()
    for i in level_list:
        # print(i)
        temp_df = pd.DataFrame()
        locals()["X_%s" %(i)] = copy.deepcopy( X[X.iloc[:,0]==i].iloc[:,1] )
        rvs  = copy.deepcopy( locals()["X_%s" %(i)] )
        locals()["Single_test_%s" %(i)] = stats.ttest_1samp(rvs, single_t_test_mean)
        temp_df[str(columns_list[0])] = [ str(i) ]
        temp_df["Count"] = [ len(rvs) ]
        temp_df["Value_Mean"] = [ float("%.4f" % np.mean(rvs)) ]
        temp_df["Test_Mean"] = [ float("%.4f" % single_t_test_mean) ]
        temp_df["T_test_Value"] = [ float("%.4f" % locals()["Single_test_%s" %(i)][0]) ]
        temp_df["P_Value"] = [ float("%.6f" % np.float( locals()["Single_test_%s" %(i)][1])) ]
        temp_df = copy.deepcopy(significance_level_mark( temp_df, case ))
        single_t_test_out = pd.concat([single_t_test_out,temp_df],ignore_index=False)
    
    """ Independent Sample T test """
    individual_t_test_mean = np.mean( X.iloc[:,1] )
    individual_t_test_out = pd.DataFrame()
    for j in range(len(level_list)):
        # print(j)
        for k in range(j+1,len(level_list)):
            # print(j,k)
            temp_df = pd.DataFrame()
            locals()["individual_t_test_%s_%s" %(j,k)] = copy.deepcopy( stats.ttest_ind( locals()["X_%s" %(level_list[j])], locals()["X_%s" %(level_list[k])] ) )            
            locals()["X_%s" %(i)] = copy.deepcopy( X[X.iloc[:,0]==i].iloc[:,1] )
            rvs  = copy.deepcopy( locals()["X_%s" %(i)] )
            locals()["Single_test_%s" %(i)] = stats.ttest_1samp(rvs, single_t_test_mean)
            
            temp_df[str(columns_list[0])] = [ str(level_list[j])+' & '+str(level_list[k]) ]
            temp_df["Count(Left)"] = [ len(locals()["X_%s" %(level_list[j])]) ]
            temp_df["Value_Mean(Left)"] = [ float("%.4f" % np.mean(locals()["X_%s" %(level_list[j])])) ]
            temp_df["Count(Right)"] = [ len(locals()["X_%s" %(level_list[k])]) ]
            temp_df["Value_Mean(Right)"] = [ float("%.4f" % np.mean(locals()["X_%s" %(level_list[k])])) ]
            temp_df["Test_mean_difference"] = [ float("%.4f" % (np.mean(locals()["X_%s" %(level_list[j])]) - np.mean(locals()["X_%s" %(level_list[k])]))) ]
            temp_df["T_test_Value"] = [ float("%.4f" % locals()["individual_t_test_%s_%s" %(j,k)][0]) ]
            temp_df["P_Value"] = [ float("%.6f" % np.float( locals()["individual_t_test_%s_%s" %(j,k)][1])) ]
            temp_df = copy.deepcopy(significance_level_mark( temp_df, case ))
            individual_t_test_out = pd.concat([individual_t_test_out,temp_df],ignore_index=False)
    individual_t_test_out.index = list(individual_t_test_out[str(columns_list[0])])
    individual_t_test_out_matrix = pd.DataFrame()
    for i in level_list:
        individual_t_test_out_matrix[i] = [0 for i in level_list ]
    individual_t_test_out_matrix.index = level_list
    for j in range(len(level_list)):
        # print(j)
        for k in range(j+1,len(level_list)):
            # print(j,k)
            temp_1 = copy.deepcopy( np.mean(locals()['X_%s' %(level_list[j])]) - np.mean(locals()['X_%s' %(level_list[k])]) )
            temp_2 = copy.deepcopy( individual_t_test_out.loc[str(level_list[j])+' & '+str(level_list[k]),'Star_Mark'] )
            temp_3 = copy.deepcopy( individual_t_test_out.loc[str(level_list[j])+' & '+str(level_list[k]),'T_test_Value'] )
            individual_t_test_out_matrix.loc[level_list[j],level_list[k]] = str(float('%.2f' % temp_1))+str(temp_2)+'('+str(float('%.2f' % temp_3))+')'
    return single_t_test_out,individual_t_test_out,individual_t_test_out_matrix


def creat_filefolds_ykp():
    # creat output file-folders in .py file
    """
    Input variables: ()
    To use this function, coding:
        code_path, path_level_1 = creat_filefolds_ykp()
    """
    Today_YMDH = datetime.datetime.now().strftime('%Y_%m_%d_%H')  # record Y-M-D-H
    Today_Minu = datetime.datetime.now().strftime('%M')  # record Minute
    Today_YMDHM = Today_YMDH+'_'+Today_Minu
    code_path = os.getcwd()+'\\'
    folder = os.getcwd() + '\\'+str(Today_YMDHM)+'_output\\'  # creat output null-file
    # Creat new null-files under last-level creat null-file
    if not os.path.exists(folder):
        os.makedirs(folder)
        path_level_1 = folder
    else:
        folder_new = folder[:-1]+'_new\\'
        os.makedirs(folder_new)
        path_level_1 = folder_new
    '''
    Output variables:
        code_path           —— path with .py code
        path_level_1        —— level-1 path under code_path
    '''
    return code_path, path_level_1


if __name__ == "__main__":
    path, path_level_1 = creat_filefolds_ykp()
    X = pd.read_excel( path+'Data_input.xlsx' )
    # Calaulate
    single_t_test_out,individual_t_test_out,individual_t_test_out_matrix = significance_ykp( X, "Economy" )
    # Out to Excel
    nowTime1 = datetime.datetime.now().strftime('%Y.%m.%d.%H')  # record Y-M-D-H
    nowTime2 = datetime.datetime.now().strftime('%M')  # record Y-M-D-H
    save_name = nowTime1+'：'+nowTime2+'.T_test_output.xlsx'
    writer = pd.ExcelWriter(path_level_1+save_name)
    single_t_test_out.to_excel(excel_writer=writer, sheet_name = '(1)OneSample_T-test', index=None)
    individual_t_test_out.to_excel(excel_writer=writer, sheet_name = '(2)Independent_T-test', index=None)
    individual_t_test_out_matrix.to_excel(excel_writer=writer, sheet_name = '(3)Sig_Matrix', index=True)
    writer.save()
    writer.close()