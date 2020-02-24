#!/usr/bin/env python3
# coding: utf-8
import os

from nltk.stem.porter import PorterStemmer
import sys
# import chardet
#
#
# def get_encoding(file):
#     f = open(file, 'rb')
#     data = f.read()
#     return chardet.detect(data)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def tokenize_line(title):
    porter_stemmer = PorterStemmer()
    # 1)Input : "A new hi-gh for the sto-ck market?"
    # 2)Output : ["a","new","high","for","the","stock","market"]
    # remove all punctuation except "*"
    need_to_remove = r"""!"#$%&'()‘’+,-./:;<=>?@[\]^_`{|}~"""
    trantab = str.maketrans({key: None for key in need_to_remove})
    j = str.lower(title.translate(trantab))  # same as j = j.replace('single punctuation','') for many line & lower
    # print(line2)
    x = j.split()
    number_with_space = ""
    number_exist = False
    result = []
    # ADD ELEMENTS FOR EACH TITLE WITH LOGIC TO DISPOSE NUMBER WITH SPACE (EG. "607 123 4567")
    for i in x:
        if number_exist and not is_number(i):
            result.append(str(number_with_space))
            result.append(porter_stemmer.stem(i))
            number_with_space = ""
            number_exist = False
        elif not number_exist and not is_number(i):
            result.append(porter_stemmer.stem(i))
            number_exist = False
        elif is_number(i) and not number_exist:
            number_exist = True
            number_with_space = number_with_space + '' + str(i)
        elif is_number(i) and number_exist:
            number_with_space = number_with_space + '' + str(i)
    if number_exist:
        result.append(str(number_with_space))
        #     print(i)
    return result


def merge_pairs(term_list):
    dictionary = []

    for i in range(0, len(term_list)):
        t = term_list[i]  # current term
        t_exist = False

        for j in range(0, len(dictionary)):
            dic = dictionary[j]

            if dic[0] == t[0]: #if term is found in dictionary
                t_exist = True
                docId = t[1]
                #print("term " , t[0] , " exist in dictionary")
                #check if docId exist in postings list of term in dictionary
                docId_exist = False
                index = 0
                p_list = dic[2]

                #print("checking postings list")
                for i in range(0,len(p_list)):
                    dId_tf = p_list[i]
                    #print("i: " , i , "   dId_tf: ",dId_tf)
                    if docId == dId_tf[0]:
                        docId_exist = True
                        index = i
                        #print("new docId: ",docId , " exist. index: ", index)
                        break
                
                if docId_exist == True: #only increment term frequency for given docId
                    #print("increment term frequency for index: ",index)
                    dId_tf = p_list[index]
                    dId_tf = list(dId_tf)
                    #print("term: " , dic[0] , "posting: " , dic[2])
                    dId_tf[1] = dId_tf[1] + 1
                    dic[2][index] = dId_tf
                else:                  #increment document frequency, add new pair to posting list
                    #print("new docId: ",docId , " does not exist.")
                    new_pair = (docId,1)
                    #print("adding new pair: ",new_pair , " to posting")
                    dic[2].append(new_pair)
                    dic[1] = dic[1] + 1
                    #print("result for new term",dic)

                '''
                if docId in dic[2]:
                    pass
                else:
                    dic[2].append(docId)
                    dic[2].sort()
                    dic[1] = dic[1] + 1
                '''

        if not t_exist:
            #post_list = [t[1]]
            #generate pair for postings list and append new entry to dictionary in following format
            #['term',docFreq,[(docId,termFreq), ...]]
            post_list = []
            docId_termFreq = (t[1],1)
            post_list.append(docId_termFreq)

            new_row = [t[0], 1, post_list]
            
            #print("adding new ",new_row)
            dictionary.append(new_row)

    return dictionary


def generate_pair(wild):
    # Generate term-docID pairs
    term_list = []
    docID = 0

    for i in wild:
        for j in i:
            term_list.append((j, docID))
        docID += 1

    return term_list


