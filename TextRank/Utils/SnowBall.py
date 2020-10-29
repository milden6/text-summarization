# Snowball Stemmer
# Алогоритм: Мартин Портер <martin@tartarus.org>

"""
Snowball stemmers
Этот модуль предоставляет порт Snowball Stemmer
разработанный Мартином Портером.
http://snowball.tartarus.org/
Стеммеры называются Snowball, потому что Портер создал
язык программирования с таким именем для
новых алгоритмов, от этого и появилось такое название.
Я использую только стеммер для английского языка т.к.
все данные будут на нем(с портала Reddit).
"""


class SnowballStemmer:
    languages = (
        "english",
        "russian",
    )

    def __init__(self, language):
        if language not in self.languages:
            raise ValueError("The language '%s' is not supported." % language)
        stemmerclass = globals()[language.capitalize() + "Stemmer"]
        self.stemmer = stemmerclass()
        self.stem = self.stemmer.stem


class _LanguageSpecificStemmer:
    """
     Это вспомогательный подкласс предлагает возможность
     вызывать конкретный стеммер напрямую.
     Это полезно, если язык будет указан явно.
    """

    def __init__(self):
        language = type(self).__name__.lower()
        if language.endswith("stemmer"):
            pass

    def __repr__(self):
        return "<%s>" % type(self).__name__

    @staticmethod
    def _rv_standard(word, vowels):
        """
         Возвращает стандартную интерпретацию строки области RV.
         Если вторая буква является согласной, RV является областью после
         следующий гласной. Если первые две буквы гласные, то RV
         область после следующей согласной. В противном случае RV является
         областью после третьей буквы.
        """
        rv = ""
        if len(word) >= 2:
            if word[1] not in vowels:
                for i in range(2, len(word)):
                    if word[i] in vowels:
                        rv = word[i + 1:]
                        break

            elif word[:2] in vowels:
                for i in range(2, len(word)):
                    if word[i] not in vowels:
                        rv = word[i + 1:]
                        break
            else:
                rv = word[3:]

        return rv

class _StandardStemmer(_LanguageSpecificStemmer):

    """
    This subclass encapsulates two methods for defining the standard versions
    of the string regions R1, R2, and RV.
    """

    def _r1r2_standard(self, word, vowels):
        """
        Return the standard interpretations of the string regions R1 and R2.
        R1 is the region after the first non-vowel following a vowel,
        or is the null region at the end of the word if there is no
        such non-vowel.
        R2 is the region after the first non-vowel following a vowel
        in R1, or is the null region at the end of the word if there
        is no such non-vowel.
        :param word: The word whose regions R1 and R2 are determined.
        :type word: str or unicode
        :param vowels: The vowels of the respective language that are
                       used to determine the regions R1 and R2.
        :type vowels: unicode
        :return: (r1,r2), the regions R1 and R2 for the respective word.
        :rtype: tuple
        :note: This helper method is invoked by the respective stem method of
               the subclasses DutchStemmer, FinnishStemmer,
               FrenchStemmer, GermanStemmer, ItalianStemmer,
               PortugueseStemmer, RomanianStemmer, and SpanishStemmer.
               It is not to be invoked directly!
        :note: A detailed description of how to define R1 and R2
               can be found at http://snowball.tartarus.org/texts/r1r2.html
        """
        r1 = ""
        r2 = ""
        for i in range(1, len(word)):
            if word[i] not in vowels and word[i-1] in vowels:
                r1 = word[i+1:]
                break

        for i in range(1, len(r1)):
            if r1[i] not in vowels and r1[i-1] in vowels:
                r2 = r1[i+1:]
                break

        return (r1, r2)



    def _rv_standard(self, word, vowels):
        """
        Return the standard interpretation of the string region RV.
        If the second letter is a consonant, RV is the region after the
        next following vowel. If the first two letters are vowels, RV is
        the region after the next following consonant. Otherwise, RV is
        the region after the third letter.
        :param word: The word whose region RV is determined.
        :type word: str or unicode
        :param vowels: The vowels of the respective language that are
                       used to determine the region RV.
        :type vowels: unicode
        :return: the region RV for the respective word.
        :rtype: unicode
        :note: This helper method is invoked by the respective stem method of
               the subclasses ItalianStemmer, PortugueseStemmer,
               RomanianStemmer, and SpanishStemmer. It is not to be
               invoked directly!
        """
        rv = ""
        if len(word) >= 2:
            if word[1] not in vowels:
                for i in range(2, len(word)):
                    if word[i] in vowels:
                        rv = word[i+1:]
                        break

            elif word[:2] in vowels:
                for i in range(2, len(word)):
                    if word[i] not in vowels:
                        rv = word[i+1:]
                        break
            else:
                rv = word[3:]

        return rv

