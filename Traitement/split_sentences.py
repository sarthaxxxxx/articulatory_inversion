
import numpy as np
import random
import os
from os.path import dirname

root_folder = os.getcwd()

donnees_pretraitees_path = os.path.join(os.path.dirname(os.getcwd()),"Donnees_pretraitees")

speakers = os.listdir(donnees_pretraitees_path)
speakers.remove("fileset")
max_length = 500
speakers = speakers[8:]
print(speakers)

for sp in speakers :
    print("speaker ",sp)
    file_names = os.listdir(os.path.join(donnees_pretraitees_path,sp,"ema"))
    file_names = [f for f in file_names if 'split' not in f]
   # file_names = file_names[0:30]
    Number_cut = 0
    for f in file_names :
        ema = np.load(os.path.join(donnees_pretraitees_path,sp,"ema",f))
        mfcc = np.load(os.path.join(donnees_pretraitees_path,sp,"mfcc",f))
        ema_filtered = np.load(os.path.join(donnees_pretraitees_path,sp,"ema_filtered",f))
        ema_VT = np.load(os.path.join(donnees_pretraitees_path,sp,"ema_VT",f))

        cut_in_N = int(len(mfcc)/max_length) +1
        if cut_in_N > 1 :
            Number_cut+=1
            temp = 0
            cut_size = int(len(mfcc)/cut_in_N)
            for k in range(cut_in_N-1) :
                mfcc_k = mfcc[temp : temp + cut_size]
                ema_k = ema[temp : temp + cut_size,:]
                ema_k_f = ema_filtered[temp : temp + cut_size,:]
                ema_k_vt = ema_VT[temp:temp+cut_size,:]

                temp = temp + cut_size
                np.save(os.path.join(donnees_pretraitees_path,sp,"mfcc",f[:-4]+"_split_"+str(k)),mfcc_k)
                np.save(os.path.join(donnees_pretraitees_path,sp,"ema",f[:-4]+"_split_"+str(k)),ema_k)
                np.save(os.path.join(donnees_pretraitees_path,sp,"ema_filtered",f[:-4]+"_split_"+str(k)),ema_k_f)
                np.save(os.path.join(donnees_pretraitees_path,sp,"ema_VT",f[:-4]+"_split_"+str(k)),ema_k_vt)

            mfcc_last = mfcc[temp :]
            ema_last = ema[temp : ,:]
            ema_last_f = ema_filtered[temp: , :]
            ema_last_vt = ema_VT[temp:, :]

            np.save(os.path.join(donnees_pretraitees_path, sp, "mfcc", f[:-4] + "_split_" + str(cut_in_N-1)), mfcc_last)
            np.save(os.path.join(donnees_pretraitees_path, sp, "ema", f[:-4] + "_split_" + str(cut_in_N-1)), ema_last)
            np.save(os.path.join(donnees_pretraitees_path, sp, "ema_filtered", f[:-4] + "_split_" + str(k)), ema_last_f)
            np.save(os.path.join(donnees_pretraitees_path, sp, "ema_VT", f[:-4] + "_split_" + str(k)), ema_last_vt)

            os.remove(os.path.join(donnees_pretraitees_path,sp,"mfcc",f))
            os.remove(os.path.join(donnees_pretraitees_path,sp,"ema",f))
            os.remove(os.path.join(donnees_pretraitees_path,sp,"ema_filtered",f))
            os.remove(os.path.join(donnees_pretraitees_path,sp,"ema_VT",f))
    print("number cut for ",sp," : ",Number_cut)




