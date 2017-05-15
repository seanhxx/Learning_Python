import pandas as pd
import numpy
from collections import Counter
from scipy import stats as ss
import re
import os
import csv
import sys
import traceback
from sklearn.ensemble import RandomForestClassifier
from pyspark import SparkContext, SparkConf, StorageLevel
from pyspark.sql import SQLContext, HiveContext, DataFrame, Row
from pyspark.sql.functions import udf, lit, instr, concat, col
from pyspark.sql.types import *
from pyspark.sql import SQLContext

class DataAnalysis(object):
    def __init__(self, tablename, date_start, date_end, device, package):
        self.tablename = tablename
        self.date_start = date_start
        self.date_end = date_end
        self.device = device
        self.package =  package
        try:
            bank = hive_context.table("prod_mti_ww_be_idl.mam_tx")
            bank.registerTempTable("mam")
            query = "select ma_id, role, resource, resource_ma_type, material_ma_type_id, event_ma_id,attribute_id,material_id, attribute_value, attribute_prior_value, date_time_local, event_type, operation from mam WHERE system_name = 'MAMASMSI' and ma_type =  'LOT' and facility_id = 'ASSEMBLY-MSA'and ma_type =  'LOT'\
              and ma_id in (content_user_input_lot_ID\
              ) and partition_date between 'content_user_input_start_date' and 'content_user_input_end_date'"
            self._data = hive_context.sql(query)
            print("Initialized")
            #data for softbin triggering
            '''query1 =''' 
            #data for feature analysis
        except Exception as e:
            print(e.message)            
            
