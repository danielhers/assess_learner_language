
# built in packages
from itertools import islice
import math
import re
import sys
import os
import csv
from collections import Counter

# dependencies
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import distance
import json
from scipy.stats import spearmanr
# import scikits.statsmodels as sm
# from statsmodels.distributions.empirical_distribution import ECDF

from nltk.tokenize import sent_tokenize as nltk_sent_tokenize
from nltk.stem import WordNetLemmatizer

# ucca
UCCA_DIR = '/home/borgr/ucca/ucca'
ASSESS_DIR = os.path.dirname(os.path.realpath(__file__)) + os.sep
# TUPA_DIR = '/cs/labs/oabend/borgr/tupa'
# UCCA_DIR = TUPA_DIR + '/ucca'
sys.path.append(UCCA_DIR + '/scripts/distances')
sys.path.append(UCCA_DIR + '/ucca')
sys.path.append(UCCA_DIR)
import align

# constants
lemmatizer = WordNetLemmatizer()
ENDERS_DEFINITELY = r"\?\!\;"
ENDERS = r"\." + ENDERS_DEFINITELY
SENTENCE_NOT_END = "[^" + ENDERS + "]"
SENTENCE_END = "[" + ENDERS + "]"
NOT_ABBREVIATION_PATTERN = re.compile(r"(.*?\s+\w\s*\.)(\s*\w\w.*)")
SENTENCE_DEFINITELY_PATTERN = re.compile(
    r"(.+\s*[" + ENDERS_DEFINITELY + r"]\s*)(.+)")
SENTENCE_ENDS_WITH_NO_SPACE_PATTERN = re.compile(
    "(.*?\w\w" + SENTENCE_END + ")(\w+[^\.].*)")
SPACE_BEFORE_SENTENCE_PATTERN = re.compile(
    "(.*?\s" + SENTENCE_END + "(\s*\")?)(.*)")
SPECIAL_WORDS_PATTERNS = [re.compile(r"i\s*\.\s*e\s*\.", re.IGNORECASE), re.compile(
    r"e\s*\.\s*g\s*\.", re.IGNORECASE), re.compile(r"\s+c\s*\.\s+", re.IGNORECASE)]
SPECIAL_WORDS_REPLACEMENTS = ["ie", "eg", " c."]
MAX_SENTENCES = 1400  # accounts for the maximum number of lines to get from the database
MAX_DIST = 2
SHORT_WORD_LEN = 4
CHANGING_RATIO = 5
PATH = ASSESS_DIR + r"/data/paragraphs/"

SARI = "sari"
MAX = "max"
BLEU = "BLEU"
SIMPLIFICATION_MEASURES = [SARI, BLEU, MAX]

ORDERED = "original order"
FIRST_LONGER = "sentence splitted"
SECOND_LONGER = "sentence concatenated"
ORDERED_ALIGNED = "ORDERED with align"
FIRST_LONGER_ALIGNED = "first longer with align"
SECOND_LONGER_ALIGNED = "second longer with align"
REMOVE_LAST = "remove last"
PARAGRAPH_END = "paragraph end"
COMMA_REPLACE_FIRST = ", in second sentence became the end of a new sentence (first longer)"
COMMA_REPLACE_SECOND = ", in first sentence became the end of a new sentence (second longer)"
NO_ALIGNED = ""
trial_name = ""


def main():
    # UCCASim_conservatism()
    # outputs_conservatism()
    ranking_conservatism()
    # reranking_simplification_conservatism("moses")
    # reranking_simplification_conservatism()
    # reranking_simplification_conservatism("moses", measure=MAX)
    # reranking_simplification_conservatism(measure=MAX)
    # reranking_simplification_conservatism("moses", measure=BLEU)
    # reranking_simplification_conservatism(measure=BLEU)


def outputs_conservatism():
    change_date = "160111"
    filename = "results/results" + change_date + ".json"
    learner_file = "conll.tok.orig"
    ACL2016RozovskayaRothOutput_file = "conll14st.output.1cleaned"
    char_based_file = "filtered_test.txt"
    JMGR_file = "JMGR"
    amu_file = "AMU"
    cuui_file = "CUUI"
    iitb_file = "IITB"
    ipn_file = "IPN"
    nthu_file = "NTHU"
    pku_file = "PKU"
    post_file = "POST"
    rac_file = "RAC"
    sjtu_file = "SJTU"
    ufc_file = "UFC"
    umc_file = "UMC"
    camb_file = "CAMB"
    gold_file = "corrected_official-2014.0.txt.comparable"
    from fce import CORRECTED_FILE as fce_gold_file
    from fce import LEARNER_FILE as fce_learner_file
    autocorrect = read_paragraph(ACL2016RozovskayaRothOutput_file)
    char_based = read_paragraph(char_based_file)
    jmgr = read_paragraph(JMGR_file)
    amu = read_paragraph(amu_file)
    camb = read_paragraph(camb_file)
    cuui = read_paragraph(cuui_file)
    iitb = read_paragraph(iitb_file)
    ipn = read_paragraph(ipn_file)
    nthu = read_paragraph(nthu_file)
    pku = read_paragraph(pku_file)
    post = read_paragraph(post_file)
    rac = read_paragraph(rac_file)
    sjtu = read_paragraph(sjtu_file)
    ufc = read_paragraph(ufc_file)
    umc = read_paragraph(umc_file)
    origin = read_paragraph(learner_file, preprocess_paragraph)
    gold = read_paragraph(gold_file, preprocess_paragraph_minimal)
    fce_gold = read_paragraph(fce_gold_file)
    fce_learner = read_paragraph(fce_learner_file)
    fce_learner_full = read_paragraph(
        fce_learner_file, preprocess_paragraph_minimal)
    fce_gold_full = read_paragraph(fce_gold_file, preprocess_paragraph_minimal)
    res_list = []
    old_res = read(filename) if filename else {}
    for (name, res) in old_res.items():
        res.append(name)
        dump(res_list, filename)

    # # compare fce origin to fce gold without matching
    # name = "fce"
    # print(name)
    # if name not in old_res:
    #   broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(fce_learner_full, fce_gold_full, sent_token_by_char, sent_token_by_char)
    #   res_list.append((broken, words_differences, index_differences, spearman_differences, aligned_by, name))
    #   dump(res_list, filename)
    # else:
    #   res_list.append(old_res[name])

    # # compare fce origin to fce gold
    # name = "fce auto"
    # print(name)
    # if name not in old_res:
    #   broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(fce_learner, fce_gold)
    #   res_list.append((broken, words_differences, index_differences, spearman_differences, aligned_by, name))
    #   dump(res_list, filename)
    # else:
    #   res_list.append(old_res[name])

    # compare gold to origin
    name = "gold"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, gold, sent_tokenize_default, sent_token_by_char)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        print(len(old_res[name][1]))
        broken, word_differences, index_differences, spearman_differences, aligned_by, name = old_res[
            name]
        origin_sentences = list(get_sentences_from_endings(origin, broken[0]))
        corrected_sentences = list(get_sentences_from_endings(gold, broken[1]))
        res_list.append(old_res[name])
        # print("\nmany words changed")
        # for i, dif in enumerate(word_differences):
        #   if dif > 10: # or i < 3 # use i to print some, use diff to print all sentences which differ ion more than "diff" words from each other
        #       print("-------\nsentences:\n", corrected_sentences[i],"\norignal:\n", origin_sentences[i])
        #       print ("word dif:", dif)
        #       print("match num:", i)
        # print("\nmany indexes changed")
        # for i, dif in enumerate(index_differences):
        #   if dif > 10: # or i < 3 # use i to print some, use diff to print all sentences which differ ion more than "diff" words from each other
        #       print("-------\nsentences:\n", corrected_sentences[i],"\norignal:\n", origin_sentences[i])
        #       print ("word dif:", dif)
        #       print("match num:", i)
        # print("\nmany swaps changed (spearman)")
        # for i, dif in enumerate(spearman_differences):
        #   if dif < 0.9: # or i < 3 # use i to print some, use diff to print all sentences which differ ion more than "diff" words from each other
        #       print("-------\nsentences:\n", corrected_sentences[i],"\norignal:\n", origin_sentences[i])
        #       print ("word dif:", dif)
        #       print("match num:", i)
    # print(len(origin_sentences), len(corrected_sentences), len(word_differences))

    # compare origin to cuui #1
    name = "cuui"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, cuui)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to camb #2
    name = "camb"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, camb)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to AMU #3
    name = "amu"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, amu)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to ACL2016RozovskayaRoth autocorrect
    name = "Rozovskaya Roth"
    name = "RoRo"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, autocorrect)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    name = "jmgr"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, jmgr)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to Char_based_file
    name = "Char"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, char_based)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to rac
    name = "rac"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, rac)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to umc
    name = "umc"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, umc)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to sjtu
    name = "sjtu"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, sjtu)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to iitb
    name = "iitb"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, iitb)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to ipn
    name = "ipn"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, ipn)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to nthu
    name = "nthu"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, nthu)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to pku
    name = "pku"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, pku)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to post
    name = "post"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, post)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])

    # compare origin to ufc
    name = "ufc"
    print(name)
    if name not in old_res:
        broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
            origin, ufc)
        res_list.append((broken, words_differences, index_differences,
                         spearman_differences, aligned_by, name))
        dump(res_list, filename)
    else:
        res_list.append(old_res[name])
    dump(res_list, filename)
    plot_comparison(res_list)
    convert_file_to_csv(filename)


