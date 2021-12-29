# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:10 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""

class ServiceWrapper:
    api_token = None
    voices = []

    """Constructor for Service classes. Authenticates the service and then populates voices with the available voices.
    """
    def __init__(self):
        print("A")
        if self.authenticate():
            self.get_voices()

    """Authenticates the service. Will be different for every service.

        RETURNS
            the api token if successful. None otherwise
    """
    def authenticate(self):
        pass

    """Populates voices with the service's available voices.
    """
    def get_voices(self):
        pass

    """Generates audio for the sentence on all of the voices in voices.

        RETURNS
            The response from the generation request, the filename of the saved file, the filesize
    """
    def generate_audio(self, output_folder, sentence):
        pass

    """Used internally in the service class to save generated audio files.

        RETURNS
            The filename of the saved file, the filesize
    """
    def save_audio(self, output_folder):
        pass