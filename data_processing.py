# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 13:39:27 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""

import os
import librosa
import soundfile as sf
import re
import random
import numpy as np


def import_text_data(text_dir, keywords: [], num_to_keep: int = 20) -> dict:
    """
    Loads text data from the text directory, and only keeps sentences associated
    with a key word.

    Defaults to keep only 10 sentences per term.
    
    Returns
        dict: keywords as the key, and a list of sentences as the value
    """
    sentences = {kw: [] for kw in keywords}
    text_files = [
        filename for filename in os.listdir(text_dir) if filename.endswith(".txt")
    ]
    for filename in text_files:
        print("Reading --->", filename)
        contents = []
        with open(os.path.join(text_dir, filename), "r") as file:
            contents = [line.strip() for line in file.readlines()]

        for line in contents:
            for kw in keywords:
                if " " + kw + " " in line:
                    sentences[kw].append(line)
                    break  # no need to continue, we found a matching line of text

    # Print stats, pick a random selection from each list
    for k, v in sentences.items():
        n = len(v)
        print("Sentences found for", k, ":", n)
        v = np.random.choice(v, min(num_to_keep, n), replace=False)
        v = [cut_sentence(s, k) for s in v]
        sentences[k] = v

    print("Only using up to ", num_to_keep, "sentences per term")
    print()
    return sentences


def cut_sentence(input_string: str, keyword: str, target_ratio: float = 1 / 17) -> str:
    """Cut the sentence to maintain the ratio : count(keyword) / word_count(sentence)

    This function is case sensitive!

    Parameters
        input_string: The string for which to cut down the wordcount ratio

        keyword: The word to leave buffer words in front of and behind

        target_ratio: Must be a float between 0 and 1. This is the ratio used to determine 
                       how many words to keep, related to how many ocurrances of the keyword
                       there are

    Returns
        string: The cut sentence
    """
    s = input_string.split(" ")
    l = len(s)
    count = sum(1 for _ in re.finditer(r"\b%s\b" % re.escape(keyword), input_string))
    if not count:
        return input_string
    r = count / l
    if r < target_ratio:
        target_count = count * (1 / target_ratio)
        key_indeces = [i for i in range(l) if s[i] == keyword]
        first = key_indeces[0]
        last = key_indeces[-1]
        num_between = last - first + 1
        keep = target_count - num_between
        s = s[int(max(0, first - (keep / 2))) : int(last + (keep / 2)) + 1]
    return " ".join(s)


def get_phonetic_sentence(sentence: str, phonetic_dict: dict) -> str:
    for w, p_list in phonetic_dict.items():
        if p_list:
            p = random.choice(p_list)
            sentence = sentence.replace(w, p)
        else:
            print("Term:", w, "has no phonetic version")

    return sentence


def resample_file(
    audio_path: str,
    new_sample_rate: int = 16000,
    pcm_rate: str = "PCM_16",
) -> None:
    """
    Resample given audio file with default sample rate of 16k hz and default PCM_16
    """
    # resample audio to 16k hz
    try:
        data, old_sample_rate = sf.read(audio_path)
        y = librosa.resample(data, old_sample_rate, new_sample_rate)
        sf.write(audio_path, y, new_sample_rate, subtype=pcm_rate)
        print(
            "Resampled "
            + audio_path
            + " from "
            + str(old_sample_rate)
            + "hz to "
            + str(new_sample_rate)
            + "hz"
        )
    except:
        print("Could not resample audio file " + audio_path)