def reranking_simplification_conservatism(k_best="nisioi", measure=SARI):
    change_date = "011126"
    if measure == MAX:
        complex_file = "simplification_rank_results_" + "max_" + k_best + "_origin"
        filename = "results/simplification_reranking_results" + \
            "max_" + k_best + change_date + ".json"
    if measure == BLEU:
        complex_file = "simplification_rank_results_" + "BLEU" + k_best + "_origin"
        filename = "results/" + "simplification_reranking_results_" + "BLEU" + \
            k_best + change_date + ".json"
    if measure == SARI:
        complex_file = "simplification_rank_results_" + k_best + "_origin"
        filename = "results/simplification_reranking_results" + \
            k_best + change_date + ".json"

    (path, dirs, files) = next(os.walk(PATH))
    filenames = []
    names = []
    # filenames.append("test.8turkers.tok.simp")
    # names.append("gold")
    for fl in files:
        if "simplification" in fl and "origin" not in fl and k_best in fl:
            if (measure == SARI and (all(measure not in fl for measure in SIMPLIFICATION_MEASURES))) or measure in fl:
                filenames.append(fl)
                names.append(fl[-5:])
                if "gold" in fl:
                    names[-1] = "gold"
    argsort = np.argsort(names)
    names = np.array(names)[argsort]
    filenames = np.array(filenames)[argsort]
    origin = read_text(complex_file)
    compare(filenames, names, filename, origin,
            read_text, compare_aligned_paragraphs)


def ranking_conservatism():
    change_date = "170531"
    filename = "results/reranking_results" + change_date + ".json"
    all_file = "first_rank_resultsALL"
    BN_file = "first_rank_resultsBN"
    # NUCLEA_file = "first_rank_resultsNUCLEA"
    # NUCLE_file = "first_rank_resultsNUCLE"
    (path, dirs, files) = next(os.walk(PATH))
    filenames = []
    nums = []
    for fl in files:
        if "subset" in fl:
            filenames.append(fl)
    names = [name[18:].replace("subset", " refs") for name in filenames]
    for name in names:
        if name[1].isdigit():
            nums.append(int(name[:2]))
        else:
            nums.append(int(name[0]))
    nums = nums + [15, 10]  # , 2, 1]
    filenames = filenames + [all_file, BN_file]  # , NUCLE_file, NUCLEA_file]
    names = names + ["all", "BN"]  # , "NUCLE", "NUCLEA"]
    argsort = np.argsort(nums)
    names = np.array(names)
    filenames = np.array(filenames)
    names = names[argsort]
    filenames = filenames[argsort]
    print(names, filenames)

    learner_file = "conll.tok.orig"
    origin = read_paragraph(learner_file, preprocess_paragraph)
    compare(filenames, names, filename, origin)


def UCCASim_conservatism():
    change_date = "170531"
    all_file = "first_rank_resultsALL"
    NUCLEA_file = "first_rank_resultsNUCLEA"
    ACL2016RozovskayaRothOutput_file = "conll14st.output.1cleaned"
    base_rerank = "uccasim_rank_results"
    filenames = [all_file, ACL2016RozovskayaRothOutput_file, NUCLEA_file] + \
        [str(base) + "_" + base_rerank for base in np.linspace(0, 1, 11)]
    names = ["all", "RoRo", "NUCLEA"] + \
        [str(base) + "combined" for base in np.linspace(0, 1, 11)]
    filename = "results/ucca_reranking_results" + change_date + ".json"

    learner_file = "conll.tok.orig"
    origin = read_paragraph(learner_file, preprocess_paragraph)
    compare(filenames, names, filename, origin)


###########################################################
####                    GENEERAL NLP                    ###
###########################################################


def is_word(w):
    return True if w != align.EMPTY_WORD and re.search('\w', w) else False


def split_by_pattern(tokens, p, first=1, second=2):
    """ gets a list of tokens and splits tokens by a compiled regex pattern
            param:
            tokens - list of strings representing sentence or sentences
            p - compiled regex pattern or object containing method match() that returns match object
            first - the group number that represents the first token found
            second - the group number that represents the second token found"""

    res = []
    for i, token in enumerate(tokens):
        matched = p.match(token)
        while matched:
            assert(matched.group(first) + matched.group(second) == token)
            res.append(matched.group(first))
            token = matched.group(second)
            matched = p.match(token)
        if token.strip():
            res.append(token)
    return res


