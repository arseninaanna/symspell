import pickle
import os
import nltk
import numpy as np


def index_path(path):
    index = {}

    # create frequency dictionary
    with open(path, encoding="utf-8", mode="r") as f:
        for line in f:
            (key, val) = line.split()
            index[key] = val

        f.close()

    return index


def build_index(path):
    index = index_path(path)

    file_name = os.path.basename(path)
    file_name = file_name.rpartition('.')[0] + "_index"

    with open(file_name + '.p', 'wb') as wf:
        pickle.dump(index, wf, protocol=pickle.HIGHEST_PROTOCOL)


def deletes1(word):
    deletes = []
    if len(word) <= 2:
        return word
    for i in range(len(word)):
        if i == len(word) - 1:
            deletes.append(word[:i])
        else:
            deletes.append(word[:i] + word[i + 1:])

    return deletes


def deletes2(word):
    if len(word) <= 2:
        return []
    edits = deletes1(word)
    deletes = []
    for i in range(len(edits)):
        cur = deletes1(edits[i])
        for j in range(len(cur)):
            deletes.append(cur[j])

    return deletes


def deletes3(word):
    if len(word) <= 3:
        return []
    edits = deletes2(word)
    deletes = []
    for i in range(len(edits)):
        cur = deletes1(edits[i])
        for j in range(len(cur)):
            deletes.append(cur[j])

    return deletes


# this function generates symspell index with distance 2
def symspell_index(dict):
    sym_dict = {}
    for word in dict:
        edits = deletes2(word)
        for edit in edits:
            sym_dict.setdefault(edit, [])
            sym_dict[edit].append(word)

    with open('symindex.p', 'wb') as wf:
        pickle.dump(sym_dict, wf, protocol=pickle.HIGHEST_PROTOCOL)


def calculate_distance(str1, str2):
    m = len(str1)
    n = len(str2)
    distance = np.zeros((m + 1, n + 1))
    for i in range(m + 1):
        distance[i][0] = i
    for i in range(n + 1):
        distance[0][i] = i

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            fl = 0 if str1[i - 1] == str2[j - 1] else 1
            distance[i][j] = min(distance[i - 1][j - 1] + fl, distance[i - 1][j] + 1, distance[i][j - 1] + 1)

    return distance[i][j]


def check_query(text, index, sym_index):
    # get a list of words from query
    tokens = nltk.word_tokenize(text.lower())
    corrections = {}
    results = {}

    for token in tokens:
        # if token is correct
        if index.get(token) is not None:
            pass

        # if 2 deletions were made
        elif sym_index.get(token) is not None:
            words = sym_index.get(token)
            distance_checker(words, token, corrections)

        # another mistake
        else:
            insertions = deletes2(token)
            # check 2 inserts
            for ins in insertions:
                if index.get(ins) is not None:
                    corrections.setdefault(token, [])
                    corrections[token].append(ins)

            # check all the other errors
            deletes = deletes3(token) + deletes1(token) + insertions
            for delete in deletes:
                words = sym_index.get(delete)
                if words is not None:
                    distance_checker(words, token, corrections)

        # select one correction
        if corrections.get(token) is not None:
            best = best_correction(token, corrections[token], index)
            results[token] = best
    return results


def best_correction(word, corrections, index):
    min = 5
    best = ""
    for i in range(len(corrections)):
        dist = calculate_distance(corrections[i], word)
        if dist < min:
            min = dist
            best = corrections[i]
        elif dist == min:
            if index[corrections[i]] > index[best]:
                best = corrections[i]

    return best


def distance_checker(words, token, corrections):
    for word in words:
        distance = calculate_distance(word, token)
        if distance <= 4:
            corrections.setdefault(token, [])
            corrections[token].append(word)
            corrections[token] = list(set(corrections[token]))


def main():
    path = "en.txt"
    if not os.path.isfile('en_index.p'):
        build_index(path)

    with open('en_index.p', 'rb') as fp:
        index = pickle.load(fp)

    if not os.path.isfile('symindex.p'):
        symspell_index(index)

    with open('symindex.p', 'rb') as fp:
        sym_index = pickle.load(fp)

    with open("check.txt") as f:
        text = f.read()
        print(check_query(text, index, sym_index))


if __name__ == "__main__":
    main()
