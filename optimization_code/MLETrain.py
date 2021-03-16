import sys
import re

words_tags = {}
counts = {}
Words = {}



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


def CreateEMLE(data_file, e_file):
    with open(data_file, "r") as f:
        data = f.read()
    data = data.split("\n")
    for i in range(len(data)):
        sentence = data[i].split(" ")
        if sentence != [""]:
            for j in range(len(sentence)):
                words_tag = sentence[j].rsplit("/", 1)
                Check_Signature(words_tag, j)

    with open(e_file, "w+") as f:
        for key in words_tags.keys():
            if key != '':
                word = key.split("/")
                f.write(word[0] + " " + word[1] + "   " + str(counts.get(str(key).casefold())) + "\n")


def Check_Signature(words_tag, index):
    word = words_tag[0].split("/")
    for w in word:
        Words[str(w)] = 0

        if not words_tags.keys().__contains__(str(w + "/" + words_tag[1])):
            words_tags[str(w + "/" + words_tag[1])] = 0
        if not counts.keys().__contains__(str(w + "/" + words_tag[1]).casefold()):
            counts[str(w + "/" + words_tag[1]).casefold()] = 0
        counts[str(w + "/" + words_tag[1]).casefold()] += 1

        if index == 0:
            if not words_tags.keys().__contains__(str("^ss" + "/" + words_tag[1])):
                words_tags[str("^ss" + "/" + words_tag[1])] = 0
            if not counts.keys().__contains__(str("^ss" + "/" + words_tag[1]).casefold()):
                counts[str("^ss" + "/" + words_tag[1]).casefold()] = 0
            counts[str("^ss" + "/" + words_tag[1]).casefold()] += 1
            continue

        token = tokenize(w)
        if not words_tags.keys().__contains__(str(token + "/" + words_tag[1])):
            words_tags[str(token + "/" + words_tag[1])] = 0
        if not counts.keys().__contains__(str(token + "/" + words_tag[1]).casefold()):
            counts[str(token + "/" + words_tag[1]).casefold()] = 0
        counts[str(token + "/" + words_tag[1]).casefold()] += 1


def CreateQMLE(data_file, q_file):
    tags_dict = {}
    tags = []
    with open(data_file, "r") as f:
        data = f.read()
    data = data.split("\n")
    tags_each_row = [[] for i in range(len(data))]
    for i in range(len(data)):
        sentence = data[i].split(" ")
        if sentence != [""]:
            for j in range(len(sentence)):
                tag = sentence[j].rsplit("/", 1)
                tags_each_row[i].append(tag[1])
                if not tags.__contains__(tag[1]):
                    tags.append(tag[1])

    for i in range(len(tags_each_row)):
        for j in range(len(tags_each_row[i])):
            if j == 0:
                if not tags_dict.keys().__contains__(str("<S> <S> " + tags_each_row[i][j])):
                    tags_dict[str("<S> <S> " + tags_each_row[i][j])] = 0
                tags_dict[str("<S> <S> " + tags_each_row[i][j])] += 1

            if j == 1:
                if not tags_dict.keys().__contains__(str("<S> " + tags_each_row[i][j - 1] + " " + tags_each_row[i][j])):
                    tags_dict[str("<S> " + tags_each_row[i][j - 1] + " " + tags_each_row[i][j])] = 0
                tags_dict[str("<S> " + tags_each_row[i][j - 1] + " " + tags_each_row[i][j])] += 1

            if j >= 2:
                if not tags_dict.keys().__contains__(
                        str(tags_each_row[i][j - 2]) + " " + str(tags_each_row[i][j - 1]) + " " + str(
                                tags_each_row[i][j])):
                    tags_dict[str(tags_each_row[i][j - 2]) + " " + str(tags_each_row[i][j - 1]) + " " + str(
                        tags_each_row[i][j])] = 0
                tags_dict[str(tags_each_row[i][j - 2]) + " " + str(tags_each_row[i][j - 1]) + " " + str(
                    tags_each_row[i][j])] += 1

            if j >= 1:
                if not tags_dict.keys().__contains__(str(tags_each_row[i][j - 1]) + " " + str(tags_each_row[i][j])):
                    tags_dict[str(tags_each_row[i][j - 1]) + " " + str(tags_each_row[i][j])] = 0
                tags_dict[str(tags_each_row[i][j - 1]) + " " + str(tags_each_row[i][j])] += 1

            if not tags_dict.keys().__contains__(str(tags_each_row[i][j])):
                tags_dict[str(tags_each_row[i][j])] = 0
            tags_dict[str(tags_each_row[i][j])] += 1

            if j == len(tags_each_row[i]) - 1:
                if not tags_dict.keys().__contains__(str(tags_each_row[i][j - 1] + " " + tags_each_row[i][j] + " <E>")):
                    tags_dict[str(tags_each_row[i][j - 1] + " " + tags_each_row[i][j] + " <E>")] = 0
                tags_dict[str(tags_each_row[i][j - 1] + " " + tags_each_row[i][j] + " <E>")] += 1

    with open(q_file, "w+") as f:
        for t in tags_dict.keys():
            f.write(t + "   " + str(tags_dict.get(t)) + "\n")


if __name__ == "__main__":
    CreateEMLE(sys.argv[1], sys.argv[3])
    CreateQMLE(sys.argv[1], sys.argv[2])