def concat_empty(tokens):
    """concatenats empty sentences or words to the one before them in the list of tokens"""
    result = []
    for token in tokens:
        if re.search(r"[A-Za-z][A-Za-z]", token) is not None:
            result.append(token)
        elif result:
            result[-1] = result[-1] + token
    return result


def sent_token_by_char(s, char="\n"):
    """tokenizes by predefined charachter"""
    return concat_empty(s.split(char))


def sent_tokenize_default(s):
    """tokenizes a text to a list of sentences"""
    tokens = nltk_sent_tokenize(s)
    tokens = split_by_pattern(tokens, SENTENCE_DEFINITELY_PATTERN)
    tokens = split_by_pattern(tokens, SENTENCE_ENDS_WITH_NO_SPACE_PATTERN)
    tokens = split_by_pattern(tokens, SPACE_BEFORE_SENTENCE_PATTERN, 1, 3)
    tokens = split_by_pattern(tokens, NOT_ABBREVIATION_PATTERN)

    return concat_empty(tokens)


def word_tokenize(s):
    """tokenizes a sentence to words list"""
    res = [w for w in align.word_tokenize(s) if is_word(w)]
    return res


def preprocess_paragraph_minimal(p):
    if p[-1] == "\n":
        p = p[:-1]
    return p


def preprocess_paragraph(p):
    """preprocesses a paragraph"""
    for i, pattern in enumerate(SPECIAL_WORDS_PATTERNS):
        p = re.sub(pattern, SPECIAL_WORDS_REPLACEMENTS[i], p)
    # p = re.sub(r"\s+\.\s+", r".", p)
    p = re.sub(r"(" + SENTENCE_NOT_END + ")(\s*\n)", r"\1.\2", p)
    p = re.sub("(\.\s*['\"])\s*\.", r"\1", p)
    p = re.sub(r"\s+", r" ", p)
    p = re.sub(r"(" + SENTENCE_END + r"\s*)" + SENTENCE_END, r"\1", p)
    return p


def preprocess_word(w):
    if w and not w[-1].isalnum():
        w = w[:-1]
    return align.preprocess_word(w)


def approximately_same_word(w1, w2):
    """ returns if both words are considered the same word with a small fix or not"""
    l1 = lemmatizer.lemmatize(w1)
    l2 = lemmatizer.lemmatize(w2)
    allowed_dist = MAX_DIST if len(
        l1) > SHORT_WORD_LEN and len(l2) > SHORT_WORD_LEN else 1
    if (distance.levenshtein(l1, l2) > allowed_dist or
            w1 == align.EMPTY_WORD or w2 == align.EMPTY_WORD):
        # suggestion: should "the" "a" etc be considered in a different way?
        # maybe they should not but not in this function
        return False  # suggestion: words such as in at on etc, might be considered all equal to each other and to the empty_word for our purpose
    return True


def _choose_ending_position(sentences, endings, i):
    """ i - sentence number
            sentences - list of sentences
            endings - list of sentences positions endings

            return position, last word in the i'th sentence"""
    for word in reversed(word_tokenize(sentences[i])):
        word = preprocess_word(word)
        if len(word) > 1:
            return endings[i], word
    print("sentence contains no words:\n\"", sentences[i], "\"")
    print("sentence before", sentences[i - 1])
    print("sentence after", sentences[i + 1])
    assert(False)
    return endings[i], preprocess_word(word_tokenize(sentences[i])[-1])


def index_diff(s1, s2):
    """ counts the number of not aligned words in 2 sentences"""
    alignment, indexes = align_sentence_words(s1, s2, True)
    sorted_alignment_indexes = [(w1, w2, i1, i2)
                                for (w1, w2), (i1, i2) in zip(alignment, indexes)]
    sorted_alignment_indexes = sorted(
        sorted_alignment_indexes, key=lambda x: x[3])
    last = -1
    res = 0

    for w1, w2, i1, i2 in sorted_alignment_indexes:
        if is_word(w1) and is_word(w2):
            if i1 < last:
                assert (i1 != -1 and i2 != -1)
                res += 1
            last = i1
    return res


def spearman_diff(s1, s2):
    """ counts the number of not aligned words in 2 sentences"""
    alignment, indexes = align_sentence_words(s1, s2, True)
    sorted_alignment_indexes = [(w1, w2, i1, i2)
                                for (w1, w2), (i1, i2) in zip(alignment, indexes)]
    sorted_alignment_indexes = sorted(
        sorted_alignment_indexes, key=lambda x: x[3])
    changes = 0
    indexes1 = []
    indexes2 = []
    for w1, w2, i1, i2 in sorted_alignment_indexes:
        if is_word(w1) and is_word(w2):
            indexes1.append(i1)
            indexes2.append(i2)
    indexes1 = np.asarray(indexes1)
    indexes2 = np.asarray(indexes2)
    return spearmanr(indexes1, indexes2)


def word_diff(s1, s2):
    """ counts the number of aligned words that are not considered approximately the same word in 2 sentences"""
    alignment, indexes = align_sentence_words(s1, s2, True)
    return sum(not approximately_same_word(preprocess_word(w1), preprocess_word(w2)) for i, (w1, w2) in enumerate(alignment) if is_word(w1) or is_word(w2))


def diff_words(s1, s2):
    """ returns the aproximately different words in the two sentences"""
    alignment, indexes = align_sentence_words(s1, s2, True)
    return [(w1, w2) for i, (w1, w2) in enumerate(alignment) if (is_word(w1) or is_word(w2)) and not approximately_same_word(preprocess_word(w1), preprocess_word(w2))]


def calculate_endings(sentences, paragraph):
    """ gets sentences splitted from a paragraph and returns the sentences endings positions"""
    current = 0
    endings = []
    for s in sentences:
        current += len(s)
        while current < len(paragraph) and not paragraph[current].isalnum():
            current += 1
        endings.append(current)
    return endings


def align_sentence_words(s1, s2, isString, empty_cache=False):
    """aligns words from sentence s1 to s2m, allows caching
            returns arrays of word tuplds and indexes tuples"""
    if empty_cache:
        align_sentence_words.cache = {}
        return
    if (s1, s2, isString) in align_sentence_words.cache:
        return align_sentence_words.cache[(s1, s2, isString)]
    elif (s2, s1, isString) in align_sentence_words.cache:
        return align_sentence_words.cache[(s2, s1, isString)]
    else:
        res = align.align(s1, s2, isString)
        align_sentence_words.cache[(s2, s1, isString)] = res
        return res
align_sentence_words.cache = {}


###########################################################
####                    WORDS CHANGED                   ###
###########################################################


