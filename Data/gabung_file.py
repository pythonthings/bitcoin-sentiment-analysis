import os
import glob
import pandas as pd

dir = input("Masukkan Direktori File (Lengkap) :")
os.chdir(str(dir))

extension = 'xlsx'
all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

combined_excel = pd.concat([pd.read_excel(f) for f in all_filenames])

combined_excel.to_excel("Data All.xlsx", index = False, encoding='utf-8-sig')