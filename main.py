# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:48:38 2021

@author: Ryan Hurlbut
"""

""" These will end up being CL options"""
from settings import audio_dir
from settings import text_dir
from settings import keyword_file
from settings import out_file
from load_data import prep_text


import os
import numpy as np
from collections import deque
import random
import csv

import ResembleWrapper
import ReplicaWrapper

def bytes_to_mins(byte_count : int) -> float:
    # TODO
    pass

if __name__ == '__main__':
    sentences_per_term = 5
    minutes_per_term = 10
    
    with open(keyword_file, 'r') as file:
        keywords = file.read().splitlines()
    
    # Load and sort text data into a dictionary {keyword:[text1,text2,. . .]}
    sentences = prep_text(text_dir, keywords)
    
    # Print stats, pick a random selection from each list
    for k, v in sentences.items():
        print("Sentences found for", k, ":", len(v))
        sentences[k] = np.random.choice( v, sentences_per_term , replace=False)
    
    print("Saving up to ", sentences_per_term, "sentences per term")
    
    # APIS that you wish to use. We may add these as command line options. 
    # For now they are hardcoded in. 
    apis = []
    apis.append(ResembleWrapper())
    apis.append(ReplicaWrapper())
    
    # Convert the lists to queues, we want to generate on each term using a queue of sentences.
    for v in sentences.values():
        v = deque(v)

    # Rotate through terms and API's, until we have made enough for each term or run out of service resources
    out_data = []
    term_q = deque(keywords)
    term_bytes = {kw:0 for kw in keywords}
    api_q = deque(apis)
    # while we can still make data, and we haven't made all of our target data
    while len(term_q) and len(api_q):
        api = api_q.pop_left()
        api_q.append(api)
        # Use all the voices in an api once
        for _ in range(api.num_voices):
            # Cut the loop if we hit data targets for all terms.
            if not len(term_q):
                break
            term = term_q.pop_left()
            print("API:", api.name, ", Term:", term)
            sentence = sentences[term].pop_left()
            sentences[term].append(sentence)
            
            resp, filename, size = api.generate_audio(text_dir, sentence) 
            if resp == 200:
                out_data.append([filename, size, sentence])
                term_bytes[term] += size
            else:
                api_q.remove(api)
                print("Error:", resp, ", Removing", api.name, "from api queue")
                
            # Add term to the queue if we still need more data for it
            if bytes_to_mins(term_bytes[term]) < minutes_per_term:
                term_q.append(term)
            
        # Randomly offset the terms, after using an api, 
        # this will ensure each term does not get used by the same api repeatedly. 
        if random.getrandbits(1):
            term_q.append(term_q.pop_left)    
        
    for t, b in term_bytes:
        print(b, "Bytes made for term:", t)
        
    # with open(audio_dir + out_file, 'w', newline='' ) as file:
    #     writer = csv.writer(file, delimeter=',')
    #     writer.writerows(out_data)