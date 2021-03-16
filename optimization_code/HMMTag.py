import sys
import numpy as np
from collections import deque
import time
import re

data_file = sys.argv[1]
output_file = "viterbi_hmm_output.txt"
counts = {}
words = {}
tags_dict = {}
tags = []
get_e_dict = {}
get_q_dict = {}
word_tags ={}

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
    elif re.search(r'(\bun|\bin|ble\b|ry\b|ish\b|ious\b|ical\b|\bnon|est\b)',element):
        return '^adj'
    elif re.search(r'(s\b)',element):
        return "^s"
    return "^mm"

def read_e():
    with open(sys.argv[3], 'r') as f:
        data = f.read()
    data = data.split("\n")
    for sentence in data:
        if sentence != "":
            word = sentence.split("   ")
            words[str(word[0].split(" ")[0])] = 0
            counts[str(word[0]).casefold()] = int(word[1])


def read_q():
    with open(sys.argv[2], 'r') as f:
        data = f.read()
    data = data.split("\n")
    for sentence in data:
        if sentence != "":
            tag = sentence.split("   ")
            tags_dict[str(tag[0])] = int(tag[1])
            for t in tag[0].split(" "):
                if not t in tags and t != "<S>" and t != "<E>":
                    tags.append(t)


def getE(element, tag):
    count_of_element = 0
    if counts.keys().__contains__(str(element + " " + tag).casefold()):
        count_of_element = counts[str(element + " " + tag).casefold()]
    tag_count = tags_dict[str(tag)]
    return float(count_of_element / tag_count)


def getQ(tag1, tag2, tag3):
    sum_all_tags = 0
    for tag in tags:
        if tags_dict.__contains__(str(tag)):
            sum_all_tags += tags_dict[str(tag)]
            
    p1, p2, p3 = 0, 0, 0
    if tag1 == "<S>" and tag3 == "<E>":
        return 1

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

    return 0.57 * p1 + 0.34 * p2 + 0.09*p3


def possible_tags(k,word):
    if k in (-1, 0):
        return ["<S>"]
    else:
        return word_tags[word]

def S(k):
    if k in (-1, 0):
        return ["<S>"]
    else:
        return tags

def getQdict():
    for k in range(1,4):
        for u in S(k):
            for v in S(k-1):
                for w in S(k-2):
                    get_q_dict[w + " " + v + " " + u] = getQ(w,v,u)

    for k in range(1,3):
        for u in S(k-1):
            for v in S(k):
                get_q_dict[u + " " + v + " " + "<E>"] = getQ(u,v,"<E>")

def get_legit_tags():
    legit_tags = []
    for word in words.keys():
        for tag in tags:
            if get_e_dict[word + " " + tag] != 0:
                legit_tags.append(tag)
        word_tags[word] = legit_tags.copy()
        legit_tags.clear()

def getEdict():
    for word in words.keys():
        for tag in tags:
            get_e_dict[word + " " + tag] = getE(word,tag)

def Viterbi_Decoding(sentence):
    V = {}
    B = {}  # B
    # init
    words_of_sentence = []
    words_of_sentence.append(sentence[0] if sentence[0] in words.keys() else "^ss")
    words_of_sentence[1:] = [word if word in words.keys() else tokenize(word) for word in sentence[1:]]

    V[str("0 <S> <S>")] = 0
    n = len(words_of_sentence)
    for k in range(1, n + 1):
        tmp = ""
        if k > 1:
            tmp = words_of_sentence[k - 2]
        for u in possible_tags(k - 1,tmp):
            for v in possible_tags(k,words_of_sentence[k-1]):
                max_score = float('-Inf')
                max_tag = None
                tmp = ""
                if k > 2:
                    tmp = words_of_sentence[k - 3]
                for w in possible_tags(k - 2,tmp):
                    score = float(V[str(str(k - 1) + " " + w + " " + u)] + np.log(get_e_dict[words_of_sentence[k-1] + " " + v]) + np.log(get_q_dict[w + " " + u + " " + v]))
                    if score > max_score:
                        max_score = score
                        max_tag = w

                V[str(str(k) + " " + u + " " + v)] = max_score
                B[str(str(k) + " " + u + " " + v)] = max_tag

    # backtracking

    max_score = float('-Inf')
    v_max = ""
    u_max = ""
    res_tags = []
    if n == 1:
        for v in possible_tags(n,words_of_sentence[n-1]):
            score = V[str(str(n) + " <S>" + " " + v)] + np.log(get_q_dict["<S> " + v +  " <E>"])
            if score > max_score:
                max_score = score
                v_max = v
        
        res_tags.append(v_max)
        return res_tags

    else:
        for u in possible_tags(n - 1,words_of_sentence[n-2]):
            for v in possible_tags(n,words_of_sentence[n-1]):
                score = V[str(str(n) + " " + u + " " + v)] + np.log(get_q_dict[u + " " + v + " " + "<E>"])
                if score > max_score:
                    max_score = score
                    u_max = u
                    v_max = v

    res_tags.append(v_max)
    res_tags.append(u_max)

    for i, k in enumerate(range(n - 2, 0, -1)):
        res_tags.append(str(B[str(str(k + 2) + " " + res_tags[i + 1] + " " + res_tags[i])]))

    return list(reversed(res_tags))


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
    getQdict()
    getEdict()
    get_legit_tags()
    with open(data_file, "r") as f:
        data = f.read()
    data = data.split("\n")
    with open(output_file, "w+") as f:
        for i in range(len(data)):
            sentence = data[i].split(" ")
            if sentence != [""]:
                res_tags = Viterbi_Decoding(sentence)
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