# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 13:39:27 2021

@author: Ryan Hurlbut
"""

import os
import librosa
import soundfile as sf


def load_text(text_dir, keywords: []) -> dict:
    """Loads text data from the text directory, and only keeps sentences associated
    with a key word.

    RETURNS
        A dictionary with keywords as the key, and a list of sentences as the value
    """
    sentences = {kw: [] for kw in keywords}
    text_files = [
        filename for filename in os.listdir(text_dir) if filename.endswith(".txt")
    ]
    for filename in text_files:
        print("Reading ---", filename)
        contents = []
        with open(text_dir + filename, "r") as file:
            contents = [line.strip() for line in file.readlines()]

        for line in contents:
            for kw in keywords:
                if " " + kw + " " in line:
                    sentences[kw].append(line)
                    break  # no need to continue, we found a matching line of text
    return sentences


def cut_sentence(sentence: str, keyword: str, ratio: float = 0.05) -> str:
    """Cut the sentence to maintain the ratio : count(keyword) / word_count(sentence)

    The default ratio is 1 key word for every 20 words.

    RETURNS
        The cut sentence as a string, if the sentence has a ratio of number of keywords to total words
        that is greater than the given ratio, the returned sentence will be exactly at the given ratio.
    """
    pass


def resample_file(
    audio_path: str,
    old_sample_rate: int,
    new_sample_rate: int = 16000,
    pcm_rate: str = "PCM_16",
) -> None:
    """Resample given audio file with default sample rate of 16k hz and default PCM_16"""
    # resample audio to 16k hz
    try:
        x, sr = librosa.load(audio_path, sr=old_sample_rate)
        y = librosa.resample(x, old_sample_rate, new_sample_rate)
        sf.write(audio_path, y, new_sample_rate, subtype=pcm_rate)
    except:
        print("Could not resample audio file " + audio_path)
