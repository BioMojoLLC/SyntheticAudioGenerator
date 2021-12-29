# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:46 2021

@author: Ryan Hurlbut
"""
from settings import resemble_api_token
from APIWrapper import APIWrapper

import requests
import datetime
import time

class ResembleWrapper(APIWrapper):
    def __init__(self):
        self.voices = ['aaron','584fae8e', 'aiden', 'scarlet', 'sophia', 'elijah']
        self.service_name = 'Resemble'
        self.__authenticate()
        self.__new_project()

    def __authenticate(self):
        self.auth_token = resemble_api_token
        
    def __new_project(self):
        name = "Auto-Generated Project on " + datetime.datetime.now().strftime("%m/%d/%Y, at %H:%M")
        print(name)
        url = "https://app.resemble.ai/api/v1/projects"
        headers = {
          'Authorization': 'Token token=' + self.auth_token,
          'Content-Type': 'application/json'
        }
        data = {
          'name': name,
          'description': name
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            self.project_uuid = response.json()["uuid"]
            print("Resemble project uuid:", self.project_uuid)
        else:
            raise Exception("Unable to make a new project for Resemble")
                
    def generate_audio(self, audio_dir: str, sentence: str, voice: str, clip_id: int()) -> tuple([int, str, int]):
        # Switch to False if the request was a success 

        clip_title = f"{self.service_name}-{voice}-{clip_id}"
        # POST the clip, sometimes we need to keep trying
        # If at first you don't succeed, try, try again
        while True:
            post_url =  f'https://app.resemble.ai/api/v1/projects/{self.project_uuid}/clips'
            post_headers = {'Authorization': f'Bearer {self.auth_token}', 'Content-Type': 'application/json'}
            data = {
                'data' : {"title": clip_title,
                          "body": f"<speak><p>{sentence}</p></speak>",
                          "voice" : f"{voice}"
                          } ,
                'precision' : "PCM_16",
                "output_format": 'wav'
                }
            post_response = requests.post(post_url, headers=post_headers, json=data)
            status = post_response.status_code
            if (status == 200):
                print(clip_title, "Created")
                break
            elif (status == 429):
                print("Resemble timed you out, waiting 2 seconds")
                time.sleep(2)
            else:
                print("Error:", status, " ocurred, please check the Resemble.ai documentation.")
                return (status, "", 0)
         
        # Get clip link with GET request
        while True:
            clip_uuid = post_response.json()['id']
            get_url = f"https://app.resemble.ai/api/v1/projects/{self.project_uuid}/clips/{clip_uuid}"
            get_headers = {
              'Authorization': f'Token token={self.auth_token}',
              'Content-Type': 'application/json'
            }
            get_response = requests.get(get_url, headers=get_headers)

            status = get_response.status_code
            if status == 200 and get_response.json()['link']:
                break
            elif status == 200 and not get_response.json()['link']:
                time.sleep(1) # try to get the link again
            elif status == 429:
                print("Resemble timed you out, waiting 2 seconds")
                time.sleep(2)
            else:
                print("Resemble generated a clip, but I can't get the link")
                print("Error:", status, " ocurred, please check the Resemble.ai documentation.")
                return (status, "", 0)
                
        # Download/ write file, this doesn't use the Resemble API
        link = get_response.json()['link'] 
        resp = requests.get(link, allow_redirects=True)
        status = resp.status_code
        if resp.status_code == 200:
            open(audio_dir + clip_title + ".wav", 'wb').write(resp.content)
            print(clip_title, "Saved")
            return 200, audio_dir + clip_title, resp.headers['content-length']
        else:
            print("Unable to download from link:", link)
            print("Error:", status)
            return (status, "", 0)