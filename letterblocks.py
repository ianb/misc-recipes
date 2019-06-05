from copy import copy
from string import ascii_lowercase as alphabet

class Invalid(Exception):
    pass

def find_letters(words, letter_limit=6):
    words = [set(word.lower()) for word in words]
    leftover = set(alphabet)
    leftover -= words[0]
    blocks = [(set([x]), copy(leftover)) for x in words[0]]
    words.pop(0)
    iterate(blocks, leftover, letter_limit)

def iterate(blocks, leftover, letter_limit):
    for letters, options in blocks:
        for word in words:
            if letters & word:
                options -= word
    for letters, options in blocks:
        if len(letters) == letter_limit:
            options.clear()
    while 1:
        did_anything = False
        for letter in leftover:
            if len(options for letters, options in blocks
                   if letter in options) == 1:
                for letters, options in blocks:
                    if letter in options:
                        letters.add(letter)
                        options.remove(letter)
                        did_anything = True
        if not did_anything:
            break


    
    
