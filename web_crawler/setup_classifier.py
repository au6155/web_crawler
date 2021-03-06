# this entire file is designed for classifier setup (training and saving for later use)
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.utils import shuffle
from text_processor import find_features, get_wordnet_pos
from web_navigator import download_article, translate_article

import nltk
import os
import pandas as pd
import random
import pickle


def download_test_articles(): # downloads articles for classifier training

    if not os.path.isdir('tekstai_classifieriui/'):  # check whether directory exists and if not - create it
        os.mkdir('tekstai_classifieriui/')

    df = pd.read_csv('su_dividendais.txt', sep = '\t', encoding = 'utf-16')   # really easy to make and use dataframe
    df = shuffle(df) # shuffle as the elements are sorted
    df = df.reset_index(drop = True) # drop initial index (stays after shuffling)
    urls = df['Nuoroda']
    about_dividends = df['Ar apie dividendus?']  # category (1 for about dividends and 0 for not about dividends)

    datafile = open(r'tekstai_classifieriui/0.txt', 'w', encoding = 'utf-16') # to keep track of how many articles have been downloaded

    for x, url in enumerate(urls):
        try:
            text, _ = download_article(url)
            text = str(about_dividends[x]) + '\n' + text # stick category in front of the article text and then save it

            with open(r'tekstai_classifieriui/%s.txt' % str(x+1), 'w', encoding = 'utf-16') as f:
                f.write(text)

            datafile.write(str(x+1) + '\n')
            print(x + 1, 'files written')
        except Exception as e:
            print(e)
            with open(r'tekstai_classifieriui/%s.txt' % str(x+1), 'w', encoding = 'utf-16') as f:
                f.write('Nepavyko parsiųsti straipsnio') # in case everything fails
        

    datafile.close()
    print('Done downloading!')


def translate_articles():  # nereikia API, nes tekstui irasyti ir nuskaityti naudojamas headless browser
    amount_of_articles = 0

    # no need to check for directory existence, because if it does not exist there is no point in creating one
    with open(r'tekstai_classifieriui/0.txt', 'r', encoding = 'utf-16') as f:
        datafile = f.readlines()
        amount_of_articles = int(datafile[-1])

    for x in range(1, amount_of_articles + 1):
        with open(r'tekstai_classifieriui/%s.txt' % x, 'r', encoding = 'utf-16') as f:
            text_to_translate = f.read()

        # just removing some dots so that the computer does not think that they mark the end of a sentence
        while 'mln.' in text_to_translate:
            text_to_translate = text_to_translate.replace('mln.', 'mln')
        while 'mlrd.' in text_to_translate:
            text_to_translate = text_to_translate.replace('mlrd.', 'mlrd')
        while 'tūkst.' in text_to_translate:
            text_to_translate = text_to_translate.replace('tūkst.', 'tūkst')

        # category and actual text are split
        category = text_to_translate[:text_to_translate.find('\n')]
        text_to_translate = text_to_translate[text_to_translate.find('\n')+1:]

        translated_text = translate_article(text_to_translate)

        with open(r'tekstai_classifieriui/%s_en.txt'%x, 'w', encoding = 'utf-16') as f:
            f.write(category + '\n' + translated_text)        
        print(x, 'articles translated')


def get_featuresets():

    if not os.path.isdir('tekstai_classifieriui/'):
        os.mkdir('tekstai_classifieriui/')
    
    with open(r'tekstai_classifieriui/0.txt', 'r', encoding = 'utf-16') as f:
        datafile = f.readlines()
        amount_of_articles = int(datafile[-1])

    documents = []
    all_words = []
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()


    for x in range(1, amount_of_articles + 1):
        with open(r'tekstai_classifieriui/%s_en.txt' % x, 'r', encoding = 'utf-16') as f:
            text = f.read()
        
        category = text[:text.find('\n')]
        text = text[text.find('\n')+1:]

        if category == '1':
            category = 'div' # for dividends
        else:
            category = 'nodiv' # for no dividends

        # text is split into words and part of speech is marked for each word
        words = word_tokenize(text)
        tagged = nltk.pos_tag(words)

        for m, word_and_tag in enumerate(tagged):
            word, part_of_speech = word_and_tag

            # for some reason the word 'thousand' is not recognized as cardinal digit (unlike 'million' or 'billion') by the algorithm, so we help it a little bit
            if word == 'thousand':
                part_of_speech = 'CD'

            w = lemmatizer.lemmatize(word, get_wordnet_pos(part_of_speech)) # word is turned back into its original (simplified) form
            # check if the word has any meaning at all (or if it is a word at all)
            if w not in stop_words:
                if w not in """,...()'":-;''s``""":
                    words[m] = w
                    all_words.append(w.lower())

        documents.append((list(words), category))

    random.shuffle(documents)

    all_words = nltk.FreqDist(all_words)  # words and times they repeat in all_words array
    all_words = all_words.most_common(1000) # grab 1000 most common words and make up featureset out of them

    word_features = []
    for w in all_words:
        word_features.append(w[0])

    # save the words so they can be quickly grabbed later
    pickle_out = open('word_features.pickle', 'wb')
    pickle.dump(word_features, pickle_out)
    pickle_out.close()
    print('Word features has been saved')

    featuresets = []
    for article, category in documents:
        featuresets.append((find_features(article, word_features), category))  # create actual featureset

    return featuresets

def train_classfier(sets_of_featuresets):

    length = len(sets_of_featuresets)
    train_test_split = 0.75  # what fraction of total data goes to training
    split = int(train_test_split * length)

    train_set = sets_of_featuresets[:split]
    test_set = sets_of_featuresets[split + 1:]
    
    print('Train set length:', len(train_set))
    print('Test set length:', len(test_set))

    classifier = nltk.NaiveBayesClassifier.train(train_set) # Naive Bayes classifier object initialized

    accuracy = (nltk.classify.accuracy(classifier, test_set)) * 100
    print("Classifier accuracy percent:", accuracy, '\n')
    classifier.show_most_informative_features(50)

    return classifier


def main():
    download_test_articles()
    translate_articles()
    featuresets = get_featuresets()
    classifier = train_classfier(featuresets)

    # classifier saved for later use in actual data collection
    pickle_out = open('classifier.pickle', 'wb')
    pickle.dump(classifier, pickle_out)
    pickle_out.close()
    

main()


