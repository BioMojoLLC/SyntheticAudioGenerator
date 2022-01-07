# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:35 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""
from settings import replica_username
from settings import replica_password
from settings import keyword_file


import requests
import os, os.path
import pronouncing

from APIWrapper import APIWrapper
import data_processing as dp


class ReplicaWrapper(APIWrapper):
    voices_map = {}  # maps voice uuid's to speaker names

    def __init__(self):
        self.service_name = "Replica API"
        if self.__authenticate() and self.__get_voices() and self.__setup_phonetics():
            print("Replica initialization successful\n")
        else:
            raise Exception("Replica failed to initialize\n")

    def __authenticate(self):
        user_id = replica_username
        password = replica_password

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
            print("Replica successfully authorized")
            self.api_token = auth_token
            return True

    def __get_voices(self):
        headers = {"Authorization": "Bearer " + self.api_token}

        r = requests.get("https://api.replicastudios.com/voice", headers=headers)

        if r.status_code != 200:
            print(
                "Error getting Replica voices - " + str(r.status_code) + " " + r.reason
            )
            return False
        self.voices = []
        self.voices_map = {}
        for voice in r.json():
            self.voices.append(voice["uuid"])
            self.voices_map[voice["uuid"]] = voice["name"]

        print("Got " + str(len(self.voices)) + " voices from Replica")
        return True

    def __setup_phonetics(self) -> bool:
        self.phonetic_dict = {}
        with open(keyword_file, "r") as file:
            keywords = file.read().splitlines()

        for kw in keywords:
            phones = pronouncing.phones_for_word(kw)  # returns a list of pronunciations
            phones = [
                "".join(
                    [i for i in phone if not i.isdigit() and not i.isspace()]
                ).lower()
                for phone in phones
            ]  # remove pesky digits
            phones = set(phones)  # remove duplicates
            phones = list(phones)[
                :5
            ]  # Keep only 5? I shouldn't be using magic numbers like this!!
            self.phonetic_dict[kw] = phones

        print("Phonetic dictionary constructed")
        return True

    def generate_audio(self, output_folder, sentence, voice, clip_id):

        # Simple conversion of specific terms
        sentence = dp.get_phonetic_sentence(sentence, self.phonetic_dict)

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
                filename, filesize = self.__save_audio(
                    output_folder, res, self.voices_map[voice], clip_id
                )
                return 200, filename, filesize
            except Exception as e:
                print("Exception while saving audio file:", res, str(e))
                return 400, None, None

    def __save_audio(self, output_folder, res, voice, clip_id):
        audio_file = "replica_" + voice + "_" + str(clip_id) + ".wav"
        audio_path = output_folder + audio_file
        link = res["url"]

        # download audio file in 22050 hz
        resp = requests.get(link, allow_redirects=True)
        if resp.status_code != 200:
            raise Exception(
                "Could not download Replica audio file - "
                + str(resp.status_code)
                + " "
                + resp.reason
            )
        else:
            # save audio file
            try:
                open(audio_path, "wb").write(resp.content)
            except:
                raise Exception("Could not save file " + audio_file + "\n")

            dp.resample_file(audio_path, 16000, "PCM_16")

            print("Successfully created: " + audio_file)

            return audio_file, os.path.getsize(audio_path)
