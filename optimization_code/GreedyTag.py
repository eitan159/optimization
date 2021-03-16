import sys
import re

counts = {}
words = {}
tags_dict = {}
tags = []
data_file = sys.argv[1]
output_file = "greedy_hmm_output.txt"

def tokenize(element):
    if "-" in element:
        return "^hyp"
    elif re.search(r'\d', element) and re.search(r'\w', element):
        return "^numL"
    elif re.search(r'\d', element):
        return '^num'
    elif re.search(r'(\ban)',element):
        return "^an"
    elif re.search(r'(al\b)',element):
        return "^al"
    elif re.search(r'(ship\b)',element):
        return "^ship"
    elif re.search(r'(est\b)',element):
        return "^est"
    elif re.search(r'(ive\b)',element):
        return "^ive"
    elif re.search(r'(ing\b)',element):
        return "^ing"
    elif re.search(r'(tion\b)',element):
        return "^tion"    
    elif re.search(r'(ed\b)',element):
        return "^ed"
    elif re.search(r'(ly\b)',element):
        return "^ly"
    elif re.search(r'(es\b)',element):
        return "^es"
    elif re.search(r'(ions\b)',element):
        return "^ions"    
    elif re.search(r'(ment\b)',element):
        return "^ment"
    elif re.search(r'(ion\b)',element):
        return "^ion"    
    elif re.search(r'[A-Z][a-z]+',element):
        return "^bs"
    elif re.search(r'[A-Z]+',element):
        return "^bb"
    elif re.search(r'(ty\b|ics\b|ence\b|ance\b|ness\b|ist\b|ism\b)',element):
        return '^noun'
    elif re.search(r'(ate\b|fy\b|ize\b|\ben|\bem)', element):
        return '^verb'
    elif re.search(r'(\bun|\bin|ble\b|ry\b|ish\b|ious\b|ical\b|\bnon)',element):
        return '^adj'
    elif re.search(r'(s\b)',element):
        return "^s"
    return "^mm"

def read_e():
    with open(sys.argv[3],'r') as f:
        data = f.read()
    data = data.split("\n")
    for sentence in data:
        if sentence != "":
            word = sentence.split("   ")
            if  not '^' in word[0].split(" ")[0]:
                words[str(word[0].split(" ")[0])] = 0
            counts[str(word[0]).casefold()] = int(word[1])

def read_q():
    with open(sys.argv[2],'r') as f:
        data = f.read()
    data = data.split("\n")
    for sentence in data:
        if sentence != "":
            tag = sentence.split("   ")
            tags_dict[str(tag[0])] = int(tag[1])
            for t in tag[0].split(" "):
                if not t in tags and t != "<S>" and t != "<E>":
                    tags.append(t)


def getE(element,tag):    
    if not counts.keys().__contains__(str(element + " " + tag).casefold()):
        count_of_element = 0
    else:
        count_of_element = counts[str(element + " " + tag).casefold()]
    tag_count = tags_dict[str(tag)]
    return float(count_of_element / tag_count)


def getQ(tag1,tag2,tag3):
    sum_all_tags = 0
    for tag in tags:
        if tags_dict.__contains__(str(tag)):
            sum_all_tags += tags_dict[str(tag)]
            
    p1, p2, p3 = 0, 0, 0
    tag1tag2tag3_count = 0
    if tags_dict.__contains__(str(tag1 + " " + tag2 + " " + tag3)):
        tag1tag2tag3_count = tags_dict[str(tag1 + " " + tag2 + " " + tag3)]

    count_tag2_tag3 = 0
    if tags_dict.__contains__(str(tag2 + " " + tag3)):
        count_tag2_tag3 = tags_dict[str(tag2 + " " + tag3)]

    tag3_count = 0
    if tags_dict.__contains__(str(tag3)):
        tag3_count = tags_dict[str(tag3)]

    if tags_dict.__contains__(str(tag1 + " " + tag2)):
        p1 = float(tag1tag2tag3_count / tags_dict[str(tag1 + " " + tag2)])
    
    if tags_dict.__contains__(str(tag2)):
        p2 = float(count_tag2_tag3 / tags_dict[str(tag2)])

    p3 = float(tag3_count / sum_all_tags)
    return  0.6* p1 +  0.4* p2 + 0.1*p3

def get_legit_tags(word):
    legit_tags = []
    for tag in tags:
        if getE(word,tag) != 0:
            legit_tags.append(tag)
    return legit_tags


def Greedy_Decoding(sentence):
    tag1 = "<S>"
    tag2 = "<S>"
    res_tags = []
    words_of_sentence = []
    words_of_sentence.append(sentence[0] if sentence[0] in words.keys() else "^ss")
    words_of_sentence[1:] = [word if word in words.keys() else tokenize(word) for word in sentence[1:]]
    for i in range(len(words_of_sentence)):
        prob = 0
        word = words_of_sentence[i]
        max_tag = ""
        for tag in get_legit_tags(word):
            tmp_prob = getE(word,tag)*getQ(tag1,tag2,tag)
            if prob < tmp_prob:
                prob = tmp_prob
                max_tag = tag
        tag1 = tag2
        tag2 = max_tag
        res_tags.append(max_tag)
    return res_tags

def get_accuracy():
    with open("data\\tagger-dev", "r") as f:
        data = f.read()
    data_1 = data.split("\n")
    with open(output_file, "r") as f:
        data = f.read()
    data_2 = data.split("\n")
    counter = 0
    all_tags = 0
    for i in range(len(data_1) - 1):
        sen_1 = data_1[i].split(" ")
        sen_2 = data_2[i].split(" ")
        all_tags += len(sen_1)
        for j in range(len(sen_1)):
            if sen_1[j].split("/")[1] == sen_2[j].split("/")[1]:
                counter += 1

    return counter/all_tags * 100

def Main():
    read_e()
    read_q()
    with open(data_file,"r") as f:
        data = f.read()
    data = data.split("\n")
    with open(output_file,"w+") as f:    
        for i in range(len(data)):
            sentence = data[i].split(" ")
            if sentence != [""]:
                res_tags = Greedy_Decoding(sentence)
                for j in range(len(res_tags)):
                    if j != len(res_tags)-1:
                        f.write(sentence[j]+"/"+res_tags[j] + " ")
                    else:
                        f.write(sentence[j]+"/"+res_tags[j])
                if i != len(data) - 1:
                    f.write("\n")

if __name__ == "__main__":
    Main()
    print("accuracy: " + str(get_accuracy()))

