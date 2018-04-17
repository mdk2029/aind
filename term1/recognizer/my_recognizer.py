import warnings
import operator
import math
from asl_data import SinglesData


def recognize(models: dict, test_set: SinglesData):
    """ Recognize test word sequences from word models set
   :param models: dict of trained models
       {'SOMEWORD': GaussianHMM model object, 'SOMEOTHERWORD': GaussianHMM model object, ...}
   :param test_set: SinglesData object
   :return: (list, list)  as probabilities, guesses
       both lists are ordered by the test set word_id
       probabilities is a list of dictionaries where each key a word and value is Log Liklihood
           [{SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            {SOMEWORD': LogLvalue, 'SOMEOTHERWORD' LogLvalue, ... },
            ]
       guesses is a list of the best guess words ordered by the test set word_id
           ['WORDGUESS0', 'WORDGUESS1', 'WORDGUESS2',...]
   """
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    probabilities = []
    guesses = []

    for index, (X, lengths) in test_set.get_all_Xlengths().items():
        test_word_scores = dict()
        for w, m in models.items():
            try:
                test_word_scores[w] = m.score(X, lengths)
            except:
                test_word_scores[w] = -math.inf
        best_word, _ = max(test_word_scores.items(), key=operator.itemgetter(1))
        probabilities.append(test_word_scores)
        guesses.append(best_word)

    return probabilities, guesses