# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:10 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""

class ServiceWrapperInterface:
    api_token = None

    def __init__(self, voices):
        self.voices = voices
        self.authenticate()

    def authenticate(self):
        pass

    def generateAudio(self, output_folder, sentence):
        pass

    def saveAudio(self):
        pass