def build_postings(term_list,wild):
    file = "postings.txt"
    if os.path.exists(file):
        os.remove(file)
    f = open(file, "a+")  # AS APPEND

    for item in term_list:
            f.write(str(item[1]) + "\t" +str(wild[item[1]].count(item[0])) + "\n")

        # f.write(item[0] + "\t" + str(item[1]) + "\n")  # USE \n TO SET EOF
    f.close()


def build_dictionary(dictionary):
    file = "dictionary.txt"
    if os.path.exists(file):
        os.remove(file)
    offset = 0
    f = open(file, "a+")  # AS APPEND
    for item in dictionary:
        f.write(item[0] + "\t" + str(item[1]) + "\t" + str(offset) + "\n")  # USE \n TO SET EOF
        offset = offset + item[1]
    f.close()


def main():
    # INPUT CHECK
    if len(sys.argv) < 2:
        print("Please input the filename U want to process! such as 'python3 Proj1.py ./filename' ")
        sys.exit()
    else:
        # READ FILE
        # f = open(sys.argv[1], encoding=get_encoding(f)) # get_encoding automatically
        f = open(sys.argv[1], encoding='utf8') # use python 3.7 or higher would detect encoding automatically when f = open(sys.argv[1])
        wild = []

        #1. Tokenize the documents. Your tokenizer should include removing special symbols and punctuations (apostrophes
        # , hyphens, periods in numbers, space between numbers, parentheses, etc.), case-folding (convert everything to
        # lower case), and stemming (you are allowed to use Porter’s stemmer). The resulting tokens will be called terms.
        for line2 in f:
            wild.append(tokenize_line(line2))

        #2. Generate (term, docID) pairs for all the terms produced by your tokenizer.
        # class tdpair:
        #         def __init__(self,term, docID):
        #                 self.term = term
        #                 self.docID = docID

        term_list = generate_pair(wild)
        print("\nTerm-docId pairs")
        for pair in term_list:
            print(pair)

        #3. Sort the (term, docID) pairs by term in alphabetic order (numbers will be treated as strings, so 22 will be sorted before 3).

        term_list.sort(key=lambda val: (val[0],val[1]))
        print("\nPairs sorted:")
        for term in term_list:
            print(term)
        #test
        # print(term_list)
        # count = 0
        # for i in term_list:
        #     print('[',i[0], " at ", i[1], ']', "\t", end = '', sep='')
        #     count+= 1
        #     if count == 8 :
        #         print()
        #         count = 0

        #4. Merge (term, docID) pairs that have the same term into a structure of the format: (term, df, postings-list), where\
        # df is the document frequency of the term and the postings-list is a sequence of the pairs of the format: (docID, tf),\
        # where tf is the term frequency of the term in the document (i.e., the number of times the term appears in the document)
        # identified by the docID. The postings list for each term is sorted in ascending docIDs.
        dictionary = merge_pairs(term_list)
        print("\nDictionary")
        for dic in dictionary:
            print(dic)

        # for i in dictionary:
        #     print(i)


        #5. Generate output. The output of this part of the project consists of two files: dictionary.txt and postings.txt. Each
        # line in dictionary.txt corresponds to one term and it has three fields: (term, df, offset), where offset refers to the
        # location of the postings list (the first line of the postings list of this term) in the postings.txt. For example, if
        # the first term in dictionary.txt has df = 2 and points to the first line in postings.txt, then the offset for this term
        # is 0; furthermore, the second term in dictionary.txt will have an offset = 2 (i.e., pointing to the third line in postings.txt)
        # because the first term has two postings (df = 2) which will use the first two lines in postings.txt. Each line in postings.txt
        # has two fields: docID and tf. If the postings list of a term has k postings, it will have k consecutive lines in postings.txt sorted by docIDs.

        build_dictionary(dictionary)

        build_postings(term_list, wild)



if __name__ == "__main__":
    main()