def aligned_ends_together(shorter, longer, reg1, reg2, addition="", force=False):
    """ checks if two sentences, ending in two regularized words ends at the same place.
    """
    sentence1 = shorter
    sentence2 = longer + addition
    addition_words = word_tokenize(addition) if addition else word_tokenize(longer)[
        len(word_tokenize(shorter)):]
    addition_words = set(preprocess_word(w) for w in addition_words)
    tokens1 = [preprocess_word(w) for w in word_tokenize(sentence1)]
    tokens2 = [preprocess_word(w) for w in word_tokenize(sentence2)]
    count1 = Counter()
    # if words appear more than once make each word unique by order of
    # appearence
    for i, token in enumerate(tokens1):
        if count1[token] > 0:
            tokens1[i] = str(count1[token]) + token
        if is_word(token):
            count1.update(token)
    count2 = Counter()
    for i, token in enumerate(tokens2):
        if count2[token] > 0:
            tokens2[i] = str(count2[token]) + token
        if is_word(token):
            count2.update(token)
    slen1 = len(tokens1)
    slen2 = len(tokens2)
    if abs(slen1 - slen2) > min(slen1, slen2) / CHANGING_RATIO:
        return False

    aligned, indexes = align_sentence_words(sentence1, sentence2, True)
    aligned = set(
        map(lambda x: (preprocess_word(x[0]), preprocess_word(x[1])), aligned))
    mapping = dict(aligned)
    rev = dict(align.reverse_mapping(aligned))
    empty = preprocess_word(align.EMPTY_WORD)

    if force or ((reg1, empty) in aligned):
        if approximately_same_word(reg2, rev[reg2]):
            return True
    if force or ((empty, reg2) in aligned):
        if approximately_same_word(reg1, mapping[reg1]):
            return True
    return False


def break2common_sentences(p1, p2, sent_tokenize1, sent_tokenize2):
    """finds the positions of the common sentence ending

    Breaking is done according to the text of both passages
    returns two lists each containing positions of sentence endings
    guarentees same number of positions is acquired and the last position is the passage end
    return:
            positions1, positions2 - lists of indexes of the changed """
    aligned_by = []
    s1 = sent_tokenize1(p1)
    s2 = sent_tokenize2(p2)

    # calculate sentence endings positions
    endings1 = calculate_endings(s1, p1)
    endings2 = calculate_endings(s2, p2)

    # find matching endings to match
    positions1 = []
    positions2 = []
    i = 0
    j = 0
    inc = False
    force = False
    while i < len(s1) and j < len(s2):
        one_after1 = "not_initialized"
        one_after2 = "not_initialized"

        # create a for loop with two pointers
        if inc:
            i += 1
            j += 1
            inc = False
            continue

        inc = True
        position1, reg1 = _choose_ending_position(s1, endings1, i)
        position2, reg2 = _choose_ending_position(s2, endings2, j)
        if approximately_same_word(reg1, reg2):

            aligned_by.append(ORDERED)
            positions1.append(position1)
            positions2.append(position2)
            continue

        # deal with addition or subtraction of a sentence ending
        slen1 = len(word_tokenize(s1[i]))
        slen2 = len(word_tokenize(s2[j]))

        if i + 1 < len(s1) and slen1 < slen2:
            pos_after1, one_after1 = _choose_ending_position(
                s1, endings1, i + 1)
            if approximately_same_word(one_after1, reg2):
                aligned_by.append(FIRST_LONGER)
                positions1.append(pos_after1)
                positions2.append(position2)
                i += 1
                continue

        if j + 1 < len(s2) and slen2 < slen1:
            pos_after2, one_after2 = _choose_ending_position(
                s2, endings2, j + 1)
            if approximately_same_word(reg1, one_after2):
                aligned_by.append(SECOND_LONGER)
                positions1.append(position1)
                positions2.append(pos_after2)
                j += 1
                continue

        # no alignment found with 2 sentences
        # check if a word was added to the end of one of the sentences
        if aligned_ends_together(s1[i], s2[j], reg1, reg2):
            aligned_by.append(ORDERED_ALIGNED)
            positions1.append(position1)
            positions2.append(position2)
            continue

        # if no match is found twice and we had ORDERED match, it might have
        # been a mistake
        if (positions1 and positions2 and
                aligned_by[-1] == NO_ALIGNED and aligned_by[-2] == NO_ALIGNED):
            removed_pos1 = positions1.pop()
            removed_pos2 = positions2.pop()
            aligned_by.append(REMOVE_LAST)
            i -= 3
            j -= 3
            position1, reg1 = _choose_ending_position(s1, endings1, i)
            position2, reg2 = _choose_ending_position(s2, endings2, j)
            pos_after1, one_after1 = _choose_ending_position(
                s1, endings1, i + 1)
            pos_after2, one_after2 = _choose_ending_position(
                s2, endings2, j + 1)
            pos_2after1, two_after1 = _choose_ending_position(
                s1, endings1, i + 2)
            pos_2after2, two_after2 = _choose_ending_position(
                s2, endings2, j + 2)
            force = True

        # check if a word was added to the end of one of the sentences
        # Also, deal with addition or subtraction of a sentence ending
        if i + 1 < len(s1) and slen1 < slen2:
            if aligned_ends_together(s2[j], s1[i], reg2, one_after1, addition=s1[i + 1], force=force):
                aligned_by.append(FIRST_LONGER_ALIGNED)
                positions1.append(pos_after1)
                positions2.append(position2)
                i += 1
                continue

        if j + 1 < len(s2) and slen2 < slen1:
            if aligned_ends_together(s1[i], s2[j], reg1, one_after2, addition=s2[j + 1], force=force):
                aligned_by.append(SECOND_LONGER_ALIGNED)
                positions1.append(position1)
                positions2.append(pos_after2)
                j += 1
                continue

        # removing last yielded no consequences keep in regular way
        if aligned_by[-1] == REMOVE_LAST:
            # try 3 distance
            if i + 2 < len(s1) and slen1 < slen2:
                if aligned_ends_together(s2[j], s1[i], reg2, two_after1, addition=s1[i + 1] + s1[i + 2], force=force):
                    aligned_by.append(FIRST_LONGER_ALIGNED)
                    aligned_by.append(FIRST_LONGER_ALIGNED)
                    positions1.append(pos_2after1)
                    positions2.append(position2)
                    i += 2
                    continue
            if j + 2 < len(s2) and slen2 < slen1:
                if aligned_ends_together(s1[i], s2[j], reg1, two_after2, addition=s2[j + 1] + s2[j + 2], force=force):
                    aligned_by.append(SECOND_LONGER_ALIGNED)
                    aligned_by.append(SECOND_LONGER_ALIGNED)
                    positions1.append(position1)
                    positions2.append(pos_2after2)
                    j += 2
                    continue
            # fallback was unnecesary
            positions1.append(removed_pos1)
            positions2.append(removed_pos2)
            i += 2
            j += 2

        # check if a , was replaced by a sentence ender
        if positions1 and slen2 < slen1:
            splitter = reg2 + ","
            comma_index = s1[i].find(splitter)
            if comma_index == -1:
                splitter = reg2 + " ,"
                comma_index = s1[i].find(splitter)
            if comma_index != -1:
                comma_index += len(splitter)
                aligned_by.append(COMMA_REPLACE_SECOND)
                positions1.append(positions1[-1] + comma_index)
                positions2.append(position2)
                s1 = s1[:i] + [s1[i][:comma_index],
                               s1[i][comma_index:]] + s1[i + 1:]
                endings1 = endings1[
                    :i] + [endings1[i - 1] + comma_index] + endings1[i:]
                continue
        if positions2 and slen1 < slen2:
            splitter = reg1 + ","
            comma_index = s2[j].find(splitter)
            if comma_index == -1:
                splitter = reg1 + " ,"
                comma_index = s2[j].find(splitter)
            if comma_index != -1:
                comma_index += len(splitter)
                aligned_by.append(COMMA_REPLACE_FIRST)
                positions2.append(positions2[-1] + comma_index)
                positions1.append(position1)
                s2 = s2[:j] + [s2[j][:comma_index],
                               s2[j][comma_index:]] + s2[j + 1:]
                endings2 = endings2[
                    :j] + [endings2[j - 1] + comma_index] + endings2[j:]
                continue

        aligned_by.append(NO_ALIGNED)

    # add last sentence in case skipped
        position1, reg1 = _choose_ending_position(s1, endings1, -1)
        position2, reg2 = _choose_ending_position(s2, endings2, -1)
    if (not positions1) or (not positions2) or (
            positions1[-1] != position1 and positions2[-1] != position2):
        positions1.append(endings1[-1])
        positions2.append(endings2[-1])
        aligned_by.append(PARAGRAPH_END)
    elif positions1[-1] != position1 and positions2[-1] == position2:
        positions1[-1] = endings1[-1]
        aligned_by.append(PARAGRAPH_END)
    elif positions1[-1] == position1 and positions2[-1] != position2:
        positions2[-1] = endings2[-1]
        aligned_by.append(PARAGRAPH_END)

    return positions1, positions2, aligned_by


