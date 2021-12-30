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

from data_processing import load_text

import os
import numpy as np
from collections import deque
import random
import csv

from ResembleWrapper import ResembleWrapper
from ReplicaWrapper import ReplicaWrapper

def bytes_to_mins(byte_count : int) -> float:
    # One minute of 16bit prec, sr 16k, mono channel wav file = 1950000 bytes
    #MIN_TO_BYTE = 1950000
    
    # Accurate for 44k sr
    MIN_TO_BYTE = 5350000
    return byte_count / MIN_TO_BYTE

if __name__ == '__main__':
    
    sentences_per_term = 10
    minutes_per_term = .05
    
    with open(keyword_file, 'r') as file:
        keywords = file.read().splitlines()
    
    # Load and sort text data into a dictionary {keyword:[text1,text2,. . .]}
    sentences = load_text(text_dir, keywords)
    
    # Print stats, pick a random selection from each list
    for k, v in sentences.items():
        n = len(v)
        print("Sentences found for", k, ":", n)
        sentences[k] = np.random.choice( v, min(sentences_per_term,n) , replace=False)
    
    print("Saving up to ", sentences_per_term, "sentences per term")
    print()
    
    if not os.path.exists(audio_dir):
        print("New directory created for audio")
        os.makedirs(audio_dir)
    else:
        print("Found existing directory:")
        print(audio_dir)
    


    print()
    print("Connecting to APIs")
    # For now APIs are hardcoded in. 
    apis = []
    apis.append(ResembleWrapper())
    apis.append(ReplicaWrapper())
    
    
    # Clip id's start at the number of previous recordings made.
    clip_id = len([name for name in os.listdir(audio_dir) if name.endswith(".wav")])
    print("Starting generator at id: ", clip_id)
    #%%
    # Convert terms, apis, and sentences for each term into queues.
    out_data = []
    for k, v in sentences.items():
        sentences[k] = deque(v)
    term_q = deque(keywords)
    term_bytes = {kw:0 for kw in keywords}
    api_q = deque(apis)

    # While we haven't made all of our target data, and we still CAN make data
    while len(term_q) and len(api_q):
        api = api_q.popleft()
        api_q.append(api)
        print("Switching to api:", api.service_name)
        
        for voice in api.voices:
            # Cut the loop if we hit data targets for all terms.
            if not len(term_q):
                break

            term = term_q.popleft()
            term_q.append(term)

            sentence = sentences[term].popleft()[:30] # TEMPORARY CUT OFF
            sentences[term].append(sentence)
            print()
            print("Making clip using:", api.service_name, ", for term:", term, "with voice:", voice)
            res, filename, size = api.generate_audio(audio_dir, sentence, voice, clip_id)

            if res == 200:
                out_data.append([filename, size, sentence])
                term_bytes[term] += size
                clip_id += 1
            else:
                print("Error:", res, ", Removing", api.service_name, "from api queue")
                api_q.remove(api)
                print("API queue:", *[a.service_name for a in api_q], len(api_q))
                break

            # Remove the term if we have hit the target for the term
            if bytes_to_mins(term_bytes[term]) >= minutes_per_term:
                print("Removing \"", term, "\" from term queue")
                term_q.remove(term)
            
        # Randomly offset the terms, after using an api. In the long run, 
        # this will ensure each term does not get used by the same api repeatedly. 
        if random.getrandbits(1) and len(term_q):
            term_q.append(term_q.popleft())    
    
    print("Finished\n")
    for t, b in term_bytes.items():
        print("Made", round(bytes_to_mins(b),3), "minutes of audio for term:", t, "\n")
        
    print("Writing", len(out_data), "rows to data.csv\n")
    with open(audio_dir + "data.csv", "a+", newline= "") as my_csv:
        csvWriter = csv.writer(my_csv, delimiter=',')
        csvWriter.writerows(out_data)
    #%%
    for api in apis:
        api.cleanup()