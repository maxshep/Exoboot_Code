import matplotlib.pyplot as plt
import pandas as pd
import exoboot
import time


def save_plot(filename: str, vars_to_plot: list, save=True, max_file_len=24000):
    filenames = [filename+'_LEFT.csv',
                 filename+'_RIGHT.csv']  # LEFT then RIGHT
    sides = ['left', 'right']
    fig, axs = plt.subplots(2, figsize=(20, 5), dpi=80)
    for i in range(2):
        try:
            df = pd.read_csv(filenames[i])
            if len(df) > max_file_len:
                print('Data file too long to plot')
                return
            for var_name in vars_to_plot:
                data = df[var_name]
                axs[i].plot(df.loop_time, data, label=sides[i]+'_'+var_name)
            axs[i].legend()
        except:
            print(filenames[i], ' not found for plotting')
            pass
    if save:
        plt.savefig(filename + '_plot.png')
