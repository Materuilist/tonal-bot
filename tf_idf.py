import math
import nltk
import string
import pymorphy2
from nltk.corpus import stopwords
from youtube import get_comments
from nltk.tokenize import sent_tokenize

def flatten(t):
    return [item for sublist in t for item in sublist]

# возвращает словарь [термин]: количество упоминаний в тексте
def get_dict_of_terms(text):
    tokens = nltk.word_tokenize(text)

    tokens = [i for i in tokens if ( i not in string.punctuation )]

    stop_words = stopwords.words('english')

    morph = pymorphy2.MorphAnalyzer() 

    tokens = [morph.parse(token)[0].normal_form for token in tokens if ( token not in stop_words )]

    tokens_count_dict = {}
    for token in tokens:
        tokens_count_dict[token] = tokens.count(token)

    return tokens_count_dict

def get_dict_of_occasions(list_of_dicts):
    encounters_dict = {}
    for dict in list_of_dicts:
        for key, value in dict.items():
            if key in encounters_dict:
                encounters_dict[key] += 1
            else:
                encounters_dict[key] = 1
    return encounters_dict

# считает tf-idf для всех терминов корпуса
def compute_tf_idfs_for_corpus(corpus):
    sentences = flatten([list(sent_tokenize(comment)) for comment in corpus])
    comments_sentences = [
        {'sentence': sentence, 'tokens_dict': get_dict_of_terms(sentence)} 
        for sentence 
        in sentences
        if len(sentence) > 5
    ]
    tokens_occasions = get_dict_of_occasions([tokens_dict['tokens_dict'] for tokens_dict in comments_sentences])

    for item in comments_sentences:

        for token, count in item['tokens_dict'].items():
            tf = count / len(item['tokens_dict'])
            idf = math.log10(len(sentences) / tokens_occasions[token])
            item['tokens_dict'][token] = tf * idf

        item['weight'] = sum(item['tokens_dict'].values())

    useful_sentences =[item['sentence'] for item in sorted(comments_sentences, key=lambda x: x['weight'], reverse=True)[:3]]
    
    return '\n'.join(useful_sentences)

def get_summary(video_id):
    comments = get_comments(video_id)
    res = compute_tf_idfs_for_corpus(comments)
    print(res)
    return res