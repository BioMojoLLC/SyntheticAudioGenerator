# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:35 2021

@author: Ryan Hurlbut
"""

import requests

from SyntheticAudioGenerator.ServiceWrapper import ServiceWrapperInterface


class ReplicaWrapper(ServiceWrapperInterface):

    def authenticate(self):
        print("Enter Replica account information")
        user_id = input("username: ")
        password = input("password: ")

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = 'client_id=' + user_id + '&secret=' + password

        # send auth request
        r = requests.post('https://api.replicastudios.com/auth', headers = headers, data = payload)
        auth_token = r.json()['access_token']
        refresh_token = r.json()['refresh_token']

        print("Replica auth_token: " + auth_token)
        print("Replica refresh_token: " + refresh_token)