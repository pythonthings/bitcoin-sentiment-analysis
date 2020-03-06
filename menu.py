directory = open(r"C:\Users\mr777\Documents\pkl\FIX KANGGO\FIX KANGGO")
file_names = [fn for fn in listdir(directory) if isfile(join(directory,fn))]
count = -1
for f in file_names:
    count = count + 1
    print("[%s] " % count + f)

while True:
    ans_file = input("Select file: ")
    if ans_file > count:
        print("Wrong selection.")
        continue
    path = directory + file_names[ans_file]
    print("Selected file: %s " % path)
    break