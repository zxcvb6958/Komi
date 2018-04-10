import sys

def get_all_images(filename):
    file = open(filename)
    lines = file.readlines()
    list = []
    for line in lines:
        line_split = line.strip('\n').split('\t')
        if(len(line_split)) == 3:
            line_split[-1] = line_split[-1].zfill(4)
            line_split[-2] = line_split[-2].zfill(4)
        if(len(line_split)) == 4:
            line_split[-1] = line_split[-1].zfill(4)
            line_split[-3] = line_split[-3].zfill(4)
        list.append(line_split)
    file.close()
    return list

def save2labelfile(list):
    file = open('label.txt', 'w')
    labellines = []
    for i in range(len(list)):
        if len(list[i]) == 3:
            labelline = list[i][0] + '/' + list[i][0] + '_' + list[i][1] + '.jpg' + '\t' + 'original' + '/' + list[i][0] + '/' + list[i][0] + '_' +list[i][2] + '.jpg' + '\t' + '1\n'
            labellines.append(labelline)
        elif len(list[i]) == 4:
            labelline = list[i][0] + '/' + list[i][0] + '_' + list[i][1] + '.jpg' + '\t' + 'original' + '/' + list[i][2] + '/' + list[i][2] + '_' + list[i][3] + '.jpg' + '\t' + '0\n'
            labellines.append(labelline)
    file.writelines(labellines)
    file.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Format Error! Usuage: python %s pairs.txt" % (sys.argv[0]))
        sys.exit()

    list = get_all_images("pairs.txt")
    save2labelfile(list)
    print("Done!")