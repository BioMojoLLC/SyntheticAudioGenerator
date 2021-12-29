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

from SyntheticAudioGenerator.APIWrapper import APIWrapper


class ReplicaWrapper(APIWrapper):
    voices_map = {}  # maps voice uuid's to speaker names

    def __init__(self):
        if self.authenticate():
            if self.get_voices():
                print("Replica initialization successful\n")
            else:
                print("Replica failed to initialize\n")

    def authenticate(self):
        print("Enter Replica account information")
        user_id = input("username: ")
        password = input("password: ")
        print()

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = "client_id=" + user_id + "&secret=" + password

        # send auth request
        r = requests.post(
            "https://api.replicastudios.com/auth", headers=headers, data=payload
        )

        if r.status_code != 200:
            print(
                "Error authorizing Replica account - "
                + str(r.status_code)
                + " "
                + r.reason
            )
            return False
        else:
            auth_token = r.json()["access_token"]
            refresh_token = r.json()["refresh_token"]
            print("Replica auth_token: " + auth_token)
            print("Replica refresh_token: " + refresh_token + "\n")
            self.api_token = auth_token
            return True

    def get_voices(self):
        headers = {"Authorization": "Bearer " + self.api_token}

        r = requests.get("https://api.replicastudios.com/voice", headers=headers)

        if r.status_code != 200:
            print(
                "Error getting Replica voices - " + str(r.status_code) + " " + r.reason
            )
            return False
        for voice in r.json():
            self.voices.append(voice["uuid"])
            self.voices_map[voice["uuid"]] = voice["name"]

        print("Got " + str(len(self.voices)) + " voices from Replica\n")
        return True

    def generate_audio(self, output_folder, sentence, voice, clip_id):

        headers = {"Authorization": "Bearer " + self.api_token}
        # send audio generation request to replica
        r = requests.get(
            "https://api.replicastudios.com/speech",
            params={"txt": sentence, "speaker_id": voice},
            headers=headers,
        )

        res = r.json()

        if r.status_code != 200:
            print(
                "Error generating Replica audio - "
                + str(r.status_code)
                + " "
                + r.reason
            )
            return r.status_code, None, None

        if "error_code" in res.keys():
            print(
                "Error generating Replica audio file: "
                + res["error_code"]
                + " - "
                + res["error"]
            )
            return 400, None, None
        else:
            if "warning" in res.keys():
                print("Only partial results were obtained: " + res["warning"])
            else:
                print(
                    "Successfully generated Replica audio file in "
                    + str("{:.2f}".format(res["duration"]))
                    + " seconds"
                )
            try:
                filename, filesize = self.save_audio(
                    output_folder, res, self.voices_map[voice], clip_id
                )
                return res, filename, filesize
            except Exception as e:
                print(str(e))
                return 400, None, None

    def save_audio(self, output_folder, res, voice, clip_id):
        audio_file = output_folder + "replica_" + voice + "_" + str(clip_id) + ".wav"
        link = res["url"]

        # download audio file in 22050 hz
        resp = requests.get(link, allow_redirects=True)
        if resp.status_code != 200:
            raise Exception(
                "Coud not download Replica audio file - "
                + str(resp.status_code)
                + " "
                + resp.reason
            )
        else:
            # save audio file
            try:
                open(audio_file, "wb").write(resp.content)
            except:
                raise Exception("Could not save file " + audio_file + "\n")

            # resample audio to 16k hz
            try:
                x, sr = librosa.load(audio_file, sr=22050)
                y = librosa.resample(x, 22050, 16000)
                sf.write(audio_file, y, 16000, subtype="PCM_16")
            except:
                print("Could not resample audio file " + audio_file)

            print("Saved to file: " + audio_file + "\n")

            return audio_file, os.path.getsize(audio_file)
