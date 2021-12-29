# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:35 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""

import requests
import os, os.path
import librosa
import soundfile as sf
import random

from SyntheticAudioGenerator.ServiceWrapper import ServiceWrapperInterface


class ReplicaWrapper(ServiceWrapperInterface):
    voices_map = {} # maps voice uuid's to speaker names

    def authenticate(self):
        print("Enter Replica account information")
        user_id = input("username: ")
        password = input("password: ")
        print()

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = 'client_id=' + user_id + '&secret=' + password

        # send auth request
        r = requests.post('https://api.replicastudios.com/auth', headers = headers, data = payload)
        auth_token = None
        try:
            auth_token = r.json()['access_token']
            refresh_token = r.json()['refresh_token']
        except:
            print("Replica authentication failed")
            return False

        print("Replica auth_token: " + auth_token)
        print("Replica refresh_token: " + refresh_token + "\n")

        self.api_token = auth_token
        return True

    def get_voices(self):
        headers = {
            'Authorization': 'Bearer ' + self.api_token
        }

        r = requests.get('https://api.replicastudios.com/voice', headers = headers)

        for voice in r.json():
            self.voices.append(voice["uuid"])
            self.voices_map[voice["uuid"]] = voice["name"]

        print("Got " + str(len(self.voices)) + " voices from Replica\n")

    def generate_audio(self, output_folder, sentence):
        voice_id = self.voices[random.randint(0, len(self.voices) - 1)]

        headers = {
            'Authorization': 'Bearer ' + self.api_token
        }
        # send audio generation request to replica
        r = requests.get('https://api.replicastudios.com/speech', params={
            'txt': sentence,  'speaker_id': voice_id
        }, headers = headers)

        res = r.json()

        if "error_code" not in res.keys():
            print("Successfully generated Replica audio file in " + str("{:.2f}".format(res["duration"])) + " seconds")
        else:
            print("Error generating Replica audio file: " + res["error_code"] + " - " + res["error"])

        filename, filesize = self.save_audio(output_folder, res, self.voices_map[voice_id])
        
        return res, filename, filesize

    def save_audio(self, output_folder, res, voice):
        id = len(os.listdir(output_folder)) # unique id starts at next value in sequence
        audio_file = output_folder + "replica_" + voice + "_" + str(id) + ".wav"
        link = res["url"]

        if "error_code" not in res.keys():
            # download audio file in 22050 hz
            resp = requests.get(link, allow_redirects=True)
            print("Attempted to download Replica audio file - " + str(resp.status_code) + " " + resp.reason)

            # save audio file
            try:
                open(audio_file, 'wb').write(resp.content)
            except:
                print("Could not save file " + audio_file + "\n")

            # resample audio to 16k hz
            try:
                x, sr = librosa.load(audio_file, sr=22050)
                y = librosa.resample(x, 22050, 16000)
                sf.write(audio_file, y, 16000, subtype='PCM_16')
            except:
                print("Could not resample audio file " + audio_file)

            print("Saved to file: " + audio_file + "\n")
            id += 1
        else:
            print("Could not save file " + audio_file + " - check audio generation for errors" + "\n")

        return audio_file, os.path.getsize(audio_file)