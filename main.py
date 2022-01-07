# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:48:38 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""

""" 
These will end up being CL options
These are relative paths, not absolute.
"""

from data_processing import import_text_data

import os
from collections import deque
import random
import csv
import argparse

from ResembleWrapper import ResembleWrapper
from ReplicaWrapper import ReplicaWrapper
# from GoogleWrapper import GoogleWrapper


def _get_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-a', '--audio_dir', type=os.path.abspath)
    parser.add_argument('-t', '--text_dir', type=os.path.abspath)
    parser.add_argument('-k', '--keywords', type=os.path.abspath)   
    parser.add_argument('-m', '--mins_per_term', type=int)
    
    args = parser.parse_args()
    
    if not os.path.exists(args.text_dir):
        raise SystemExit( f'\n{args.text_dir} \ndoes not exist')
    if not os.path.exists(args.keywords):
        raise SystemExit( f'\n{args.keywords} \ndoes not exist')

    return args

def _bytes_to_mins(byte_count : int) -> float:
    # Accurate for 16k sr (mono channel)
    MIN_TO_BYTE = 1950000
    
    # Accurate for 44k sr
    # MIN_TO_BYTE = 5350000
    return byte_count / MIN_TO_BYTE

def _get_next_recording_number(directory:str) ->int:
    return len([name for name in os.listdir(directory) if name.endswith(".wav")])

def main():
    args = _get_args()
    
    with open(args.keywords, 'r') as file:
        keywords = file.read().splitlines()
    
    # Load and sort text data into a dictionary {keyword:[text1,text2,. . .]}
    sentences = import_text_data(args.text_dir, keywords)
    
    if not os.path.exists(args.audio_dir):
        os.makedirs(args.audio_dir)
        print("New directory created for audio:")
    else:
        print("Using existing directory:")
    
    print(args.audio_dir)
    
    print("\nConnecting to APIs")
    # For now APIs are hardcoded in. 
    apis = []
    apis.append(ResembleWrapper())
    apis.append(ReplicaWrapper())
    # apis.append(GoogleWrapper())
    
    clip_id = _get_next_recording_number(args.audio_dir)
    print("Starting generator at id: ", clip_id)

    # Convert terms, apis, and sentences for each term into queues.
    term_q = deque(keywords)
    api_q = deque(apis)
    for k, v in sentences.items():
        sentences[k] = deque(v)

    out_data = []
    term_bytes = {kw:0 for kw in keywords}
    
    try:
        # While we haven't made all of our target data, AND we still have an api to use
        while len(term_q) and len(api_q):
            api = api_q.popleft()
            api_q.append(api)
            print("\nSwitching to api:", api.service_name)
            
            for voice in api.voices:
                # Cut the loop if we hit data targets for all terms.
                if not len(term_q):
                    break
    
                term = term_q.popleft()
                term_q.append(term)

                sentence = sentences[term].popleft()
                sentences[term].append(sentence)
                print("\nMaking clip using:", api.service_name, ", for term:", term, ", with voice:", voice)
                res, filename, size = api.generate_audio(args.audio_dir, sentence, voice, clip_id)

                if res == 200:
                    out_data.append([filename, size, sentence])
                    term_bytes[term] += size
                    clip_id += 1
                else:
                    print("Error:", res, ", Removing", api.service_name, "from api queue")
                    api_q.remove(api)
                    print("Current API queue:", [a.service_name for a in api_q], len(api_q))
                    break
    
                # Remove the term if we have hit the target for the term
                if _bytes_to_mins(term_bytes[term]) >= args.mins_per_term:
                    print("\nRemoving \"", term.strip(), "\" from term queue")
                    term_q.remove(term)
                
            # Randomly offset the terms, after using an api. In the long run, 
            # this will ensure each term does not get used by the same api repeatedly. 
            if random.getrandbits(1) and len(term_q):
                term_q.append(term_q.popleft())    
        
        print("\nFinished")
        for t, b in term_bytes.items():
            print("Made", round(_bytes_to_mins(b),3), "minutes of audio for term:", t)
    
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt")
    except Exception as e:
        print("Exception occured during program execution")
        print(e)

    print("\nWriting", len(out_data), "rows to data.csv\n")
    with open(os.path.join(args.audio_dir, "data.csv"), "a+", newline= "") as my_csv:
        csvWriter = csv.writer(my_csv, delimiter=',')
        csvWriter.writerows(out_data)

    for api in apis:
        api.cleanup()
        print("Cleaned", api.service_name)
        

if __name__ == '__main__':
    main()