class EnglishStemmer(_StandardStemmer):

    """
    The English Snowball stemmer.
    :cvar __vowels: The English vowels.
    :type __vowels: unicode
    :cvar __double_consonants: The English double consonants.
    :type __double_consonants: tuple
    :cvar __li_ending: Letters that may directly appear before a word final 'li'.
    :type __li_ending: unicode
    :cvar __step0_suffixes: Suffixes to be deleted in step 0 of the algorithm.
    :type __step0_suffixes: tuple
    :cvar __step1a_suffixes: Suffixes to be deleted in step 1a of the algorithm.
    :type __step1a_suffixes: tuple
    :cvar __step1b_suffixes: Suffixes to be deleted in step 1b of the algorithm.
    :type __step1b_suffixes: tuple
    :cvar __step2_suffixes: Suffixes to be deleted in step 2 of the algorithm.
    :type __step2_suffixes: tuple
    :cvar __step3_suffixes: Suffixes to be deleted in step 3 of the algorithm.
    :type __step3_suffixes: tuple
    :cvar __step4_suffixes: Suffixes to be deleted in step 4 of the algorithm.
    :type __step4_suffixes: tuple
    :cvar __step5_suffixes: Suffixes to be deleted in step 5 of the algorithm.
    :type __step5_suffixes: tuple
    :cvar __special_words: A dictionary containing words
                           which have to be stemmed specially.
    :type __special_words: dict
    :note: A detailed description of the English
           stemming algorithm can be found under
           http://snowball.tartarus.org/algorithms/english/stemmer.html
    """

    __vowels = "aeiouy"
    __double_consonants = ("bb", "dd", "ff", "gg", "mm", "nn",
                           "pp", "rr", "tt")
    __li_ending = "cdeghkmnrt"
    __step0_suffixes = ("'s'", "'s", "'")
    __step1a_suffixes = ("sses", "ied", "ies", "us", "ss", "s")
    __step1b_suffixes = ("eedly", "ingly", "edly", "eed", "ing", "ed")
    __step2_suffixes = ('ization', 'ational', 'fulness', 'ousness',
                        'iveness', 'tional', 'biliti', 'lessli',
                        'entli', 'ation', 'alism', 'aliti', 'ousli',
                        'iviti', 'fulli', 'enci', 'anci', 'abli',
                        'izer', 'ator', 'alli', 'bli', 'ogi', 'li')
    __step3_suffixes = ('ational', 'tional', 'alize', 'icate', 'iciti',
                        'ative', 'ical', 'ness', 'ful')
    __step4_suffixes = ('ement', 'ance', 'ence', 'able', 'ible', 'ment',
                        'ant', 'ent', 'ism', 'ate', 'iti', 'ous',
                        'ive', 'ize', 'ion', 'al', 'er', 'ic')
    __step5_suffixes = ("e", "l")
    __special_words = {"skis" : "ski",
                       "skies" : "sky",
                       "dying" : "die",
                       "lying" : "lie",
                       "tying" : "tie",
                       "idly" : "idl",
                       "gently" : "gentl",
                       "ugly" : "ugli",
                       "early" : "earli",
                       "only" : "onli",
                       "singly" : "singl",
                       "sky" : "sky",
                       "news" : "news",
                       "howe" : "howe",
                       "atlas" : "atlas",
                       "cosmos" : "cosmos",
                       "bias" : "bias",
                       "andes" : "andes",
                       "inning" : "inning",
                       "innings" : "inning",
                       "outing" : "outing",
                       "outings" : "outing",
                       "canning" : "canning",
                       "cannings" : "canning",
                       "herring" : "herring",
                       "herrings" : "herring",
                       "earring" : "earring",
                       "earrings" : "earring",
                       "proceed" : "proceed",
                       "proceeds" : "proceed",
                       "proceeded" : "proceed",
                       "proceeding" : "proceed",
                       "exceed" : "exceed",
                       "exceeds" : "exceed",
                       "exceeded" : "exceed",
                       "exceeding" : "exceed",
                       "succeed" : "succeed",
                       "succeeds" : "succeed",
                       "succeeded" : "succeed",
                       "succeeding" : "succeed"}

    def stem(self, word):

        """
        Stem an English word and return the stemmed form.
        :param word: The word that is stemmed.
        :type word: str or unicode
        :return: The stemmed form.
        :rtype: unicode
        """
        word = word.lower()

        if len(word) <= 2:
            return word

        elif word in self.__special_words:
            return self.__special_words[word]

        # Map the different apostrophe characters to a single consistent one
        word = (word.replace("\u2019", "\x27")
                    .replace("\u2018", "\x27")
                    .replace("\u201B", "\x27"))

        if word.startswith("\x27"):
            word = word[1:]

        if word.startswith("y"):
            word = "".join(("Y", word[1:]))

        for i in range(1, len(word)):
            if word[i-1] in self.__vowels and word[i] == "y":
                word = "".join((word[:i], "Y", word[i+1:]))

        step1a_vowel_found = False
        step1b_vowel_found = False

        r1 = ""
        r2 = ""

        if word.startswith(("gener", "commun", "arsen")):
            if word.startswith(("gener", "arsen")):
                r1 = word[5:]
            else:
                r1 = word[6:]

            for i in range(1, len(r1)):
                if r1[i] not in self.__vowels and r1[i-1] in self.__vowels:
                    r2 = r1[i+1:]
                    break
        else:
            r1, r2 = self._r1r2_standard(word, self.__vowels)


        # STEP 0
        for suffix in self.__step0_suffixes:
            if word.endswith(suffix):
                word = word[:-len(suffix)]
                r1 = r1[:-len(suffix)]
                r2 = r2[:-len(suffix)]
                break

        # STEP 1a
        for suffix in self.__step1a_suffixes:
            if word.endswith(suffix):

                if suffix == "sses":
                    word = word[:-2]
                    r1 = r1[:-2]
                    r2 = r2[:-2]

                elif suffix in ("ied", "ies"):
                    if len(word[:-len(suffix)]) > 1:
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]
                    else:
                        word = word[:-1]
                        r1 = r1[:-1]
                        r2 = r2[:-1]

                elif suffix == "s":
                    for letter in word[:-2]:
                        if letter in self.__vowels:
                            step1a_vowel_found = True
                            break

                    if step1a_vowel_found:
                        word = word[:-1]
                        r1 = r1[:-1]
                        r2 = r2[:-1]
                break

        # STEP 1b
        for suffix in self.__step1b_suffixes:
            if word.endswith(suffix):
                if suffix in ("eed", "eedly"):

                    if r1.endswith(suffix):
                        word = "".join((word[:-len(suffix)], "ee"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "ee"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "ee"))
                        else:
                            r2 = ""
                else:
                    for letter in word[:-len(suffix)]:
                        if letter in self.__vowels:
                            step1b_vowel_found = True
                            break

                    if step1b_vowel_found:
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                        r2 = r2[:-len(suffix)]

                        if word.endswith(("at", "bl", "iz")):
                            word = "".join((word, "e"))
                            r1 = "".join((r1, "e"))

                            if len(word) > 5 or len(r1) >=3:
                                r2 = "".join((r2, "e"))

                        elif word.endswith(self.__double_consonants):
                            word = word[:-1]
                            r1 = r1[:-1]
                            r2 = r2[:-1]

                        elif ((r1 == "" and len(word) >= 3 and
                               word[-1] not in self.__vowels and
                               word[-1] not in "wxY" and
                               word[-2] in self.__vowels and
                               word[-3] not in self.__vowels)
                              or
                              (r1 == "" and len(word) == 2 and
                               word[0] in self.__vowels and
                               word[1] not in self.__vowels)):

                            word = "".join((word, "e"))

                            if len(r1) > 0:
                                r1 = "".join((r1, "e"))

                            if len(r2) > 0:
                                r2 = "".join((r2, "e"))
                break

        # STEP 1c
        if len(word) > 2 and word[-1] in "yY" and word[-2] not in self.__vowels:
            word = "".join((word[:-1], "i"))
            if len(r1) >= 1:
                r1 = "".join((r1[:-1], "i"))
            else:
                r1 = ""

            if len(r2) >= 1:
                r2 = "".join((r2[:-1], "i"))
            else:
                r2 = ""

        # STEP 2
        for suffix in self.__step2_suffixes:
            if word.endswith(suffix):
                if r1.endswith(suffix):
                    if suffix == "tional":
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]

                    elif suffix in ("enci", "anci", "abli"):
                        word = "".join((word[:-1], "e"))

                        if len(r1) >= 1:
                            r1 = "".join((r1[:-1], "e"))
                        else:
                            r1 = ""

                        if len(r2) >= 1:
                            r2 = "".join((r2[:-1], "e"))
                        else:
                            r2 = ""

                    elif suffix == "entli":
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]

                    elif suffix in ("izer", "ization"):
                        word = "".join((word[:-len(suffix)], "ize"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "ize"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "ize"))
                        else:
                            r2 = ""

                    elif suffix in ("ational", "ation", "ator"):
                        word = "".join((word[:-len(suffix)], "ate"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "ate"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "ate"))
                        else:
                            r2 = "e"

                    elif suffix in ("alism", "aliti", "alli"):
                        word = "".join((word[:-len(suffix)], "al"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "al"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "al"))
                        else:
                            r2 = ""

                    elif suffix == "fulness":
                        word = word[:-4]
                        r1 = r1[:-4]
                        r2 = r2[:-4]

                    elif suffix in ("ousli", "ousness"):
                        word = "".join((word[:-len(suffix)], "ous"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "ous"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "ous"))
                        else:
                            r2 = ""

                    elif suffix in ("iveness", "iviti"):
                        word = "".join((word[:-len(suffix)], "ive"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "ive"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "ive"))
                        else:
                            r2 = "e"

                    elif suffix in ("biliti", "bli"):
                        word = "".join((word[:-len(suffix)], "ble"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "ble"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "ble"))
                        else:
                            r2 = ""

                    elif suffix == "ogi" and word[-4] == "l":
                        word = word[:-1]
                        r1 = r1[:-1]
                        r2 = r2[:-1]

                    elif suffix in ("fulli", "lessli"):
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]

                    elif suffix == "li" and word[-3] in self.__li_ending:
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]
                break

        # STEP 3
        for suffix in self.__step3_suffixes:
            if word.endswith(suffix):
                if r1.endswith(suffix):
                    if suffix == "tional":
                        word = word[:-2]
                        r1 = r1[:-2]
                        r2 = r2[:-2]

                    elif suffix == "ational":
                        word = "".join((word[:-len(suffix)], "ate"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "ate"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "ate"))
                        else:
                            r2 = ""

                    elif suffix == "alize":
                        word = word[:-3]
                        r1 = r1[:-3]
                        r2 = r2[:-3]

                    elif suffix in ("icate", "iciti", "ical"):
                        word = "".join((word[:-len(suffix)], "ic"))

                        if len(r1) >= len(suffix):
                            r1 = "".join((r1[:-len(suffix)], "ic"))
                        else:
                            r1 = ""

                        if len(r2) >= len(suffix):
                            r2 = "".join((r2[:-len(suffix)], "ic"))
                        else:
                            r2 = ""

                    elif suffix in ("ful", "ness"):
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                        r2 = r2[:-len(suffix)]

                    elif suffix == "ative" and r2.endswith(suffix):
                        word = word[:-5]
                        r1 = r1[:-5]
                        r2 = r2[:-5]
                break

        # STEP 4
        for suffix in self.__step4_suffixes:
            if word.endswith(suffix):
                if r2.endswith(suffix):
                    if suffix == "ion":
                        if word[-4] in "st":
                            word = word[:-3]
                            r1 = r1[:-3]
                            r2 = r2[:-3]
                    else:
                        word = word[:-len(suffix)]
                        r1 = r1[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                break

        # STEP 5
        if r2.endswith("l") and word[-2] == "l":
            word = word[:-1]
        elif r2.endswith("e"):
            word = word[:-1]
        elif r1.endswith("e"):
            if len(word) >= 4 and (word[-2] in self.__vowels or
                                   word[-2] in "wxY" or
                                   word[-3] not in self.__vowels or
                                   word[-4] in self.__vowels):
                word = word[:-1]


        word = word.replace("Y", "y")


        return word

class RussianStemmer(_LanguageSpecificStemmer):
    """
    The Russian Snowball stemmer.
    :cvar __perfective_gerund_suffixes: Suffixes to be deleted.
    :type __perfective_gerund_suffixes: tuple
    :cvar __adjectival_suffixes: Suffixes to be deleted.
    :type __adjectival_suffixes: tuple
    :cvar __reflexive_suffixes: Suffixes to be deleted.
    :type __reflexive_suffixes: tuple
    :cvar __verb_suffixes: Suffixes to be deleted.
    :type __verb_suffixes: tuple
    :cvar __noun_suffixes: Suffixes to be deleted.
    :type __noun_suffixes: tuple
    :cvar __superlative_suffixes: Suffixes to be deleted.
    :type __superlative_suffixes: tuple
    :cvar __derivational_suffixes: Suffixes to be deleted.
    :type __derivational_suffixes: tuple
    :note: A detailed description of the Russian
           stemming algorithm can be found under
           http://snowball.tartarus.org/algorithms/russian/stemmer.html
    """

    __perfective_gerund_suffixes = ("ivshis'", "yvshis'", "vshis'",
                                    "ivshi", "yvshi", "vshi", "iv",
                                    "yv", "v")
    __adjectival_suffixes = ('ui^ushchi^ui^u', 'ui^ushchi^ai^a',
                             'ui^ushchimi', 'ui^ushchymi', 'ui^ushchego',
                             'ui^ushchogo', 'ui^ushchemu', 'ui^ushchomu',
                             'ui^ushchikh', 'ui^ushchykh',
                             'ui^ushchui^u', 'ui^ushchaia',
                             'ui^ushchoi^u', 'ui^ushchei^u',
                             'i^ushchi^ui^u', 'i^ushchi^ai^a',
                             'ui^ushchee', 'ui^ushchie',
                             'ui^ushchye', 'ui^ushchoe', 'ui^ushchei`',
                             'ui^ushchii`', 'ui^ushchyi`',
                             'ui^ushchoi`', 'ui^ushchem', 'ui^ushchim',
                             'ui^ushchym', 'ui^ushchom', 'i^ushchimi',
                             'i^ushchymi', 'i^ushchego', 'i^ushchogo',
                             'i^ushchemu', 'i^ushchomu', 'i^ushchikh',
                             'i^ushchykh', 'i^ushchui^u', 'i^ushchai^a',
                             'i^ushchoi^u', 'i^ushchei^u', 'i^ushchee',
                             'i^ushchie', 'i^ushchye', 'i^ushchoe',
                             'i^ushchei`', 'i^ushchii`',
                             'i^ushchyi`', 'i^ushchoi`', 'i^ushchem',
                             'i^ushchim', 'i^ushchym', 'i^ushchom',
                             'shchi^ui^u', 'shchi^ai^a', 'ivshi^ui^u',
                             'ivshi^ai^a', 'yvshi^ui^u', 'yvshi^ai^a',
                             'shchimi', 'shchymi', 'shchego', 'shchogo',
                             'shchemu', 'shchomu', 'shchikh', 'shchykh',
                             'shchui^u', 'shchai^a', 'shchoi^u',
                             'shchei^u', 'ivshimi', 'ivshymi',
                             'ivshego', 'ivshogo', 'ivshemu', 'ivshomu',
                             'ivshikh', 'ivshykh', 'ivshui^u',
                             'ivshai^a', 'ivshoi^u', 'ivshei^u',
                             'yvshimi', 'yvshymi', 'yvshego', 'yvshogo',
                             'yvshemu', 'yvshomu', 'yvshikh', 'yvshykh',
                             'yvshui^u', 'yvshai^a', 'yvshoi^u',
                             'yvshei^u', 'vshi^ui^u', 'vshi^ai^a',
                             'shchee', 'shchie', 'shchye', 'shchoe',
                             'shchei`', 'shchii`', 'shchyi`', 'shchoi`',
                             'shchem', 'shchim', 'shchym', 'shchom',
                             'ivshee', 'ivshie', 'ivshye', 'ivshoe',
                             'ivshei`', 'ivshii`', 'ivshyi`',
                             'ivshoi`', 'ivshem', 'ivshim', 'ivshym',
                             'ivshom', 'yvshee', 'yvshie', 'yvshye',
                             'yvshoe', 'yvshei`', 'yvshii`',
                             'yvshyi`', 'yvshoi`', 'yvshem',
                             'yvshim', 'yvshym', 'yvshom', 'vshimi',
                             'vshymi', 'vshego', 'vshogo', 'vshemu',
                             'vshomu', 'vshikh', 'vshykh', 'vshui^u',
                             'vshai^a', 'vshoi^u', 'vshei^u',
                             'emi^ui^u', 'emi^ai^a', 'nni^ui^u',
                             'nni^ai^a', 'vshee',
                             'vshie', 'vshye', 'vshoe', 'vshei`',
                             'vshii`', 'vshyi`', 'vshoi`',
                             'vshem', 'vshim', 'vshym', 'vshom',
                             'emimi', 'emymi', 'emego', 'emogo',
                             'ememu', 'emomu', 'emikh', 'emykh',
                             'emui^u', 'emai^a', 'emoi^u', 'emei^u',
                             'nnimi', 'nnymi', 'nnego', 'nnogo',
                             'nnemu', 'nnomu', 'nnikh', 'nnykh',
                             'nnui^u', 'nnai^a', 'nnoi^u', 'nnei^u',
                             'emee', 'emie', 'emye', 'emoe',
                             'emei`', 'emii`', 'emyi`',
                             'emoi`', 'emem', 'emim', 'emym',
                             'emom', 'nnee', 'nnie', 'nnye', 'nnoe',
                             'nnei`', 'nnii`', 'nnyi`',
                             'nnoi`', 'nnem', 'nnim', 'nnym',
                             'nnom', 'i^ui^u', 'i^ai^a', 'imi', 'ymi',
                             'ego', 'ogo', 'emu', 'omu', 'ikh',
                             'ykh', 'ui^u', 'ai^a', 'oi^u', 'ei^u',
                             'ee', 'ie', 'ye', 'oe', 'ei`',
                             'ii`', 'yi`', 'oi`', 'em',
                             'im', 'ym', 'om')
    __reflexive_suffixes = ("si^a", "s'")
    __verb_suffixes = ("esh'", 'ei`te', 'ui`te', 'ui^ut',
                       "ish'", 'ete', 'i`te', 'i^ut', 'nno',
                       'ila', 'yla', 'ena', 'ite', 'ili', 'yli',
                       'ilo', 'ylo', 'eno', 'i^at', 'uet', 'eny',
                       "it'", "yt'", 'ui^u', 'la', 'na', 'li',
                       'em', 'lo', 'no', 'et', 'ny', "t'",
                       'ei`', 'ui`', 'il', 'yl', 'im',
                       'ym', 'en', 'it', 'yt', 'i^u', 'i`',
                       'l', 'n')
    __noun_suffixes = ('ii^ami', 'ii^akh', 'i^ami', 'ii^am', 'i^akh',
                       'ami', 'iei`', 'i^am', 'iem', 'akh',
                       'ii^u', "'i^u", 'ii^a', "'i^a", 'ev', 'ov',
                       'ie', "'e", 'ei', 'ii', 'ei`',
                       'oi`', 'ii`', 'em', 'am', 'om',
                       'i^u', 'i^a', 'a', 'e', 'i', 'i`',
                       'o', 'u', 'y', "'")
    __superlative_suffixes = ("ei`she", "ei`sh")
    __derivational_suffixes = ("ost'", "ost")

    def stem(self, word):
        """
        Stem a Russian word and return the stemmed form.
        :param word: The word that is stemmed.
        :type word: str or unicode
        :return: The stemmed form.
        :rtype: unicode
        """
        chr_exceeded = False
        for i in range(len(word)):
            if ord(word[i]) > 255:
                chr_exceeded = True
                break

        if chr_exceeded:
            word = self.__cyrillic_to_roman(word)

        step1_success = False
        adjectival_removed = False
        verb_removed = False
        undouble_success = False
        superlative_removed = False

        rv, r2 = self.__regions_russian(word)

        # Step 1
        for suffix in self.__perfective_gerund_suffixes:
            if rv.endswith(suffix):
                if suffix in ("v", "vshi", "vshis'"):
                    if (rv[-len(suffix) - 3:-len(suffix)] == "i^a" or
                            rv[-len(suffix) - 1:-len(suffix)] == "a"):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                        step1_success = True
                        break
                else:
                    word = word[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    step1_success = True
                    break

        if not step1_success:
            for suffix in self.__reflexive_suffixes:
                if rv.endswith(suffix):
                    word = word[:-len(suffix)]
                    r2 = r2[:-len(suffix)]
                    rv = rv[:-len(suffix)]
                    break

            for suffix in self.__adjectival_suffixes:
                if rv.endswith(suffix):
                    if suffix in ('i^ushchi^ui^u', 'i^ushchi^ai^a',
                                  'i^ushchui^u', 'i^ushchai^a', 'i^ushchoi^u',
                                  'i^ushchei^u', 'i^ushchimi', 'i^ushchymi',
                                  'i^ushchego', 'i^ushchogo', 'i^ushchemu',
                                  'i^ushchomu', 'i^ushchikh', 'i^ushchykh',
                                  'shchi^ui^u', 'shchi^ai^a', 'i^ushchee',
                                  'i^ushchie', 'i^ushchye', 'i^ushchoe',
                                  'i^ushchei`', 'i^ushchii`', 'i^ushchyi`',
                                  'i^ushchoi`', 'i^ushchem', 'i^ushchim',
                                  'i^ushchym', 'i^ushchom', 'vshi^ui^u',
                                  'vshi^ai^a', 'shchui^u', 'shchai^a',
                                  'shchoi^u', 'shchei^u', 'emi^ui^u',
                                  'emi^ai^a', 'nni^ui^u', 'nni^ai^a',
                                  'shchimi', 'shchymi', 'shchego', 'shchogo',
                                  'shchemu', 'shchomu', 'shchikh', 'shchykh',
                                  'vshui^u', 'vshai^a', 'vshoi^u', 'vshei^u',
                                  'shchee', 'shchie', 'shchye', 'shchoe',
                                  'shchei`', 'shchii`', 'shchyi`', 'shchoi`',
                                  'shchem', 'shchim', 'shchym', 'shchom',
                                  'vshimi', 'vshymi', 'vshego', 'vshogo',
                                  'vshemu', 'vshomu', 'vshikh', 'vshykh',
                                  'emui^u', 'emai^a', 'emoi^u', 'emei^u',
                                  'nnui^u', 'nnai^a', 'nnoi^u', 'nnei^u',
                                  'vshee', 'vshie', 'vshye', 'vshoe',
                                  'vshei`', 'vshii`', 'vshyi`', 'vshoi`',
                                  'vshem', 'vshim', 'vshym', 'vshom',
                                  'emimi', 'emymi', 'emego', 'emogo',
                                  'ememu', 'emomu', 'emikh', 'emykh',
                                  'nnimi', 'nnymi', 'nnego', 'nnogo',
                                  'nnemu', 'nnomu', 'nnikh', 'nnykh',
                                  'emee', 'emie', 'emye', 'emoe', 'emei`',
                                  'emii`', 'emyi`', 'emoi`', 'emem', 'emim',
                                  'emym', 'emom', 'nnee', 'nnie', 'nnye',
                                  'nnoe', 'nnei`', 'nnii`', 'nnyi`', 'nnoi`',
                                  'nnem', 'nnim', 'nnym', 'nnom'):
                        if (rv[-len(suffix) - 3:-len(suffix)] == "i^a" or
                                rv[-len(suffix) - 1:-len(suffix)] == "a"):
                            word = word[:-len(suffix)]
                            r2 = r2[:-len(suffix)]
                            rv = rv[:-len(suffix)]
                            adjectival_removed = True
                            break
                    else:
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                        adjectival_removed = True
                        break

            if not adjectival_removed:
                for suffix in self.__verb_suffixes:
                    if rv.endswith(suffix):
                        if suffix in ("la", "na", "ete", "i`te", "li",
                                      "i`", "l", "em", "n", "lo", "no",
                                      "et", "i^ut", "ny", "t'", "esh'",
                                      "nno"):
                            if (rv[-len(suffix) - 3:-len(suffix)] == "i^a" or
                                    rv[-len(suffix) - 1:-len(suffix)] == "a"):
                                word = word[:-len(suffix)]
                                r2 = r2[:-len(suffix)]
                                rv = rv[:-len(suffix)]
                                verb_removed = True
                                break
                        else:
                            word = word[:-len(suffix)]
                            r2 = r2[:-len(suffix)]
                            rv = rv[:-len(suffix)]
                            verb_removed = True
                            break

            if not adjectival_removed and not verb_removed:
                for suffix in self.__noun_suffixes:
                    if rv.endswith(suffix):
                        word = word[:-len(suffix)]
                        r2 = r2[:-len(suffix)]
                        rv = rv[:-len(suffix)]
                        break

        # Step 2
        if rv.endswith("i"):
            word = word[:-1]
            r2 = r2[:-1]

        # Step 3
        for suffix in self.__derivational_suffixes:
            if r2.endswith(suffix):
                word = word[:-len(suffix)]
                break

        # Step 4
        if word.endswith("nn"):
            word = word[:-1]
            undouble_success = True

        if not undouble_success:
            for suffix in self.__superlative_suffixes:
                if word.endswith(suffix):
                    word = word[:-len(suffix)]
                    superlative_removed = True
                    break
            if word.endswith("nn"):
                word = word[:-1]

        if not undouble_success and not superlative_removed:
            if word.endswith("'"):
                word = word[:-1]

        if chr_exceeded:
            word = self.__roman_to_cyrillic(word)

        return word

    @staticmethod
    def __regions_russian(word):
        """
        Return the regions RV and R2 which are used by the Russian stemmer.
        In any word, RV is the region after the first vowel,
        or the end of the word if it contains no vowel.
        R2 is the region after the first non-vowel following
        a vowel in R1, or the end of the word if there is no such non-vowel.
        R1 is the region after the first non-vowel following a vowel,
        or the end of the word if there is no such non-vowel.
        :param word: The Russian word whose regions RV and R2 are determined.
        :type word: str or unicode
        :return: the regions RV and R2 for the respective Russian word.
        :rtype: tuple
        :note: This helper method is invoked by the stem method of the subclass
               RussianStemmer. It is not to be invoked directly!
        """
        r1 = ""
        r2 = ""
        rv = ""

        vowels = ("A", "U", "E", "a", "e", "i", "o", "u", "y")
        word = (word.replace("i^a", "A")
                .replace("i^u", "U")
                .replace("e`", "E"))

        for i in range(1, len(word)):
            if word[i] not in vowels and word[i - 1] in vowels:
                r1 = word[i + 1:]
                break

        for i in range(1, len(r1)):
            if r1[i] not in vowels and r1[i - 1] in vowels:
                r2 = r1[i + 1:]
                break

        for i in range(len(word)):
            if word[i] in vowels:
                rv = word[i + 1:]
                break

        r2 = (r2.replace("A", "i^a")
              .replace("U", "i^u")
              .replace("E", "e`"))
        rv = (rv.replace("A", "i^a")
              .replace("U", "i^u")
              .replace("E", "e`"))

        return rv, r2

    @staticmethod
    def __cyrillic_to_roman(word):
        """
        Transliterate a Russian word into the Roman alphabet.
        A Russian word whose letters consist of the Cyrillic
        alphabet are transliterated into the Roman alphabet
        in order to ease the forthcoming stemming process.
        :param word: The word that is transliterated.
        :type word: unicode
        :return: the transliterated word.
        :rtype: unicode
        :note: This helper method is invoked by the stem method of the subclass
               RussianStemmer. It is not to be invoked directly!
        """
        word = (word.replace("\u0410", "a").replace("\u0430", "a")
                .replace("\u0411", "b").replace("\u0431", "b")
                .replace("\u0412", "v").replace("\u0432", "v")
                .replace("\u0413", "g").replace("\u0433", "g")
                .replace("\u0414", "d").replace("\u0434", "d")
                .replace("\u0415", "e").replace("\u0435", "e")
                .replace("\u0401", "e").replace("\u0451", "e")
                .replace("\u0416", "zh").replace("\u0436", "zh")
                .replace("\u0417", "z").replace("\u0437", "z")
                .replace("\u0418", "i").replace("\u0438", "i")
                .replace("\u0419", "i`").replace("\u0439", "i`")
                .replace("\u041A", "k").replace("\u043A", "k")
                .replace("\u041B", "l").replace("\u043B", "l")
                .replace("\u041C", "m").replace("\u043C", "m")
                .replace("\u041D", "n").replace("\u043D", "n")
                .replace("\u041E", "o").replace("\u043E", "o")
                .replace("\u041F", "p").replace("\u043F", "p")
                .replace("\u0420", "r").replace("\u0440", "r")
                .replace("\u0421", "s").replace("\u0441", "s")
                .replace("\u0422", "t").replace("\u0442", "t")
                .replace("\u0423", "u").replace("\u0443", "u")
                .replace("\u0424", "f").replace("\u0444", "f")
                .replace("\u0425", "kh").replace("\u0445", "kh")
                .replace("\u0426", "t^s").replace("\u0446", "t^s")
                .replace("\u0427", "ch").replace("\u0447", "ch")
                .replace("\u0428", "sh").replace("\u0448", "sh")
                .replace("\u0429", "shch").replace("\u0449", "shch")
                .replace("\u042A", "''").replace("\u044A", "''")
                .replace("\u042B", "y").replace("\u044B", "y")
                .replace("\u042C", "'").replace("\u044C", "'")
                .replace("\u042D", "e`").replace("\u044D", "e`")
                .replace("\u042E", "i^u").replace("\u044E", "i^u")
                .replace("\u042F", "i^a").replace("\u044F", "i^a"))

        return word

    @staticmethod
    def __roman_to_cyrillic(word):
        """
        Transliterate a Russian word back into the Cyrillic alphabet.
        A Russian word formerly transliterated into the Roman alphabet
        in order to ease the stemming process, is transliterated back
        into the Cyrillic alphabet, its original form.
        :param word: The word that is transliterated.
        :type word: str or unicode
        :return: word, the transliterated word.
        :rtype: unicode
        :note: This helper method is invoked by the stem method of the subclass
               RussianStemmer. It is not to be invoked directly!
        """
        word = (word.replace("i^u", "\u044E").replace("i^a", "\u044F")
                .replace("shch", "\u0449").replace("kh", "\u0445")
                .replace("t^s", "\u0446").replace("ch", "\u0447")
                .replace("e`", "\u044D").replace("i`", "\u0439")
                .replace("sh", "\u0448").replace("k", "\u043A")
                .replace("e", "\u0435").replace("zh", "\u0436")
                .replace("a", "\u0430").replace("b", "\u0431")
                .replace("v", "\u0432").replace("g", "\u0433")
                .replace("d", "\u0434").replace("e", "\u0435")
                .replace("z", "\u0437").replace("i", "\u0438")
                .replace("l", "\u043B").replace("m", "\u043C")
                .replace("n", "\u043D").replace("o", "\u043E")
                .replace("p", "\u043F").replace("r", "\u0440")
                .replace("s", "\u0441").replace("t", "\u0442")
                .replace("u", "\u0443").replace("f", "\u0444")
                .replace("''", "\u044A").replace("y", "\u044B")
                .replace("'", "\u044C"))

        return word
