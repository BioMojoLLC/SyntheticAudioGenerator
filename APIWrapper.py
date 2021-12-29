# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:10 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""


class APIWrapper:
    api_token = None
    voices = []
    num_voices = 0

    """Constructor for API wrapper classes.
        This method must be implemented vy all API wrapper sub-classes.
    """

    def __init__(self):
        pass

    """Generates audio for the sentence on all of the voices in voices.
        This method must be implemented by all API wrapper sub-classes.

        RETURNS
            The response from the generation request, the filename of the saved file, the filesize
    """

    def generate_audio(self, output_folder, sentence, voice, clip_id):
        pass
