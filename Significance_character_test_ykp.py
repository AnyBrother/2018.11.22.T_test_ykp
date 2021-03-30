# -*- coding: utf-8 -*-
"""
@Date     : 2020-09-14 14:46
@author  : ykp
@Version: significant test for credit characters among different types.
"""
import pandas as pd
import numpy as np
import os
import copy
import datetime
from scipy import stats
from statsmodels.sandbox.stats.runs import runstest_2samp


# 显著性检验星号标注 Significant Star mark
def significance_level_mark(df, subject):
    """
    Input:
        df —— DataFrame with only 1 row, 1 column['P_Value']
        subject—— "General" or "Economy"
    """
    if subject == "General":
        if df["P_Value"][0] >= 0.05:
            df["Significance_Level"] = ["Not significant"]
            df["Star_Mark"] = [""]
        elif df["P_Value"][0] >= 0.01:
            df["Significance_Level"] = ["95% confidence level"]
            df["Star_Mark"] = ["*"]
        elif df["P_Value"][0] >= 0.001:
            df["Significance_Level"] = ["99% confidence level"]
            df["Star_Mark"] = ["**"]
        else:
            df["Significance_Level"] = ["99.9% confidence level"]
            df["Star_Mark"] = ["***"]
    elif subject == "Economy":
        if df["P_Value"][0] >= 0.10:
            df["Significance_Level"] = ["Not significant"]
            df["Star_Mark"] = [""]
        elif df["P_Value"][0] >= 0.05:
            df["Significance_Level"] = ["90% confidence level"]
            df["Star_Mark"] = ["*"]
        elif df["P_Value"][0] >= 0.01:
            df["Significance_Level"] = ["95% confidence level"]
            df["Star_Mark"] = ["**"]
        else:
            df["Significance_Level"] = ["99% confidence level"]
            df["Star_Mark"] = ["***"]
    else:
        print("Error: No such subject!\n")
    return df


