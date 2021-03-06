"""
Markov chain generator for making fantasy names and other made-up words.
"""
import string
import random
import sys
import collections
from optparse import OptionParser
from unicodedata import category
import csv

class CharList(collections.defaultdict):
    """Models the list of characters in the chain. The characters
    each have a corresponding int value, which is the proportion of
    those characters which follow the key pattern. """
    def __init__(self):
        """initializes the values to 0"""
        collections.defaultdict.__init__(self, int)

    def add(self, char):
        self[char] += 1

    def total(self):
        return sum(self.values())

    def choice(self):
        """returns a random value based on a key"""
        rnd = random.randrange(0, self.total())
        position = 0
        for char,count in self.items():
            position += count
            if rnd <= position:
                return char

class Chain(collections.defaultdict):
    """The histogram of letter probabilities. It is keyed by tuples,
    the length of which is defined by the lookback parameter."""
    class START(object):pass
    class END(object):pass
    def __init__(self, lookback = 2):
        collections.defaultdict.__init__(self, CharList)
        self.lookback = lookback

    def add(self,string):
        """ adds a word to the chain """
        key = [Chain.START] * self.lookback
        for char in string:
            self[tuple(key)].add(char)
            key.append(char)
            key.pop(0)
        self[tuple(key)].add(Chain.END)

class MarkovChain(collections.defaultdict):
    """ """
    def __init__(self, corpus_files, dictionary_file, lookback = 2):
        """ initializes the Markov object. """
        df = open(dictionary_file, 'r')
        self.dictionary = df.readlines()
        self.corpus_files = corpus_files
        self.lookback = lookback
        self.chain = Chain(self.lookback)
        self.load_corpuses()
        self.words = self.make_words()

    def load_corpuses(self):
        """loads the corpuses"""
        for file_path in self.corpus_files:
            f = open(file_path,'r')
            lines = f.readlines()
            for line in lines:
                for word in line.split():
                    word = ''.join(ch for ch in word if category(ch)[0] == 'L' )
                    self.chain.add(word.lower())

    def make_words(self):
        """ runs through the dictionary and makes a fantasy word for
        each entry in the 'real' dictionary """
        result = {}
        for w in self.dictionary:
            word = ""
            while True:
                word = self.make_word()
                if word not in result.values(): break
            result[w.strip()] = word
        return result

    def __str__(self):
        """ outputs the results of the corpuses applied to the
        dictionary file"""
        output = ""
        keys = list(self.words.keys())
        keys.sort()
        for key in keys:
            output += key + "," + self.words[key] + "\n"
        return output

    def make_word(self):
        """ makes a fantasy word from a series of random characters."""
        word = ""
        key = [Chain.START] * self.lookback
        while True:
            char = self.chain[tuple(key)].choice()
            if char == Chain.END: break
            word += char
            key += char
            key.pop(0)
        return word


def strip_chars(s, chars_to_strip = string.punctuation):
    """ Strips a series of characters from a string."""
    return s.translate(''.maketrans("",""), chars_to_strip)
