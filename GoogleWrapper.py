# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:35 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""

import requests
import random
import os, os.path
from google.cloud import texttospeech

from .APIWrapper import APIWrapper


class GoogleWrapper(APIWrapper):
    client = texttospeech.TextToSpeechClient()

    def __init__(self):
        self.service_name = "Google Cloud Speech to Text"
        self.__get_voices()
        # self.voices = [
        #     "en-US-Wavenet-A",
        #     "en-US-Wavenet-B",
        #     "en-US-Wavenet-C",
        #     "en-US-Wavenet-D",
        #     "en-US-Wavenet-E",
        #     "en-US-Wavenet-F",
        #     "en-US-Wavenet-G",
        #     "en-US-Wavenet-H",
        #     "en-US-Wavenet-I",
        #     "en-US-Wavenet-J",
        # ]
        # if self.authenticate() and self.get_voices():
        #     print("Replica initialization successful\n")
        # else:
        #     raise Exception("Replica failed to initialize\n")

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

        failed_attempts = 0
        while (r.status_code == 401 or r.status_code == 403) and failed_attempts < 3:
            failed_attempts += 1
            print("Invalid credentials, try again")
            user_id = input("username: ")
            password = input("password: ")
            print()
            # send auth request
            r = requests.post(
                "https://api.replicastudios.com/auth", headers=headers, data=payload
            )

        if failed_attempts == 3:
            print("Could not vaildate Replica account")
            return False

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

    def __get_voices(self):
        self.voices = self.client.list_voices()
        print(self.voices)

    def generate_audio(self, output_folder, sentence, voice, clip_id):

        input_text = texttospeech.SynthesisInput(text=sentence)

        rand_gender = random.randint(0, 1)
        if rand_gender == 0:
            gender = texttospeech.SsmlVoiceGender.MALE
        else:
            gender = texttospeech.SsmlVoiceGender.FEMALE

        voice_config = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice,
            ssml_gender=gender,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        res = self.client.synthesize_speech(
            request={
                "input": input_text,
                "voice": voice_config,
                "audio_config": audio_config,
            }
        )

        try:
            filename, filesize = self.__save_audio(
                output_folder, res, self.voices_map[voice], clip_id
            )
            return res, filename, filesize
        except Exception as e:
            print(str(e))
            return 400, None, None

    def __save_audio(self, output_folder, res, voice, clip_id):
        audio_file = output_folder + "google_" + voice + "_" + str(clip_id) + ".wav"

        # save audio file
        try:
            with open(audio_file, "wb") as out:
                out.write(res.audio_content)
                print("Saved to file: " + audio_file + "\n")
        except:
            raise Exception("Could not save file " + audio_file + "\n")

        print("Saved to file: " + audio_file + "\n")

        return audio_file, os.path.getsize(audio_file)