def significance_ykp(X, subject):
    columns_list = X.columns.tolist()
    level_list = list(set(X[columns_list[0]]))
    level_num_label_dict = {str(level_list[j]): j + 1 for j in list(range(len(level_list)))}
    X["Category2Num"] = X.apply(lambda x: level_num_label_dict[x[0]], axis=1)
    """ OneSample T-test """
    single_t_test_mean = np.mean(X.iloc[:, 1])
    single_t_test_max = np.max(X.iloc[:, 1])
    single_t_test_min = np.min(X.iloc[:, 1])
    single_t_test_std = np.std(X.iloc[:, 1])
    single_t_test_median = np.median(X.iloc[:, 1])
    single_t_test_out = pd.DataFrame()
    for i in level_list:
        # print(i)
        temp_df = pd.DataFrame()
        locals()["X_%s" % i] = copy.deepcopy(X[X.iloc[:, 0] == i].iloc[:, 1])
        rvs = copy.deepcopy(locals()["X_%s" % i])
        locals()["Single_test_%s" % i] = stats.ttest_1samp(rvs, single_t_test_mean)
        temp_df[str(columns_list[0])] = [str(i)]
        temp_df["Count"] = [len(rvs)]
        temp_df["Value_Mean"] = [float("%.4f" % np.mean(rvs))]
        temp_df["Test_Mean"] = [float("%.4f" % single_t_test_mean)]
        temp_df["Test_Max"] = [float("%.4f" % single_t_test_max)]
        temp_df["Test_Min"] = [float("%.4f" % single_t_test_min)]
        temp_df["Test_Std"] = [float("%.4f" % single_t_test_std)]
        temp_df["Test_Median"] = [float("%.4f" % single_t_test_median)]
        temp_df["T_test_Value"] = [float("%.4f" % locals()["Single_test_%s" % i][0])]
        temp_df["P_Value"] = [float("%.6f" % np.float(locals()["Single_test_%s" % i][1]))]
        temp_df = copy.deepcopy(significance_level_mark(temp_df, subject))
        single_t_test_out = pd.concat([single_t_test_out, temp_df], ignore_index=False)
    """ Independent Sample T test """
    individual_t_test_mean = np.mean(X.iloc[:, 1])
    individual_t_test_out = pd.DataFrame()
    for j in range(len(level_list)):
        # print(j)
        for k in range(j + 1, len(level_list)):
            # print(j,k)
            temp_df = pd.DataFrame()
            locals()["individual_t_test_%s_%s" % (j, k)] = copy.deepcopy(
                stats.ttest_ind(locals()["X_%s" % (level_list[j])], locals()["X_%s" % (level_list[k])]))
            locals()["X_%s" % j] = copy.deepcopy(X[X.iloc[:, 0] == j].iloc[:, 1])
            rvs = copy.deepcopy(locals()["X_%s" % j])
            locals()["Single_test_%s" % j] = stats.ttest_1samp(rvs, single_t_test_mean)
            # 保存结果
            temp_df[str(columns_list[0])] = [str(level_list[j]) + ' & ' + str(level_list[k])]
            temp_df["Count(Left)"] = [len(locals()["X_%s" % (level_list[j])])]
            temp_df["Value_Mean(Left)"] = [float("%.4f" % np.mean(locals()["X_%s" % (level_list[j])]))]
            temp_df["Count(Right)"] = [len(locals()["X_%s" % (level_list[k])])]
            temp_df["Value_Mean(Right)"] = [float("%.4f" % np.mean(locals()["X_%s" % (level_list[k])]))]
            temp_df["Test_mean_difference"] = [float(
                "%.4f" % (np.mean(locals()["X_%s" % (level_list[j])]) - np.mean(locals()["X_%s" % (level_list[k])])))]
            temp_df["T_test_Value"] = [float("%.4f" % locals()["individual_t_test_%s_%s" % (j, k)][0])]
            temp_df["P_Value"] = [float("%.6f" % np.float(locals()["individual_t_test_%s_%s" % (j, k)][1]))]
            temp_df = copy.deepcopy(significance_level_mark(temp_df, subject))
            individual_t_test_out = pd.concat([individual_t_test_out, temp_df], ignore_index=False)
    individual_t_test_out.index = list(individual_t_test_out[str(columns_list[0])])
    individual_t_test_out_matrix = pd.DataFrame()
    for i in level_list:
        individual_t_test_out_matrix[i] = [0 for i in level_list]
    individual_t_test_out_matrix.index = level_list
    for j in range(len(level_list)):
        # print(j)
        for k in range(j + 1, len(level_list)):
            # print(j,k)
            temp_1 = copy.deepcopy(
                np.mean(locals()['X_%s' % (level_list[j])]) - np.mean(locals()['X_%s' % (level_list[k])]))
            temp_2 = copy.deepcopy(
                individual_t_test_out.loc[str(level_list[j]) + ' & ' + str(level_list[k]), 'Star_Mark'])
            temp_3 = copy.deepcopy(
                individual_t_test_out.loc[str(level_list[j]) + ' & ' + str(level_list[k]), 'T_test_Value'])
            individual_t_test_out_matrix.loc[level_list[j], level_list[k]] = str(float('%.2f' % temp_1)) + str(
                temp_2) + '(' + str(float('%.2f' % temp_3)) + ')'
    """ Mann-Whitney_U_检验 """
    individual_MHU_test_out = pd.DataFrame()
    for j in range(len(level_list)):
        # print(j)
        locals()['X_%s' % (level_list[j])] = copy.deepcopy(X[X.iloc[:, 0] == level_list[j]].iloc[:, 1])
    for j in range(len(level_list)):
        # print(j)
        for k in range(j + 1, len(level_list)):
            # print(j, k)
            # print(str(level_list[j]) + ' 与 ' + str(level_list[k]))
            temp_df = pd.DataFrame()
            locals()['individual_MHU_test_%s_%s' % (j, k)] = copy.deepcopy(
                stats.mannwhitneyu(locals()['X_%s' % (level_list[j])], locals()['X_%s' % (level_list[k])]))
            temp_df[str(columns_list[0])] = [str(level_list[j]) + ' 与 ' + str(level_list[k])]
            temp_df['企业数量(左)'] = [len(locals()['X_%s' % (level_list[j])])]
            temp_df['信用得分均值(左)'] = [float('%.4f' % np.mean(locals()['X_%s' % (level_list[j])]))]
            temp_df['企业数量(右)'] = [len(locals()['X_%s' % (level_list[k])])]
            temp_df['信用得分均值(右)'] = [float('%.4f' % np.mean(locals()['X_%s' % (level_list[k])]))]
            temp_df['检验的均值差值'] = [float(
                '%.4f' % (np.mean(locals()['X_%s' % (level_list[j])]) - np.mean(locals()['X_%s' % (level_list[k])])))]
            temp_df['MHU统计量值'] = [float('%.4f' % locals()['individual_MHU_test_%s_%s' % (j, k)][0])]
            temp_df['P_Value'] = [float('%.6f' % np.float(locals()['individual_MHU_test_%s_%s' % (j, k)][1]))]
            temp_df = copy.deepcopy(significance_level_mark(temp_df, subject))
            individual_MHU_test_out = pd.concat([individual_MHU_test_out, temp_df], ignore_index=False)
        individual_MHU_test_out.index = list(individual_MHU_test_out[str(columns_list[0])])
    individual_MHU_test_out_matrix = pd.DataFrame()
    for i in level_list:
        individual_MHU_test_out_matrix[i] = [0 for i in level_list]
    individual_MHU_test_out_matrix.index = level_list
    for j in range(len(level_list) - 1):
        # print(j)
        for k in range(j + 1, len(level_list)):
            # print(j, k)
            temp_1 = copy.deepcopy(
                np.mean(locals()['X_%s' % (level_list[j])]) - np.mean(locals()['X_%s' % (level_list[k])]))
            temp_2 = copy.deepcopy(individual_MHU_test_out.loc[str(level_list[j]) + ' 与 ' + str(level_list[k]), 'Star_Mark'])
            temp_3 = copy.deepcopy(individual_MHU_test_out.loc[str(level_list[j]) + ' 与 ' + str(level_list[k]), 'MHU统计量值'])
            individual_MHU_test_out_matrix.loc[level_list[j], level_list[k]] = str(float('%.2f' % temp_1)) + str(
                temp_2) + '(' + str(float('%.2f' % temp_3)) + ')'
    """ KS_检验 """
    individual_KS_test_out = pd.DataFrame()
    for j in range(len(level_list)):
        # print(j)
        locals()['X_%s' % (level_list[j])] = copy.deepcopy(X[X.iloc[:, 0] == level_list[j]].iloc[:, 1])
    for j in range(len(level_list)):
        # print(j)
        for k in range(j + 1, len(level_list)):
            # print(j, k)
            # print(str(level_list[j]) + ' 与 ' + str(level_list[k]))
            temp_df = pd.DataFrame()
            locals()['individual_KS_test_%s_%s' % (j, k)] = copy.deepcopy(
                stats.ks_2samp(locals()['X_%s' % (level_list[j])], locals()['X_%s' % (level_list[k])]))
            temp_df[str(columns_list[0])] = [str(level_list[j]) + ' 与 ' + str(level_list[k])]
            temp_df['企业数量(左)'] = [len(locals()['X_%s' % (level_list[j])])]
            temp_df['信用得分均值(左)'] = [float('%.4f' % np.mean(locals()['X_%s' % (level_list[j])]))]
            temp_df['企业数量(右)'] = [len(locals()['X_%s' % (level_list[k])])]
            temp_df['信用得分均值(右)'] = [float('%.4f' % np.mean(locals()['X_%s' % (level_list[k])]))]
            temp_df['检验的均值差值'] = [float(
                '%.4f' % (np.mean(locals()['X_%s' % (level_list[j])]) - np.mean(locals()['X_%s' % (level_list[k])])))]
            temp_df['KS统计量值'] = [float('%.4f' % locals()['individual_KS_test_%s_%s' % (j, k)][0])]
            temp_df['P_Value'] = [float('%.6f' % np.float(locals()['individual_KS_test_%s_%s' % (j, k)][1]))]
            temp_df = copy.deepcopy(significance_level_mark(temp_df, subject))
            individual_KS_test_out = pd.concat([individual_KS_test_out, temp_df], ignore_index=False)
        individual_KS_test_out.index = list(individual_KS_test_out[str(columns_list[0])])
    individual_KS_test_out_matrix = pd.DataFrame()
    for i in level_list:
        individual_KS_test_out_matrix[i] = [0 for i in level_list]
    individual_KS_test_out_matrix.index = level_list
    for j in range(len(level_list) - 1):
        # print(j)
        for k in range(j + 1, len(level_list)):
            # print(j, k)
            temp_1 = copy.deepcopy(
                np.mean(locals()['X_%s' % (level_list[j])]) - np.mean(locals()['X_%s' % (level_list[k])]))
            temp_2 = copy.deepcopy(individual_KS_test_out.loc[str(level_list[j]) + ' 与 ' + str(level_list[k]), 'Star_Mark'])
            temp_3 = copy.deepcopy(
                individual_KS_test_out.loc[str(level_list[j]) + ' 与 ' + str(level_list[k]), 'KS统计量值'])
            individual_KS_test_out_matrix.loc[level_list[j], level_list[k]] = str(float('%.2f' % temp_1)) + str(
                temp_2) + '(' + str(float('%.2f' % temp_3)) + ')'
    """ 非参数统计Wald-Wolfowitz游程检验runstest_2samp """
    individual_WWR_test_out = pd.DataFrame()
    for j in range(len(level_list)):
        # print(j)
        locals()['X_%s' % (level_list[j])] = copy.deepcopy(X[X.iloc[:, 0] == level_list[j]].iloc[:, 1])
    for j in range(len(level_list)):
        # print(j)
        for k in range(j + 1, len(level_list)):
            # print(j, k)
            # print(str(level_list[j]) + ' 与 ' + str(level_list[k]))
            temp_df = pd.DataFrame()
            locals()['individual_WWR_test_%s_%s' % (j, k)] = copy.deepcopy(
                runstest_2samp(locals()['X_%s' % (level_list[j])], locals()['X_%s' % (level_list[k])]))
            temp_df[str(columns_list[0])] = [str(level_list[j]) + ' 与 ' + str(level_list[k])]
            temp_df['企业数量(左)'] = [len(locals()['X_%s' % (level_list[j])])]
            temp_df['信用得分均值(左)'] = [float('%.4f' % np.mean(locals()['X_%s' % (level_list[j])]))]
            temp_df['企业数量(右)'] = [len(locals()['X_%s' % (level_list[k])])]
            temp_df['信用得分均值(右)'] = [float('%.4f' % np.mean(locals()['X_%s' % (level_list[k])]))]
            temp_df['检验的均值差值'] = [float(
                '%.4f' % (np.mean(locals()['X_%s' % (level_list[j])]) - np.mean(locals()['X_%s' % (level_list[k])])))]
            temp_df['WWR统计量值'] = [float('%.4f' % locals()['individual_WWR_test_%s_%s' % (j, k)][0])]
            temp_df['P_Value'] = [float('%.6f' % np.float(locals()['individual_WWR_test_%s_%s' % (j, k)][1]))]
            temp_df = copy.deepcopy(significance_level_mark(temp_df, subject))
            individual_WWR_test_out = pd.concat([individual_WWR_test_out, temp_df], ignore_index=False)
        individual_WWR_test_out.index = list(individual_WWR_test_out[str(columns_list[0])])
    individual_WWR_test_out_matrix = pd.DataFrame()
    for i in level_list:
        individual_WWR_test_out_matrix[i] = [0 for i in level_list]
    individual_WWR_test_out_matrix.index = level_list
    for j in range(len(level_list) - 1):
        # print(j)
        for k in range(j + 1, len(level_list)):
            # print(j, k)
            temp_1 = copy.deepcopy(
                np.mean(locals()['X_%s' % (level_list[j])]) - np.mean(locals()['X_%s' % (level_list[k])]))
            temp_2 = copy.deepcopy(individual_WWR_test_out.loc[str(level_list[j]) + ' 与 ' + str(level_list[k]), 'Star_Mark'])
            temp_3 = copy.deepcopy(
                individual_WWR_test_out.loc[str(level_list[j]) + ' 与 ' + str(level_list[k]), 'WWR统计量值'])
            individual_WWR_test_out_matrix.loc[level_list[j], level_list[k]] = str(float('%.2f' % temp_1)) + str(
                temp_2) + '(' + str(float('%.2f' % temp_3)) + ')'
    return single_t_test_out, individual_t_test_out, individual_t_test_out_matrix, \
           individual_MHU_test_out, individual_MHU_test_out_matrix, \
           individual_KS_test_out, individual_KS_test_out_matrix, \
           individual_WWR_test_out, individual_WWR_test_out_matrix


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


