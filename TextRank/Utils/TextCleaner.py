import string
import unicodedata
import logging
import re
from .SnowBall import SnowballStemmer
from .StopWords import get_stopwords_by_language

logger = logging.getLogger('summa.preprocessing.cleaner')

try:
    from pattern.en import tag

    logger.info("'pattern' package found; tag filters are available for English")
    HAS_PATTERN = True
except ImportError:
    logger.info("'pattern' package not found; tag filters are not available for English")
    HAS_PATTERN = False

# Часть функций взята из Gensim v0.10.0:
# Gensim - это готовая к работе библиотека с
# открытым исходным кодом для неконтролируемого моделирования
# тем и обработки естественного языка с использованием современного
# статистического машинного обучения. Gensim реализован на Python и Cython
# для максимальной производительности и масштабируемости.
# https://github.com/RaRe-Technologies/gensim/blob/0.10.0/gensim/utils.py
# https://github.com/RaRe-Technologies/gensim/blob/0.10.0/gensim/parsing/preprocessing.py


SEPARATOR = r"@"
RE_SENTENCE = re.compile('(\S.+?[.!?])(?=\s+|$)|(\S.+?)(?=[\n]|$)')
AB_SENIOR = re.compile("([A-Z][a-z]{1,2}\.)\s(\w)")
AB_ACRONYM = re.compile("(\.[a-zA-Z]\.)\s(\w)")
AB_ACRONYM_LETTERS = re.compile("([a-zA-Z])\.([a-zA-Z])\.")
UNDO_AB_SENIOR = re.compile("([A-Z][a-z]{1,2}\.)" + SEPARATOR + "(\w)")
UNDO_AB_ACRONYM = re.compile("(\.[a-zA-Z]\.)" + SEPARATOR + "(\w)")

STEMMER = None
STOPWORDS = None


def set_stemmer_language(language):
    global STEMMER
    if not language in SnowballStemmer.languages:
        raise ValueError("Valid languages are: " + ", ".join(sorted(SnowballStemmer.languages)))
    STEMMER = SnowballStemmer(language)


def set_stopwords_by_language(language, additional_stopwords):
    global STOPWORDS
    words = get_stopwords_by_language(language)
    if not additional_stopwords:
        additional_stopwords = {}
    STOPWORDS = frozenset({w for w in words.split() if w} | {w for w in additional_stopwords if w})


def init_textcleanner(language, additional_stopwords):
    set_stemmer_language(language)
    set_stopwords_by_language(language, additional_stopwords)


def split_sentences(text):
    processed = replace_abbreviations(text)
    return [undo_replacement(sentence) for sentence in get_sentences(processed)]


def replace_abbreviations(text):
    return replace_with_separator(text, SEPARATOR, [AB_SENIOR, AB_ACRONYM])


def undo_replacement(sentence):
    return replace_with_separator(sentence, r" ", [UNDO_AB_SENIOR, UNDO_AB_ACRONYM])


def replace_with_separator(text, separator, regexs):
    replacement = r"\1" + separator + r"\2"
    result = text
    for regex in regexs:
        result = regex.sub(replacement, result)
    return result


def get_sentences(text):
    for match in RE_SENTENCE.finditer(text):
        yield match.group()


# Взято из Gensim
RE_PUNCT = re.compile('([%s])+' % re.escape(string.punctuation), re.UNICODE)


def strip_punctuation(s):
    return RE_PUNCT.sub(" ", s)


# Взято из Gensim
RE_NUMERIC = re.compile(r"[0-9]+", re.UNICODE)


def strip_numeric(s):
    return RE_NUMERIC.sub("", s)


def remove_stopwords(sentence):
    return " ".join(w for w in sentence.split() if w not in STOPWORDS)


def stem_sentence(sentence):
    word_stems = [STEMMER.stem(word) for word in sentence.split()]
    return " ".join(word_stems)


def apply_filters(sentence, filters):
    for f in filters:
        sentence = f(sentence)
    return sentence


def filter_words(sentences):
    filters = [lambda x: x.lower(), strip_numeric, strip_punctuation, remove_stopwords,
               stem_sentence]
    apply_filters_to_token = lambda token: apply_filters(token, filters)
    return list(map(apply_filters_to_token, sentences))


# Взято из Gensim
def deaccent(text):
    """
    Удалить акцентуацию с заданной строки.
    """
    norm = unicodedata.normalize("NFD", text)
    result = "".join(ch for ch in norm if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize("NFC", result)


# Взято из Gensim
PAT_ALPHABETIC = re.compile('(((?![\d])\w)+)', re.UNICODE)


def tokenize(text, lowercase=False, deacc=False):
    """
    Итеративно выдает токены в виде строк в кодировке Юникод, опционально также их нижний регистр
    и удаляет следы акцента.
    """
    if lowercase:
        text = text.lower()
    if deacc:
        text = deaccent(text)
    for match in PAT_ALPHABETIC.finditer(text):
        yield match.group()


def merge_syntactic_units(original_units, filtered_units, tags=None):
    units = []
    for i in range(len(original_units)):
        if filtered_units[i] == '':
            continue

        text = original_units[i]
        token = filtered_units[i]
        tag = tags[i][1] if tags else None
        sentence = SyntacticUnit(text, token, tag)
        sentence.index = i

        units.append(sentence)

    return units


def clean_text_by_sentences(text, language, additional_stopwords=None):
    """ Разбивает данный текст на предложения, применяя фильтры и их лемматизируя.
     Возвращает список SyntacticUnit. """
    init_textcleanner(language, additional_stopwords)
    original_sentences = split_sentences(text)
    filtered_sentences = filter_words(original_sentences)

    return merge_syntactic_units(original_sentences, filtered_sentences)


def clean_text_by_word(text, language, deacc=False, additional_stopwords=None):
    """ Разбивает данный текст на слова, применяя фильтры и их лемматизируя.
     Возвращает слово слова -> syntacticUnit. """
    init_textcleanner(language, additional_stopwords)
    text_without_acronyms = replace_with_separator(text, "", [AB_ACRONYM_LETTERS])
    original_words = list(tokenize(text_without_acronyms, lowercase=True, deacc=deacc))
    filtered_words = filter_words(original_words)
    if HAS_PATTERN:
        tags = tag(" ".join(original_words))  # тегу нужен контекст слов в тексте
    else:
        tags = None
    units = merge_syntactic_units(original_words, filtered_words, tags)
    return {unit.text: unit for unit in units}


def tokenize_by_word(text, deacc=False):
    text_without_acronyms = replace_with_separator(text, "", [AB_ACRONYM_LETTERS])
    return tokenize(text_without_acronyms, lowercase=True, deacc=deacc)


class SyntacticUnit(object):

    def __init__(self, text, token=None, tag=None):
        self.text = text
        self.token = token
        self.tag = tag[:2] if tag else None  # только первые две буквы тега
        self.index = -1
        self.score = -1

    def __str__(self):
        return "Original unit: '" + self.text + "' *-*-*-* " + "Processed unit: '" + self.token + "'"

    def __repr__(self):
        return str(self)
