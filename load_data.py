# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 13:39:27 2021

@author: Ryan Hurlbut
"""

import os

def prep_text(text_dir, keywords:[]) -> dict:
    """Loads text data from the text directory, and only keeps sentences associated
        with a key word. 
        
        RETURNS
            A dictionary with keywords as the key, and a list of sentences as the value
    """
    sentences = {kw:[] for kw in keywords}
    text_files = [filename for filename in os.listdir(text_dir) if filename.endswith(".txt")]
    for filename in text_files:
        print('Reading ---',  filename)
        contents = []
        with open(text_dir + filename, 'r') as file:
            contents = [line.strip() for line in file.readlines()]
        
        for line in contents:
            for kw in keywords:
                if ' ' + kw + ' ' in line:
                    sentences[kw].append(line)
                    break # no need to continue, we found a matching line of text
    return sentences
    