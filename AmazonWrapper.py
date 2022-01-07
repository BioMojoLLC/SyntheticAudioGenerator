# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:35 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""

import os, os.path
from settings import amazon_access_key_id
from settings import amazon_secret_access_key
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import wave

from APIWrapper import APIWrapper


class AmazonWrapper(APIWrapper):
    session = None
    client = None

    def __init__(self):
        self.service_name = "Amazon Polly"
        if self.__authenticate() and self.__get_voices():
            print("Amazon initialization successful\n")
        else:
            raise Exception("Amazon failed to initialize\n")

    def __authenticate(self):
        try:
            self.session = Session(
                aws_access_key_id=amazon_access_key_id,
                aws_secret_access_key=amazon_secret_access_key,
                region_name="us-east-1",
            )
            self.client = self.session.client("polly")
        except Exception as e:
            print(str(e))
            return False
        return True

    def __get_voices(self):
        res = {}
        la_codes = ["en-US", "en-GB", "en-AU"]
        try:
            for la_code in la_codes:
                res = self.client.describe_voices(
                    Engine="neural",
                    LanguageCode=la_code,
                    IncludeAdditionalLanguageCodes=False,
                )
                for voice in res["Voices"]:
                    self.voices.append(voice["Id"])
        except:
            print("Error getting Amazon voices")
            return False

        print("Got " + str(len(self.voices)) + " voices from Amazon")
        print(self.voices)
        return True

    def generate_audio(self, output_folder, sentence, voice, clip_id):
        try:
            # Request speech synthesis
            res = self.client.synthesize_speech(
                Text=sentence, OutputFormat="pcm", VoiceId=voice
            )

            try:
                filename, filesize = self.__save_audio(
                    output_folder, res, voice, clip_id
                )
                return 200, filename, filesize
            except Exception as e:
                print("Exception while saving audio file: ", str(e))
                return 400, None, None
        except (BotoCoreError, ClientError) as error:
            print(error)
            return 400, None, None

    def __save_audio(self, output_folder, res, voice, clip_id):
        audio_file = "amazon_" + voice + "_" + str(clip_id)
        audio_path_pcm = output_folder + audio_file + ".pcm"
        audio_path_wav = output_folder + audio_file + ".wav"

        if "AudioStream" in res:
            with closing(res["AudioStream"]) as stream:
                try:
                    with open(audio_path_pcm, "wb") as file:
                        file.write(stream.read())
                except:
                    raise Exception("Could not save file " + audio_file + "\n")

        # convert from pcm to wav
        with open(audio_path_pcm, "rb") as pcmfile:
            pcmdata = pcmfile.read()
        with wave.open(audio_path_wav, "wb") as wavfile:
            wavfile.setparams((1, 2, 16000, 0, "NONE", "NONE"))
            wavfile.writeframes(pcmdata)

        os.remove(audio_path_pcm)

        print("Successfully created: " + audio_file + ".wav")

        return audio_file, os.path.getsize(audio_path_wav)

    def cleanup(self):
        pass
