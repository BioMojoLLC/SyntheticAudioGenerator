# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:35 2021

@author: Ryan Hurlbut
"""

import requests
import os, os.path
# import librosa
# import soundfile as sf

from SyntheticAudioGenerator.ServiceWrapper import ServiceWrapperInterface


class ReplicaWrapper(ServiceWrapperInterface):

    def authenticate(self):
        print("Enter Replica account information")
        user_id = input("username: ")
        password = input("password: ")
        print()

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = 'client_id=' + user_id + '&secret=' + password

        # send auth request
        r = requests.post('https://api.replicastudios.com/auth', headers = headers, data = payload)
        auth_token = r.json()['access_token']
        refresh_token = r.json()['refresh_token']

        print("Replica auth_token: " + auth_token)
        print("Replica refresh_token: " + refresh_token + "\n")

        self.api_token = auth_token

    def generateAudio(self, output_folder, sentence):
        replica_results = []
        total_dur = 0

        for voice_id in self.voices[:2]:
            headers = {
                'Authorization': 'Bearer ' + self.api_token
            }
            # send audio generation request to replica
            r = requests.get('https://api.replicastudios.com/speech', params={
                'txt': sentence,  'speaker_id': voice_id
            }, headers = headers)

            res = r.json()
            replica_results.append(res) 

            if not "error_code" in res.keys():
                total_dur += res["duration"]
            
            print("Elapsed time: " + str("{:<12.2f}".format(total_dur)) + " " + str(res))

        print("\nTotal elapsed time: " + str(total_dur) + " seconds")

        self.saveAudio(output_folder, replica_results)

    def saveAudio(self, output_folder, replica_results):
        id = len(os.listdir(output_folder)) # unique id starts at next value in sequence
        successes = 0

        for res in replica_results:
            link = res["url"]
            if not "error_code" in res.keys():
                # download audio file in 22050 hz
                audio_file = output_folder + "replica_" + self.voices[0] + "_" + str(id) + ".wav"
                resp = requests.get(link, allow_redirects=True)
                print("Attempted to download audio file - " + str(resp.status_code) + " " + resp.reason)

                # save audio file
                try:
                    open(audio_file, 'wb').write(resp.content)
                except:
                    print("Could not save file " + audio_file + "\n")
                    continue

                # resample audio to 16k hz
                # try:
                #     x, sr = librosa.load(audio_file, sr=22050)
                #     y = librosa.resample(x, 22050, 16000)
                #     sf.write(audio_file, y, 16000, subtype='PCM_16')
                #     successes += 1
                # except:
                #     print("Could not resample audio file " + audio_file)
                #     continue

                print("Saved to file: " + audio_file + "\n")
                id += 1
            else:
                print("Could not save file " + audio_file + " - check audio generation for errors" + "\n")

        print("Generated and saved " + str(successes) + " of " + str(len(replica_results)) + " audio files")