def get_sentences_from_endings(paragraph, endings):
    """a generator of sentences from a paragraph and ending positions in it"""
    last = 0
    for cur in endings:
        yield paragraph[last:cur]
        last = cur


def calculate_conservatism(origin_sentences, corrected_sentences):
    print("calculating conservatism")
    index_differences = [index_diff(orig, cor) for orig, cor in zip(
        origin_sentences, corrected_sentences)]
    spearman_differences = [spearman_diff(orig, cor)[0] for orig, cor in zip(
        origin_sentences, corrected_sentences)]
    word_differences = [word_diff(orig, cor) for orig, cor in zip(
        origin_sentences, corrected_sentences)]
    print("comparing done, printing interesting results")
    for i, dif in enumerate(word_differences):
        if dif > 10:  # or i < 3 # use i to print some, use diff to print all sentences which differ ion more than "diff" words from each other
            print("-------\nsentences:\n",
                  corrected_sentences[i], "\norignal:\n", origin_sentences[i])
            print("word dif:", dif)
            print("match num:", i)
    # for i, dif in enumerate(index_differences):
    #     if dif > 10:  # or i < 3 # use i to print some, use diff to print all sentences which differ ion more than "diff" words from each other
    #         print("-------\nsentences:\n",
    #               corrected_sentences[i], "\norignal:\n", origin_sentences[i])
    #         print("word dif:", dif)
    #         print("match num:", i)
    return word_differences, index_differences, spearman_differences


def compare_aligned_paragraphs(origin, corrected, break_sent1=sent_token_by_char, break_sent2=sent_token_by_char):
    origin_sentences = break_sent1(origin)
    corrected_sentences = break_sent2(corrected)
    broken1 = [i for i, char in enumerate(origin) if char == "\n"]
    broken2 = [i for i, char in enumerate(corrected) if char == "\n"]

    word_differences, index_differences, spearman_differences = calculate_conservatism(
        origin_sentences, corrected_sentences)
    assert len(origin_sentences) == len(corrected_sentences)
    return [broken1, broken2], word_differences, index_differences, spearman_differences, [ORDERED_ALIGNED] * len(origin_sentences)


def compare_paragraphs(origin, corrected, break_sent1=sent_tokenize_default, break_sent2=sent_tokenize_default):
    """ compares two paragraphs
            return:
            broken - the sentence endings indexes
            differences - difference measures corresponding to the indexes in broken
            aligned_by - the way the sentences were aligned"""
    print("comparing paragraphs")
    align_sentence_words(None, None, None, True)
    print("aligning sentences")
    broken = [None, None]
    broken[0], broken[1], aligned_by = break2common_sentences(
        origin, corrected, break_sent1, break_sent2)
    print("assesing differences")
    origin_sentences = list(get_sentences_from_endings(origin, broken[0]))
    corrected_sentences = list(
        get_sentences_from_endings(corrected, broken[1]))
    # print(corrected_sentences)
    word_differences, index_differences, spearman_differences = calculate_conservatism(
        origin_sentences, corrected_sentences)
    return broken, word_differences, index_differences, spearman_differences, aligned_by


def preprocess_simplification(s):
    s = s.replace("-rrb-", " ")
    s = s.replace("-lrb-", "")
    s = s.replace("&quot", '"')
    s = s.replace("&apos", "'")
    s = re.sub(r"[ \t]+", r" ", s)
    return s


def read_text(filename, process=preprocess_simplification):
    with open(PATH + filename, "r") as fl:
        return process(fl.read())


def read_paragraph(filename, process=preprocess_paragraph):
    with open(PATH + filename) as fl:
        return process("".join(islice(fl, MAX_SENTENCES)))


def extract_aligned_by_dict(a):
    """ takes aligned_by list and creates a counter of ordered, first longer and second longer sentences"""
    count = Counter(a)
    res = Counter()
    res[ORDERED] = count[ORDERED] + count[ORDERED_ALIGNED]
    res[FIRST_LONGER] = count[FIRST_LONGER] + count[FIRST_LONGER_ALIGNED]
    res[SECOND_LONGER] = count[SECOND_LONGER] + count[SECOND_LONGER_ALIGNED]
    return res


