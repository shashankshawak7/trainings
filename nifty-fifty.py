
# coding: utf-8
########################################################################################################
##modules required : pandas
#pandas module can be installed using pip command
#pip install pandas
#if inside proxy server" pip --proxy proxy_server:port install pandas
#######################################################################################################
###let me know if any issues
########################################################################################################

import pandas as pd
import os
import time
import requests
from datetime import datetime, timedelta

##########################################################################################
timestr = time.strftime("%Y%m%d")
mydate=time.strftime("%d%m%Y")

s = mydate
date = datetime.strptime(s, "%d%m%Y")
modified_date = date + timedelta(days=-1)
old_date=datetime.strftime(modified_date, "%d%m%Y")
niftyfile="nifty_100.csv_"+timestr
os.system('curl  https://www.nseindia.com/content/indices/ind_nifty100list.csv >'+ niftyfile)
volatalityfile="volatality.csv"
def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok
#downloading the files
if exists('https://www.nseindia.com/archives/nsccl/volt/CMVOLT_'+ mydate +'.CSV') == True:
    os.system('curl  https://www.nseindia.com/archives/nsccl/volt/CMVOLT_'+ mydate +'.CSV >'+volatalityfile)
    
else:
    os.system('curl  https://www.nseindia.com/archives/nsccl/volt/CMVOLT_'+ old_date +'.CSV >'+volatalityfile)
#reading the files
df1 = pd.read_csv(niftyfile, header=None )
df2 = pd.read_csv(volatalityfile, header=None)
##########################################################################
#merging files on the basis of columns in both files
##########################################################################
merger = pd.merge(df1, df2, left_on = 2, right_on = 1)
merger.to_csv('combined.csv', header=None, index=False)
df=pd.read_csv('combined.csv')
#sorting values as required
df = df.sort_values(by=['Underlying Annualised Volatility (F) = E*Sqrt(365)', 'Previous Day Underlying Volatility (D)','Current Day Underlying Daily Volatility (E) = Sqrt(0.94*D*D + 0.06*C*C)'])
df.loc[:,'Previous Day Underlying Volatility (D)'] *= 100
df.loc[:,'Current Day Underlying Daily Volatility (E) = Sqrt(0.94*D*D + 0.06*C*C)'] *= 100
df.loc[:,'Underlying Annualised Volatility (F) = E*Sqrt(365)'] *= 100
################################################################################
#dropping columns as required
##########################################################################
df.drop(df.columns[[7,10]], axis=1, inplace=True)
df=df.loc[df['Current Day Underlying Daily Volatility (E) = Sqrt(0.94*D*D + 0.06*C*C)'] >= 2]
df.drop(df.columns[[3,4,5]], axis=1, inplace=True)
datestr=df.iloc[3,3]
df.drop(df.columns[[3]], axis=1, inplace=True)
df = df.sort_values('Current Day Underlying Daily Volatility (E) = Sqrt(0.94*D*D + 0.06*C*C)',ascending=[False])
df.rename(columns={'Previous Day Underlying Volatility (D)': 'previous volatality', 'Current Day Underlying Daily Volatility (E) = Sqrt(0.94*D*D + 0.06*C*C)': 'current volatality','Underlying Annualised Volatility (F) = E*Sqrt(365)':'annual volatality','Underlying Previous Day Close Price (B)':'previous close','Underlying Close Price (A)':'current close'}, inplace=True)
#datestr="testing"
final_file="fresh_data_"+datestr+".csv"
########################################################################################
#generating final file
##########################################################################################
df.to_csv(final_file,header=True)
os.remove('combined.csv')
os.system("mailx -a 'fresh_data_" +datestr+".csv' -s 'volatility' shashankshawak7@gmail.com  < /dev/null" ) 
os.system('rm '+ niftyfile)
os.system('rm '+volatalityfile)
