# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:46 2021

@author: Ryan Hurlbut
"""
from settings import resemble_api_token
from ServiceWrapper import ServiceWrapper

import requests
import os, os.path
import datetime

class ResembleWrapper(ServiceWrapper):
    def __init__(self):
        print("B")
        self.voices = ['aaron','584fae8e', 'aiden', 'scarlet', 'sophia', 'elijah']
        self.__authenticate()
        self.__new_project()

    def __authenticate(self):
        self.auth_token = resemble_api_token
        
    def __new_project(self):
        name = "Auto-Generated on" #+ datetime.datetime.now().tostring()
        print(name)
        
    def generate_audio(self, audio_dir, sentence) -> tuple([int, str, int]):
        pass