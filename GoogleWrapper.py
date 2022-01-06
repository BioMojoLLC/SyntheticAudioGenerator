# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 12:49:35 2021

@author: Ryan Hurlbut
@author: Jacob Bream
"""

import random
import os, os.path
from google.cloud import texttospeech
from settings import google_auth_key_path
import soundfile as sf
import data_processing as dp

from APIWrapper import APIWrapper


class GoogleWrapper(APIWrapper):
    client = None

    def __init__(self):
        self.service_name = "Google Cloud Text to Speech"
        if self.__authenticate() and self.__get_voices():
            print("Google Cloud Text to Speech initialization successful\n")
        else:
            raise Exception("Google Cloud Text to Speech failed to initialize\n")

    def __authenticate(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_auth_key_path
        try:
            self.client = texttospeech.TextToSpeechClient()
            print("Google Cloud Text to Speech successfully authorized")
            return True
        except:
            print("Error authorizing Google Cloud Text to Speech")
            return False

    def __get_voices(self):
        voices_dict = self.client.list_voices()
        try:
            for voice in voices_dict.voices:
                for language_code in voice.language_codes:
                    if language_code == "en-GB" or language_code == "en-US":
                        self.voices.append(voice.name)
            return True
        except:
            print("Error getting Google voices")
            return False

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

        try:
            res = self.client.synthesize_speech(
                request={
                    "input": input_text,
                    "voice": voice_config,
                    "audio_config": audio_config,
                }
            )
            print("Successfully generated Google audio file")
            try:
                filename, filesize = self.__save_audio(
                    output_folder, res, voice, clip_id
                )
                return 200, filename, filesize
            except Exception as e:
                print(str(e))
                return 400, None, None

        except Exception:
            print("Error generating Google audio file")
            return 400, None, None

    def __save_audio(self, output_folder, res, voice, clip_id):
        audio_file = "google_" + voice + "_" + str(clip_id) + ".wav"
        audio_path = output_folder + audio_file

        # save audio file
        try:
            with open(audio_path, "wb") as out:
                out.write(res.audio_content)
            dp.resample_file(audio_path, 16000, "PCM_16")
        except:
            raise Exception("Could not save file " + audio_file + "\n")

        print("Saved to file: " + audio_file + "\n")
        return audio_file, os.path.getsize(audio_path)