def compare(filenames, names, backup, origin, read_paragraph=read_paragraph, compare_paragraphs=compare_paragraphs):
    """ compares the conservatism of an iterable of files to an origin text
    filenames - iterable containing file names of sentences
                            that correspond to the sentences in origin file.
                            One sentence per line.
    names - iterable of names to call each file
    backup - cache file
    origin - paragran with original sentences (not a filename)
    """
    contents = []
    res_list = []
    for filename in filenames:
        contents.append(read_paragraph(filename))
    #     print(np.mean([len(s) for s in contents[-1].split("\n")]), filename)
    # print(np.mean([len(s) for s in origin.split("\n")]), "origin")
    # return
    old_res = read(backup) if backup else {}
    for (name, res) in old_res.items():
        res.append(name)
        dump(res_list, backup)
    for name, content in zip(names, contents):
        if name not in old_res:
            broken, words_differences, index_differences, spearman_differences, aligned_by = compare_paragraphs(
                origin, content)
            res_list.append((broken, words_differences, index_differences,
                             spearman_differences, aligned_by, name))
            dump(res_list, backup)
        else:
            res_list.append(old_res[name])
    dump(res_list, backup)
    plot_comparison(res_list)
    convert_file_to_csv(backup)


###########################################################
####                    VISUALIZATION                   ###
###########################################################


def create_hist(l, top=30, bottom=0):
    """ converts a int counter to a sorted list for a histogram"""
    count = Counter(l)
    hist = [0] * (max(count.keys()) - bottom + 1)
    for key, val in count.items():
        if key <= top and key >= bottom:
            hist[key - bottom] = val
    return hist if hist else [0]


def plot_ygrid(magnitude, ymin=None, ymax=None, ax=None, alpha=0.3):
    ax = init_ax(ax)
    ymin, ymax = init_ylim(ymin, ymax, ax)
    # not efficient if far from 0
    i = 1
    while magnitude * i < ymax:
        y = magnitude * i
        i += 1
        if y > ymin:
            plt.axhline(y=y, lw=0.5, color="black",
                        alpha=alpha, linestyle='--')
    i = 0
    while magnitude * i > ymin:
        y = magnitude * i
        i += 1
        if y < ymax:
            plt.axhline(y=y, lw=0.5, color="black",
                        alpha=alpha, linestyle='--')


def remove_spines(ax=None):
    ax = init_ax(ax)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)


def init_ax(ax=None):
    if ax is None:
        ax = plt.gca()
    return ax


def init_ylim(ymin=None, ymax=None, ax=None):
    ax = init_ax(ax)
    if ymin is None or ymax is None:
        tymin, tymax = ax.get_ylim()
        if ymin is None:
            ymin = tymin
        if ymax is None:
            ymax = tymax
    return ymin, ymax


def beautify_heatmap(colorbar=None, magnitude=None, ymin=None, ymax=None,  ax=None, fontsize=14):
    ax = init_ax(ax)
    remove_spines(ax)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.tick_params(axis="both", which="both", bottom="off", top="off",
                    labelbottom="on", left="off", right="off", labelleft="on")
    if colorbar:
        colorbar.ax.tick_params(labelsize=fontsize)


def beautify_lines_graph(magnitude, ymin=None, ymax=None, ax=None, fontsize=14, ygrid_alpha=None):
    ax = init_ax(ax)
    remove_spines(ax)

    # Ensure that the axis ticks only show up on the bottom and left of the plot.
    # Ticks on the right and top of the plot are generally unnecessary
    # chartjunk.
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)

    # # Limit the range of the plot to only where the data is.
    # # Avoid unnecessary whitespace.
    # plt.ylim(ymin, ymax)
    # plt.xlim(xmin, xmax)

    # Provide tick lines across the plot to help your viewers trace along
    # the axis ticks. Make sure that the lines are light and small so they
    # don't obscure the primary data lines.
    # Remove the tick marks; they are unnecessary with the tick lines we
    # just plotted.
    plt.tick_params(axis="both", which="both", bottom="off", top="off",
                    labelbottom="on", left="off", right="off", labelleft="on")
    data = {"ymin": ymin, "ymax": ymax,
            "magnitude": magnitude, "alpha": ygrid_alpha, "ax": ax}
    data = dict((k, v) for k, v in data.items() if v is not None)
    plot_ygrid(**data)


def many_colors(labels, colors=cm.rainbow):
    """creates colors, each corresponding to a unique label

    use for a list of colors:
    example = [(230, 97, 1), (253, 184, 99),
                   (178, 171, 210), (94, 60, 153)]
    for i in range(len(example)):    
        r, g, b = example[i]    
        example[i] = (r / 255., g / 255., b / 255.)

     places with colors
     https://matplotlib.org/users/colormaps.html
     http://colorbrewer2.org/#type=diverging&scheme=PuOr&n=4
     http://tableaufriction.blogspot.co.il/2012/11/finally-you-can-use-tableau-data-colors.html
     https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
     """
    cls = set(labels)
    if len(cls) == 2:
        return dict(zip(cls, ("blue", "orange")))
    return dict(zip(cls, colors(np.linspace(0, 1, len(cls)))))