def main():
    path, path_level_1 = creat_filefolds_ykp()  # 自动获取文件所在路径
    sheetname = "Sheet1"
    data_in = pd.read_excel(path + 'Data_input1.xlsx', sheet_name=sheetname)  # 读取数据(数据要求: 第1列为类别列, 第2列为信用得分)
    subject = "Economy"
    data_in["Category"] = [str(x) for x in list(data_in["Category"])]
    data_in["Value"] = [np.float(x) for x in list(data_in["Value"])]
    results_out = significance_ykp(data_in, subject)  # 得出显著性检验结果
    # 输出Excel结果
    out_sheet_list = ['(1)单样本T检验结果', '(2)独立样本T检验结果', '(3)独立样本T检验的结果矩阵',
                      '(4)MHU检验结果', '(5)MHU检验的结果矩阵', '(6)KS检验结果',
                      '(7)KS检验的结果矩阵', '(8)WWR检验结果', '(9)WWR检验的结果矩阵']
    nowTime1 = datetime.datetime.now().strftime('%Y.%m.%d.%H')  # 记录当前的年、月、日、小时
    nowTime2 = datetime.datetime.now().strftime('%M')  # 记录当前的分钟
    save_name = nowTime1 + '：' + nowTime2 + '.显著性检验结果.xlsx'
    writer = pd.ExcelWriter(path_level_1 + save_name)
    for i in range(len(results_out)):
        results_out[i].to_excel(excel_writer=writer, sheet_name=out_sheet_list[i], index=True)
    writer.save()
    writer.close()


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')
    main()