#%%
    @staticmethod
    def analysis(df):
        def getdata(df):
            columns1 = ['ma_id','role','resource']
            df1 = df.query("resource_ma_type in ('HUMAN','MACHINE') and role not in ('WAFER MEASURE OPER',\
                            'STRIP SORTER OPER','STRIP SORTER MACH','SPLIT OPER','SHIP OPERATOR',\
                            'SCREEN CHECK OPER','SCRAP OPERATOR','SAM INSPECT OPER','SAM INSPECT MACHINE',\
                            'SAM INSP RETURN OPER','SAM INSP ISSUE OPER','RECEIVE OPERATOR','PRODUCT ASSIGN OPER',\
                            'PROCESS ASSIGN OPER','LOT LOCATE OPERATOR','LEADFRAME COUNT OPER','ENCAP RECEIVE OPER',\
                            'DIE BANK OPER','COMMENT OPERATOR','CHANGE OPERATOR','ATCH/C UNLOAD OPER','ADJUST OPERATOR',\
                            'CHANGE OPER','OPERATOR','SURVEILLANCE OPER','SUBCON TRACK OPER')" )
            part1 = pd.DataFrame(df1,columns = columns1)
            columns2 = ['ma_id','material_ma_type_id','material_id']
            df2 = df [pd.notnull(df.material_id)]
            part2 = pd.DataFrame(df2,columns = columns2)
            part2.rename(columns={'ma_id': 'ma_id', 'material_ma_type_id': 'role','material_id':'resource'}, inplace=True)
            rawdata = part1.append(part2)
            rawdata = rawdata.drop_duplicates()
            return rawdata
    
        def mergeparentinfo(rawdata,df):
            columns = ['event_ma_id','ma_id']
            df = df.query("event_type == 'MACreated' and event_ma_id != ma_id")
            df = pd.DataFrame(df,columns = columns)
            df = df.drop_duplicates()
            tmp = pd.merge(df, rawdata, how='inner', on=['ma_id'])
            tmp.rename(columns={'ma_id':'parent_id','event_ma_id': 'ma_id'}, inplace=True)
            columns2 = ['ma_id','role','resource']
            tmp = pd.DataFrame(tmp, columns = columns2)
            #append parent lot info when the info is not in child lot info
            copyrawdata = rawdata
            for index, row in tmp.iterrows():
                if (row['ma_id'] in copyrawdata['ma_id'] and row['role'] in copyrawdata['role']) or(row['ma_id'] not in copyrawdata['ma_id']): 
                    continue
                else:
                    rawdata = rawdata.append(row)
            return rawdata
    
        def rawdata(df):
            #3 iteration of parent lot info merge
            a = mergeparentinfo(getdata(df),df)
            b = mergeparentinfo(a,df)
            c = mergeparentinfo(b,df)
            rawdata = c
            file_path = os.path.join('content_user_input_path', 'result_raw.csv')
            pd.DataFrame(rawdata).to_csv(file_path)
            c['txt'] = c['role'] + '#' + c['resource']
            c['txt'] = [x.strip().replace(' ', '_') for x in c['txt']]
            c = c.pivot_table(index='ma_id', values = 'txt', aggfunc = lambda x: ' '.join(x))
            c.rename(columns =['text'])
            return c
    
        def text_analysis(df):   
            # find frequent features in bad lot text
            try:
                df1 = pd.read_csv("content_user_input_csv_file")
                df1 = df1.set_index(["LOT"]) 
                failrate = df1['FNC'].tolist()
                df2 = rawdata(df)
                df3 = df1.join(df2, how = 'left')
                txt_bad = ''
                for index, row in df3.iterrows():
                    if row['RESULT'] == 1:
                        txt_bad = row['txt']+txt_bad
                df3.dropna(inplace=True)
                reg = re.compile('\S{4,}')
                c = Counter(ma.group() for ma in reg.finditer(txt_bad))
                #only choose features explain >60% bad lot and create new data frame
                common = [k for k,v in c.items()]
                i = 0
                while i< len(common):
                    temp = []
                    for index, row in df3.iterrows():
                        if row['txt'].find(common[i])>0:
                            a=1
                        else:
                            a=0
                        temp.append(a)
                    column = common[i]
                    df3[column] = temp
                    i = i+1
                df3 = df3.drop(df3.columns[[0,2]], axis=1)
                param = df3.values.T.tolist()
                response = param[0]
            #    response = numpy.asarray(response).T.tolist()
                param.pop(0)
                feature = numpy.asarray(param).T.tolist()
                name = list(df3)
                name.pop(0)
                return response, feature, name, failrate
            except Exception as e:
                print(e.message)
        def randomforest(X,Y,names):
            rf = RandomForestClassifier(max_depth = 4, n_jobs=-1, n_estimators = 1000,random_state = 12)
            rf.fit(X, Y)
        #    print ("Random Forest Classifier")
         #   print ("Features sorted by their score:")
            result =  (sorted(zip(map(lambda x: round(x, 4), rf.feature_importances_), names), reverse=True))
            df_result = pd.DataFrame(result)
            df_result.columns = ['RF Score','Features']
            file_path = os.path.join('content_user_input_path', 'result_rf.csv')
            pd.DataFrame(df_result.head(10)).to_csv(file_path)

            feature_importance = rf.feature_importances_
        #    dic = dict(zip(names, feature_importance))
        #    valid_feature_importance = [dic.get(s, -1.) for s in names]
        #   select 3 most important features
            sorted_idx = numpy.argsort(feature_importance)[::-1][:3]
            vip_name = [names[i] for i in sorted_idx]
            return vip_name, df_result.head(10)
        
        '''def normalanalysis(df):
            df1 = hardbin(df)
            df2 = normalrawdata(df)
            df3 = df1.join(df2, how = 'left')
            df3 = df3.drop(df3.columns[[0, 1, 2]], axis=1)
            param = df3.values.T.tolist()
            response = param[0]
        #    response = numpy.asarray(response).T.tolist()
            param.pop(0)
            feature = numpy.asarray(param).T.tolist()
            name = list(df3)
            name.pop(0)
            return response, feature, name
        
        def normalrawdata(df):
            #3 iteration of parent lot info merge
            a = mergeparentinfo(getdata(df),df)
            b = mergeparentinfo(a,df)
            c = mergeparentinfo(b,df)
            c = c.pivot_table(index='ma_id', columns='role', values = 'resource',  aggfunc = lambda x: ' '.join(x))
            return c
        
        df = pd.read_excel('example.xlsx')
        Y,X,names = normalanalysis(df)
        randomforest(X,Y,names)'''
        
        def kruskalwallis(X,Y,names,vip_name):
            file_path = os.path.join('content_user_input_path', 'result_k.csv')
            try:
                X = numpy.asarray(X).T.tolist()
                new_X = [X[names.index(x)] for x in vip_name]
                H = []
                kw_result = []
                for b in new_X:
                    a0 = [a for a in Y if (b[Y.index(a)] == 0)]
                    a1 = [a for a in Y if (b[Y.index(a)] == 1)]
                    h = ss.mstats.kruskalwallis(a0, a1)[0]
                    H.append(h)
                    kw_score = list(zip(vip_name, H))
                    kw_result = numpy.sort(kw_score, axis=0)[::-1][:3].tolist()
                    kw_df = pd.DataFrame(kw_result)
                    kw_df.columns = ["Features","H-test Score"]
                #below output need to change to kw_df
                # with open(file_path, 'wb') as outfile:
                #     wr = csv.writer(outfile, quoting=csv.QUOTE_ALL)
                #     wr.writerow(kw_result)
                pd.DataFrame(kw_df).to_csv(file_path)
                return kw_df
            except Exception as e:
                traceback.print_exc()
                print(str(e))
                print('KruskalWallis_Error')
                tmp_ls = ['Null', 'Null', 'Null']
                with open(file_path, 'wb') as outfile:
                    wr = csv.writer(outfile, quoting=csv.QUOTE_ALL)
                    wr.writerow(tmp_ls)
                return tmp_ls

        Y,X,names,failrate = text_analysis(df)
        result, result_print = randomforest(X,Y,names)
        # print (result_print)
        kresult = kruskalwallis(X,failrate,names,result)
        # print (kresult)
#%%
def main(argv):
    print("active main")
    tablename = argv[0]
    date_start = argv[1]
    date_end = argv[2]
    device = argv[3]
    package = argv[4]
    try:
        finalAnalysis = DataAnalysis(tablename, date_start, date_end, device, package)
        df = finalAnalysis._data.toPandas()
        finalAnalysis.analysis(df)
        print('Files_generated')
    except Exception as e:
        traceback.print_exc()
        print(e.message)
        print('File_generation_fail')

if __name__ == "__main__":
    sc =SparkContext()
    hive_context = HiveContext(sc)  
    argv = ["prod_mti_ww_be_idl.mam_tx", '2017-02-14' , '2017-02-15' ,"B0KB","3DP"]
    main(argv)