def plot_words_relative_differences_hist(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the hists"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    plot_differences_hist(l, ax, words_differences, "words", 0, relative_bar=0)


def plot_words_differences_hist(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the hists"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    plot_differences_hist(l, ax, words_differences, "words", 0)


def plot_index_differences_hist(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the hists"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    plot_differences_hist(l, ax, index_differences, "index", 1)


def plot_spearman_differences(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the hists"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    boxplot_differences(l, ax, spearman_differences, r"$\rho$", 1)


def plot_spearman_ecdf(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the hists"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    plot_ecdf(l, ax, spearman_differences, r"$\rho$", 0.7, 1)


def plot_words_differences(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the hists"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    plot_differences(l, ax, words_differences, "words", 2)


def plot_words_heat(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the hists"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    plot_differences_heatmap(l, ax, words_differences, "words", [
                             0, 1, 2, 3, 4, 5, 10, 20])


def plot_index_differences(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the hists"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    plot_differences(l, ax, index_differences, "index", 1)


def plot_ecdf(l, ax, pivot, diff_type, bottom, top):
    # ys = []
    name = -1
    colors = many_colors(range(len(l)))
    for i, tple in enumerate(l):
        x = np.sort(tple[pivot])
        x = [point for point in x if point < top and point >= bottom]
        yvals = np.arange(len(x)) / float(len(x))
        # ys.append((x, tple[name], colors[i]))
        if tple[name] == "gold" or "fce" in tple[name]:
            ax.plot(x, yvals, "--", color=colors[i], label=tple[name])
        else:
            ax.plot(x, yvals, color=colors[i], label=tple[name])
    plt.ylim(ymax=0.6)
    # for y, name, color in ys:
    # x = np.linspace(min(sample), max(sample))
    # y = ecdf(x)
    # ax.step(x, y, olor=color, label=name)
    # ax.boxplot(x, labels=names, showmeans=True)
    plt.ylabel("probability")
    plt.xlabel(diff_type)
    # plt.title("empirical distribution of " + diff_type + " changes")
    plt.legend(loc=6, fontsize=10, fancybox=True, shadow=True)


def boxplot_differences(l, ax, pivot, diff_type, bottom):
    # ys = []
    x = []
    names = []
    name = -1
    # max_len = 0
    colors = many_colors(range(len(l)))

    for i, tple in enumerate(l):
        y = tple[pivot]
        x.append(y)
        names.append(tple[name])

    plt.autoscale(enable=True, axis='x', tight=False)
    ax.boxplot(x, labels=names, showmeans=True)
    # plt.title("box plot of " + diff_type + " changes")
    plt.legend(loc=7, fontsize=10, fancybox=True, shadow=True)


def plot_differences_hist(l, ax, pivot, diff_type, bottom, bins=None, relative_bar=-1):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the plots"""
    total_width = 1
    width = total_width / len(l)
    name = -1
    if bins != None:
        bins = np.array(bins) + 1 - bottom
    relative = 0
    ys = []
    names = []
    for i, tple in enumerate(l):
        full_hist = create_hist(tple[pivot], bottom=bottom)
        # print(full_hist)
        if bins == None:
            y = full_hist
        else:
            y = [sum(full_hist[:bins[0]])]
            # print(full_hist[:bins[0]])
            for j in range(1, len(bins)):
                print(full_hist[bins[j - 1]:bins[j]])
                y.append(sum(full_hist[bins[j - 1]:bins[j]]))
            y.append(sum(full_hist[bins[j]:]))
        relative_text = "relative_bar to column number " + \
            str(relative_bar) if relative_bar >= 0 else ""
        y = np.array(y)
        ys.append(y)
        if i == relative_bar:
            relative = y
        names.append(tple[name])
    print(ys)
    colors = many_colors(range(len(l)))
    for i, (y, name) in enumerate(zip(ys, names)):
        print(diff_type + " hist", relative_text,
              "results", name, ":", y - relative_bar)
        if relative_bar >= 0:
            longer_shape = y.shape if len(y) > len(
                relative) else relative.shape
            print("unpadded", y, relative, longer_shape)
            y = np.lib.pad(y, (0, longer_shape[0] - y.shape[0]), "constant")
            relative = np.lib.pad(
                relative, (0, longer_shape[0] - relative.shape[0]), "constant")
            print("padded", y, relative)
        x = np.array(range(len(y)))
        x = x + i * width - 0.5 * total_width
        ax.bar(x, y - relative, width=width,
               color=colors[i], align='center', label=name, edgecolor=colors[i])
    plt.autoscale(enable=True, axis='x', tight=False)
    ylabel = "amount" if relative_bar < 0 else "amount relative to " + \
        names[relative_bar]
    plt.ylabel(ylabel)
    plt.xlim(xmin=0 - 0.5 * total_width)
    plt.xlabel("number of " + diff_type + " changed")
    # plt.title("number of " + diff_type + " changed by method of correction")
    plt.legend(loc=7, fontsize=10, fancybox=True, shadow=True)
    # plt.tight_layout()

    # #old version
    #   width = 1/len(l)
    # name = -1
    # for i, tple in enumerate(l):
    #   y = create_hist(tple[pivot], bottom=bottom)
    #   x = np.array(range(len(y)))
    #   print(diff_type + " hist results ",tple[name],":",y)
    #   colors = many_colors(range(len(l)))
    #   ax.bar(x + i*width, y, width=width, color=colors[i], align='center', label=tple[name], edgecolor=colors[i])
    # plt.autoscale(enable=True, axis='x', tight=False)
    # plt.ylabel("amount")
    # plt.xlim(xmin=0)
    # plt.xlabel("number of " + diff_type + " changed")
    # # plt.title("number of " + diff_type + " changed by method of correction")
    # plt.legend(loc=7, fontsize=10, fancybox=True, shadow=True)
    # # plt.tight_layout()


def plot_aligned_by(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot """
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    width = 1 / len(l)
    for i, tple in enumerate(l):
        y = extract_aligned_by_dict(tple[aligned_by])
        y = [y[FIRST_LONGER] + y[COMMA_REPLACE_FIRST], y[ORDERED],
             y[SECOND_LONGER] + y[COMMA_REPLACE_SECOND]]
        print("first ordered and second longer", tple[name], ":", y)
        x = np.array(range(len(y)))
        colors = many_colors(range(len(l)))
        ax.bar(x + i * width, y, width=width,
               color=colors[i], align='center', label=tple[name], edgecolor=colors[i])
    ax.autoscale(tight=True)
    plt.ylabel("amount")
    plt.xlabel("number of sentence changes of that sort")
    # plt.title("number of sentence changes by method of correction")
    plt.xticks(x + width, ("sentences split",
                           ORDERED, "sentences concatanated"))
    plt.legend(loc=7, fontsize=10, fancybox=True, shadow=True)
    # plt.tight_layout()


def plot_not_aligned(l, ax):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the bars"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    width = 1 / len(l)
    start = 1 + 2 / 5
    for i, tple in enumerate(l):
        y = extract_aligned_by_dict(tple[aligned_by])
        y = y = [y[FIRST_LONGER] + y[COMMA_REPLACE_FIRST],
                 y[SECOND_LONGER] + y[COMMA_REPLACE_SECOND]]
        x = np.array(range(len(y)))
        colors = many_colors(range(len(l)))
        if tple[name] == "gold" or "fce" in tple[name]:
            bar = ax.bar(x + (start + i) * width, y, width=width, color=colors[
                         i], align='center', label=tple[name], edgecolor="black", hatch="\\")
            ax.bar(x + i * width, y, width=width /
                   2000000, edgecolor="w", color="w")
        else:
            bar = ax.bar(x + (start + i) * width, y, width=width,
                         color=colors[i], align='center', label=tple[name], edgecolor=colors[i])
    ax.autoscale(tight=True)
    plt.ylim(ymax=40)
    plt.ylabel("amount")
    plt.xlabel("number of sentence changes of that sort")
    # plt.title("number of sentence     changes by method of correction")
    plt.xticks(x + width * (len(l) / 2 - 1),
               ("sentences split", "sentences concatanated"))
    plt.legend(loc=7, fontsize=10, fancybox=True, shadow=True)
    # plt.tight_layout()


# cm.coolwarm_r
def plot_differences_heatmap(l, ax, pivot, diff_type, bins, colors=cm.bone_r):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the plots"""
    width = 1 / len(l)
    name = -1
    mesh = []
    names = []
    top_bins = np.array(bins) + 1
    for i, tple in enumerate(l):
        names.append(tple[-1])
        full_hist = create_hist(tple[pivot], bottom=0)
        y = [sum(full_hist[:top_bins[0]])]
        for j in range(1, len(top_bins)):
            y.append(sum(full_hist[top_bins[j - 1]:top_bins[j]]))
        y.append(sum(full_hist[top_bins[j]:]))
        print(diff_type + " heatmap results ", tple[name], ":", y)
        mesh.append(y)
        # ax.bar(x + i*width, y, width=width, color=colors[i], align='center', label=tple[name], edgecolor=colors[i])
    x = np.array(range(len(y)))
    mesh = np.array(mesh)
    ax.set_frame_on(False)
    heatmap = ax.pcolormesh(mesh, cmap=colors)
    plt.autoscale(enable=True, axis='x', tight=False)
    # plt.ylabel("")
    plt.xlim(xmin=0)
    plt.xlabel("number of " + diff_type + " changed")
    bin_names = ["0" if bins[0] == 0 else "0-" + str(bins[0])]
    for i in range(len(bins)):
        if bins[i] > bins[i - 1] + 1:
            bin_names.append(str(bins[i - 1] + 1) + "-" + str(bins[i]))
        elif bins[i] == bins[i - 1] + 1:
            bin_names.append(str(bins[i]))
    bin_names.append(str(bins[-1]) + "+")
    ax.set_yticks(np.arange(len(names)) + 0.5)
    ax.set_yticklabels(names)
    ax.set_xticks(x + 0.5)
    ax.set_xticklabels(bin_names, minor=False)

    colorbar = plt.colorbar(heatmap)
    beautify_heatmap(colorbar=colorbar)
    # plt.title("number of " + diff_type + " changed by method of correction")
    # plt.tight_layout()


def plot_differences(l, ax, pivot, diff_type, bottom):
    """ gets a list of (broken, words_differences, index_differences, spearman_differences, aligned_by, name) tuples and plot the plots"""
    broken, words_differences, index_differences, spearman_differences, aligned_by, name = list(
        range(6))  # tuple structure
    ys = []
    max_len = 0
    colors = many_colors(range(len(l)))

    for i, tple in enumerate(l):
        y = create_hist(tple[pivot], bottom=bottom)
        ys.append((y, tple[name], colors[i]))
        max_len = max(max_len, len(y))

    x = np.array(range(bottom, max_len + bottom))

    for y, name, color in ys:
        y = y + [0] * (max_len - len(y))
        if name == "gold" or "fce" in name:
            ax.plot(x, np.cumsum(y), "--", color=color, label=name)
        else:
            ax.plot(x, np.cumsum(y), color=color, label=name)
    plt.autoscale(enable=True, axis='x', tight=False)
    plt.ylabel("amount")
    plt.xlabel("number of " + diff_type + " changed")
    # plt.xlim(xmin=-x[-1]/5)
    # plt.xticks([10*i for i in range(math.ceil(x[-1]/10) + 1)])
    # plt.legend(loc=6, fontsize=10, fancybox=True, shadow=True)
    plt.legend(loc=7, fontsize=10, fancybox=True, shadow=True)
    # plt.title("accumulative number of sentences by " + diff_type + " changed")


def plot_comparison(l):
    """gets a list of tuple parameters and plots them"""
    data = []
    ax = plt.subplot(221)
    plot_spearman_differences(l, ax)
    ax = plt.subplot(222)
    plot_spearman_ecdf(l, ax)
    ax = plt.subplot(223)
    plot_aligned_by(l, ax)
    ax = plt.subplot(224)
    plot_not_aligned(l, ax)
    plt.clf()

    data = []
    dirname = "./plots/"
    ax = plt.subplot(111)
    plot_spearman_differences(l, ax)
    plt.savefig(dirname + r"spearman_differences" +
                trial_name + ".png", bbox_inches='tight')
    plt.clf()
    ax = plt.subplot(111)
    plot_spearman_ecdf(l, ax)
    plt.savefig(dirname + r"spearman_ecdf" +
                trial_name + ".png", bbox_inches='tight')
    plt.clf()
    ax = plt.subplot(111)
    plot_words_differences(l, ax)
    plt.savefig(dirname + r"words_differences" +
                trial_name + ".png", bbox_inches='tight')
    plt.clf()
    ax = plt.subplot(111)
    plot_words_differences_hist(l, ax)
    plt.savefig(dirname + r"words_differences_hist" +
                trial_name + ".png", bbox_inches='tight')
    plt.clf()
    ax = plt.subplot(111)
    plot_words_relative_differences_hist(l, ax)
    plt.savefig(dirname + r"words_relative_differences_hist" +
                trial_name + ".png", bbox_inches='tight')
    plt.show()
    plt.clf()
    ax = plt.subplot(111)
    plot_words_heat(l, ax)
    plt.savefig(dirname + r"words_differences_heat" +
                trial_name + ".png", bbox_inches='tight')
    plt.clf()
    ax = plt.subplot(111)
    plot_index_differences(l, ax)
    plt.savefig(dirname + r"index_differences" +
                trial_name + ".png", bbox_inches='tight')
    plt.clf()
    ax = plt.subplot(111)
    plot_index_differences_hist(l, ax)
    plt.savefig(dirname + r"index_differences_hist" +
                trial_name + ".png", bbox_inches='tight')
    plt.clf()
    ax = plt.subplot(111)
    plot_aligned_by(l, ax)
    plt.savefig(dirname + r"aligned_all" +
                trial_name + ".png", bbox_inches='tight')
    plt.clf()
    ax = plt.subplot(111)
    plot_not_aligned(l, ax)
    plt.savefig(dirname + r"aligned" + trial_name +
                ".png", bbox_inches='tight')
    plt.clf()


###########################################################
####                        UTIL                        ###
###########################################################
def convert_file_to_csv(filename):
    l = read(filename)
    filename = os.path.splitext(filename)[0] + ".csv"
    col_names = ["words_differences", "index_differences",
                 "spearman_differences", "aligned_by"]
    names = l.keys()
    names_row = []
    spacing_left = int(len(col_names) / 2) * [""]
    spacing_right = (int((len(col_names) + 1) / 2) - 1) * [""]
    for name in names:
        names_row += spacing_left + [name] + spacing_right
    col_names = col_names * len(names_row)
    max_len = 0
    for value in l.values():
        for lst in value:
            lst = lst[1:]  # remove sentence breaks
            max_len = max(max_len, len(lst))
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(names_row)
        writer.writerow(col_names)
        for i in range(max_len):
            row = []
            for value in l.values():
                value = value[1:]
                for lst in value:
                    if len(lst) > i:
                        row.append(lst[i])
                    else:
                        row.append("")
            writer.writerow(row)


def read(filename):
    try:
        with open(filename, "r+") as fl:
            return json.load(fl)
    except FileNotFoundError as e:
        print(e, "The file was not found, creating it instead")
        return dict()
    except json.decoder.JSONDecodeError as e:
        print("json decoder error in ", filename, ":", e)
        return dict()


def dump(l, filename):
    out = read(filename)
    for obj in l:
        name = obj[-1]
        obj = obj[:-1]
        if name not in out:
            print(name, " name")
            out[name] = obj
    with open(filename, "w+") as fl:
        json.dump(out, fl)


if __name__ == '__main__':
    main()
