import math
import statistics
import itertools
import traceback
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences


class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    """

    def select(self):
        """ select the best model for self.this_word based on
            BIC score for n between self.min_n_components and self.max_n_components

            :return: GaussianHMM object
            """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        if len(self.sequences) < 5:
            return self.base_model(self.n_constant)

        best_bic = math.inf
        best_model = None

        for n_components in range(self.min_n_components, self.max_n_components+1) :

            try:
                model = self.base_model(n_components)

                if model:

                    #calculate various components of the bic
                    log_likelihood = model.score(self.X, self.lengths)

                    num_features = len(self.sequences[0][0])
                    num_transition_probs = n_components * (n_components -1)
                    num_start_probs = n_components - 1
                    num_means = n_components * num_features
                    num_variances = n_components * num_features  #"diag" covariance
                    num_parameters = num_transition_probs + num_start_probs + num_means + num_variances

                    num_datapoints = len(self.X)

                    bic = (-2 * log_likelihood) + num_parameters * math.log(num_datapoints)

                    if bic < best_bic:
                        best_bic, best_model = bic, model

            except:
                if self.verbose:
                    print("Failed to estimate bic score for n_components = {}", n_components)
                    traceback.print_exc()

        return best_model


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    https://pdfs.semanticscholar.org/ed3d/7c4a5f607201f3848d4c02dd9ba17c791fc2.pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        if len(self.sequences) < 5:
            return self.base_model(self.n_constant)

        best_dic = -np.inf
        best_model = None
        for n_components in range(self.min_n_components, self.max_n_components + 1):
            try:
                model = self.base_model(n_components)
                log_likelihood = model.score(self.X, self.lengths)
                log_likelihood_others = []

                for word in self.hwords:
                    try:
                        if word != self.this_word:
                            w_x, w_lengths = self.hwords[word]
                            log_likelihood_others.append(model.score(w_x, w_lengths))
                    except:
                        pass

                ll_others_avg = np.average(log_likelihood_others)
                dic = log_likelihood - ll_others_avg

                if dic > best_dic:
                    best_model, best_dic = model, dic
            except:
                if self.verbose:
                    print("Failure to construct base_model with n_components={} due to exception: {}", n_components, traceback.format_exc())

        return best_model


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        best_model = None
        try:
            # Find the n_component with max avg score and then
            # train on the whole dataset with n_component
            best_model = self.base_model(self.find_best_n_components())
        except:
            if self.verbose:
                print("SelectorCV cannot select best_model due to exception: {}".format(traceback.format_exc()))

        return best_model

    def find_best_n_components(self):

        # If we do not have enough data, trying to fit leads to overfitting.
        # For e.g. amongst the test words, FISH has only two samples. Attempt to fit in this case
        # leads to a model with n_components=13 which doesn't sound right
        # To avoid such issues, we bail out if we have less than 5 samples.
        if len(self.sequences) < 5:
            return self.n_constant

        split_method = KFold(n_splits=min(3, len(self.sequences)))
        best_n_component, best_score = None, -np.inf
        for n_components in range(self.min_n_components, self.max_n_components+1):
            scores = []
            if self.verbose:
                print("Beginning n_components={}".format(n_components))
            for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                train_data_word = np.array(self.sequences)[cv_train_idx]
                # train_data_word is a nested list like this:
                # [ [[1,2,3,4], [5,6,7,8]] , [[9,10,11,12]] , ...]
                flattened_train_data_word = [word for wordseq in train_data_word for word in wordseq]
                flattened_train_lengths = [len(s) for s in train_data_word]

                try:
                    hmm_model = GaussianHMM(n_components, covariance_type="diag", n_iter=5000,
                                     random_state=self.random_state, verbose=False).fit(flattened_train_data_word, flattened_train_lengths)
                except :
                    if self.verbose:
                        print("failed to construct hmm_model, exception: {}".format(traceback.format_exc()))
                    continue

                #score the model on test_data
                test_data_word = np.array(self.sequences)[cv_test_idx]
                flattened_test_data = [word for wordseq in test_data_word for word in wordseq]
                flattened_test_lengths = [len(s) for s in test_data_word]
                try:
                    score = hmm_model.score(flattened_test_data, flattened_test_lengths)
                    scores.append(score)
                except :
                    if self.verbose:
                        print("failed to score hmm_model : {}".format(traceback.format_exc()))

            if self.verbose:
                print("scores for n_components {} : {}".format(n_components,scores))

            if scores:
                avg = np.average(scores)
                if avg > best_score:
                    best_score, best_n_component = avg, n_components

        if self.verbose:
            print("Best (n_component,score)=({},{})".format(best_n_component, best_score))

        return best_n_component





























