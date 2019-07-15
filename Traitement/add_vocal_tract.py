
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import os
import librosa
import numpy as np
import scipy
import torch
from Apprentissage.velum_modele import learn_velum

   # from velum_modele import learn_velum
import matplotlib.pyplot as plt
articulators = [
        'tt_x', 'tt_y', 'td_x', 'td_y', 'tb_x', 'tb_y', 'li_x', 'li_y',
        'ul_x', 'ul_y', 'll_x', 'll_y']




articulators_after = [
        'tt_x', 'tt_y', 'td_x', 'td_y', 'tb_x', 'tb_y', 'li_x', 'li_y',
        'ul_x', 'ul_y', 'll_x', 'll_y','la','pro','ttcl','tbcl','lar','v_x','v_y'] #détailler

root_folder = os.path.dirname(os.getcwd())


def add_vocal_tract(speaker,max):
    print("adding vocal tracts for speaker {}".format(speaker))
    def add_lip_aperture(ema):
        ind_1, ind_2 = [articulators.index("ul_y"), articulators.index("ll_y")]
        lip_aperture = ema[:, ind_1] - ema[:, ind_2]  # upperlip_y - lowerlip_y
        return lip_aperture
    def add_lip_protrusion(ema):
        ind_1, ind_2 = [articulators.index("ul_x"), articulators.index("ll_x")]
        lip_protrusion = (ema[:, ind_1] + ema[:, ind_2]) / 2
        return lip_protrusion

    def add_voicing(wav,ema,sr):
        hop_time = 10 / 1000  # en ms
        hop_length = int((hop_time * sr))
        N_frames = int(len(wav) / hop_length)
        window = scipy.signal.get_window("hanning", N_frames)
        ste = scipy.signal.convolve(wav ** 2, window ** 2, mode="same")
        ste = scipy.signal.resample(ste, num=len(ema))
        ste = [np.max(min(x, 1), 0) for x in ste]
        return ste

    def add_TTCL(ema): #tongue tip constriction location in degree
        ind_1, ind_2 = [articulators.index("tt_x"), articulators.index("tt_y")]
        TTCL = ema[:, ind_1] / np.sqrt(ema[:, ind_1]**2+ema[:,ind_2]**2 ) # upperlip_y - lowerlip_y
        return TTCL

    def add_TBCL(ema): #tongue body constriction location in degree
        ind_1, ind_2 = [articulators.index("tb_x"), articulators.index("tb_y")]
        TBCL = ema[:, ind_1] / np.sqrt(ema[:, ind_1] ** 2 + ema[:, ind_2] ** 2)  # upperlip_y - lowerlip_y
        return TBCL


    def add_velum(mfcc):
        model = learn_velum(hidden_dim=200, input_dim=429, output_dim=2, name_file="modele_velum").double()
        model_to_load = os.path.join(root_folder, "Apprentissage", "saved_models", "modeles_valides",
                                     "modele_velum.txt")
        loaded_state = torch.load(model_to_load)
        model.load_state_dict(loaded_state)
        mfcc_2 = torch.from_numpy(mfcc).view((1, len(mfcc), len(mfcc[0])))
        velum_xy = model(mfcc_2).double()
        velum_xy = velum_xy.detach().numpy().reshape((len(mfcc), 2))
        return velum_xy

    if speaker in ["msak0", "fsew0","maps0","faet0","mjjn0","ffes0"]:
        speaker_2 = "mocha_" + speaker
        wav_path = os.path.join(root_folder, "Donnees_brutes","mocha", speaker)
        sampling_rate_wav = 16000

    elif speaker in ["F1", "F5", "M1","M3"]:
        speaker_2 = "usc_timit_" + speaker
        wav_path = os.path.join(root_folder, "Donnees_brutes", "usc_timit",speaker,"wav_cut")
        sampling_rate_wav = 20000

    elif speaker == "MNGU0":
        speaker_2 = speaker
        wav_path = os.path.join(root_folder, "Donnees_brutes", speaker,"wav")
        sampling_rate_wav= 16000
    elif speaker in ["F01", "F02", "F03", "F04", "M01", "M02", "M03", "M04"]:
        speaker_2 = "Haskins_"+speaker
        wav_path = os.path.join(root_folder, "Donnees_brutes", "Haskins_IEEE_Rate_Comparison_DB",speaker,"wav")
        sampling_rate_wav= 44100

    mfcc_path = os.path.join(root_folder, "Donnees_pretraitees", speaker_2,"mfcc")
    files_path = os.path.join(root_folder, "Donnees_pretraitees", speaker_2,"ema_filtered_norma")

    if not os.path.exists(os.path.join(root_folder,"Donnees_pretraitees",speaker_2,"ema_VT")):
        os.makedirs(os.path.join(root_folder,"Donnees_pretraitees",speaker_2,"ema_VT"))

    EMA_files_names = sorted(
        [name[:-4] for name in os.listdir(files_path) if name.endswith('.npy')])

    EMA_files_names = [f for f in EMA_files_names if "split" not in f ] #juste pour ignorer mgnu0
    N = len(EMA_files_names)
    if max != "All":
        N = max
    for i in range(N):
        if i+1%500 ==0:
            print("{} out of {}".format(i, N))
        ema = np.load(os.path.join(files_path,EMA_files_names[i]+".npy"))
        lip_aperture = add_lip_aperture(ema)
        lip_protrusion = add_lip_protrusion(ema)
        TTCL = add_TTCL(ema)
        TBCL = add_TBCL(ema)
        if speaker in ["fsew0","msak0","faet0","ffes0","falh0"] : # 14 arti de 0 à 13 (2*6 + 2)
            wav,sr = librosa.load(os.path.join(wav_path, EMA_files_names[i] + ".wav"),sr = sampling_rate_wav)
            voicing = add_voicing(wav, ema, sampling_rate_wav)
            velum_xy = ema[:,-2:]
            ema = np.concatenate((ema,np.zeros((len(ema),5))),axis=1)

        elif speaker in ["MNGU0","maps0","mjjn0"]: # 12 arti de 0 à 11
            wav, sr = librosa.load(os.path.join(wav_path, EMA_files_names[i] + ".wav"), sr=sampling_rate_wav)
            voicing = add_voicing(wav, ema, sampling_rate_wav)
            mfcc = np.load(os.path.join(mfcc_path, EMA_files_names[i] + ".npy"))
            velum_xy = add_velum(mfcc)
            ema = np.concatenate((ema,np.zeros((len(ema),7))),axis=1)

        elif speaker in ["F1","F5","M1","M3"]:
            wav = np.load(os.path.join(wav_path, EMA_files_names[i] + ".npy"))
            mfcc = np.load(os.path.join(mfcc_path,EMA_files_names[i]+".npy"))
            ema = np.concatenate((ema,np.zeros((len(ema),7))),axis=1)

            if len(ema)!= len(mfcc):
                print("pbm shape",len(ema),len(mfcc),EMA_files_names[i])
            voicing = add_voicing(wav,ema,sampling_rate_wav)
            velum_xy = add_velum(mfcc)

        elif speaker in  ["F01","F02","F03","F04","M01","M02","M03","M04"] : #haskins
            wav = np.reshape(np.load(os.path.join(wav_path, EMA_files_names[i] + ".npy")),-1)
            mfcc = np.load(os.path.join(mfcc_path, EMA_files_names[i] + ".npy"))
            ema = np.concatenate((ema, np.zeros((len(ema), 7))), axis=1)
            if len(ema) != len(mfcc):
                print("pbm shape", len(ema), len(mfcc), EMA_files_names[i])
            voicing = add_voicing(wav, ema, sampling_rate_wav)
            velum_xy = add_velum(mfcc)

        ema[:, 12] = lip_aperture
        ema[:, 13] = lip_protrusion
        ema[:, 14] = TTCL
        ema[:, 15] = TBCL
        ema[:, 16] = voicing
        ema[:, 17:19] = velum_xy
        np.save(os.path.join(root_folder,"Donnees_pretraitees",speaker_2,"ema_VT",EMA_files_names[i]),ema)

#speakers =  ["F01","F02","F03","F04","M01","M02","M03","M04","F5","F1","M1","M3"
 #   ,"maps0","faet0",'mjjn0',"ffes0","MNGU0","fsew0","msak0"]

def add_vocal_tract_per_corpus(corpus,max="All") :
    if corpus == "MNGU0":
        speakers = ["MNGU0"]
    elif corpus == "usc":
        speakers = ["F1", "F5", "M1","M3"]
    elif corpus == "Haskins":
        speakers=  ["F01","F02","F03","F04","M01","M02","M03","M04"]

    elif corpus == "mocha":
        speakers =["fsew0","msak0","faet0","ffes0","maps0","mjjn0"]

    else :
        print("vous navez pas choisi un des corpus")

    for sp in speakers :
        add_vocal_tract(sp,max = max)

corpus = ["mocha","usc","MNGU0","Haskins"]

for co in corpus :
    print("adding vt for corpus ",co)
    add_vocal_tract_per_corpus(co)