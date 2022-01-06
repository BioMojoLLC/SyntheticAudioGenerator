# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:46 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""
from settings import resemble_api_token

from APIWrapper import APIWrapper

import requests
import datetime
import time
import os

import data_processing as dp


class ResembleWrapper(APIWrapper):
    def __init__(self):
        self.voices = ["aaron", "584fae8e", "aiden"]  # , 'scarlet', 'sophia', 'elijah']
        self.service_name = "Resemble"
        if self.__authenticate() and self.__new_project():
            print("Resemble initialization successful\n")
        else:
            raise Exception("Resemble failed to initialize\n")

    def __authenticate(self):
        self.api_token = resemble_api_token
        return True

    def __new_project(self):
        name = "Auto-Generated Project on " + datetime.datetime.now().strftime(
            "%m/%d/%Y, at %H:%M"
        )
        print(name)
        url = "https://app.resemble.ai/api/v1/projects"
        headers = {
            "Authorization": "Token token=" + self.api_token,
            "Content-Type": "application/json",
        }
        data = {"name": name, "description": name}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            self.project_uuid = response.json()["uuid"]
            print("Resemble project uuid:", self.project_uuid)
            return True
        else:
            raise Exception("Unable to make a new project for Resemble")

    def generate_audio(
        self, audio_dir: str, sentence: str, voice: str, clip_id: int()
    ) -> tuple([int, str, int]):
        # Switch to False if the request was a success

        clip_name = f"{self.service_name}-{voice}-{clip_id}.wav"
        # POST the clip, sometimes we need to keep trying
        # If at first you don't succeed, try, try again
        while True:
            post_url = (
                f"https://app.resemble.ai/api/v1/projects/{self.project_uuid}/clips"
            )
            post_headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            }
            data = {
                "data": {
                    "title": clip_name,
                    "body": f"<speak><p><prosody rate='75%'>{sentence}</prosody></p></speak>",
                    "voice": f"{voice}",
                },
                "precision": "PCM_16",
                "output_format": "wav",
            }
            post_response = requests.post(post_url, headers=post_headers, json=data)
            status = post_response.status_code
            if status == 200:
                break
            elif status == 429:
                print("Resemble timed you out, waiting 2 seconds")
                time.sleep(2)
            else:
                print(
                    "Error:",
                    status,
                    " ocurred, please check the Resemble.ai documentation.",
                )
                return status, None, None

        # Get clip link with GET request
        while True:
            clip_uuid = post_response.json()["id"]
            get_url = f"https://app.resemble.ai/api/v1/projects/{self.project_uuid}/clips/{clip_uuid}"
            get_headers = {
                "Authorization": f"Token token={self.api_token}",
                "Content-Type": "application/json",
            }
            get_response = requests.get(get_url, headers=get_headers)

            status = get_response.status_code
            if status == 200 and get_response.json()["link"]:
                break
            elif status == 200 and not get_response.json()["link"]:
                time.sleep(1)  # try to get the link again
            elif status == 429:
                print("Resemble timed you out, waiting 2 seconds")
                time.sleep(2)
            else:
                print("Resemble generated a clip, but I can't get the link")
                print(
                    "Error:",
                    status,
                    " ocurred, please check the Resemble.ai documentation.",
                )
                return status, None, None

        # Download/ write file, this doesn't use the Resemble API
        link = get_response.json()["link"]
        resp = requests.get(link, allow_redirects=True)
        status = resp.status_code

        if resp.status_code == 200:

            audio_path = os.path.join(audio_dir, clip_name)
            open(audio_path, "wb").write(resp.content)
            dp.resample_file(audio_path, 16000, "PCM_16")
            size = os.path.getsize(audio_path)

            print("Successfully created:", clip_name)
            return status, clip_name, size
        else:
            print("Unable to download from link:", link)
            print("Error:", status)
            return status, None, None

    def cleanup(self):
        delete_url = f"https://app.resemble.ai/api/v1/projects/{self.project_uuid}"
        headers = {
            "Authorization": "Token token=" + self.api_token,
            "Content-Type": "application/json",
        }
        delete_res = requests.delete(delete_url, headers=headers)

        status = delete_res.status_code
        if status == 204:
            return
        elif status == 429:
            time.sleep(2)  # Try again, we went too fast
        else:
            print("Error while cleaning up Resemble:", status)
