from AmazonWrapper import AmazonWrapper
from GoogleWrapper import GoogleWrapper
from ReplicaWrapper import ReplicaWrapper


# replica = ReplicaWrapper()
# res, filename, filesize = replica.generate_audio(
#     "../audio/",
#     "Hi my name is Jacob and I have crippling eczema",
#     "94c8d359-9a7c-4189-9002-6ba989f74486",
#     0,
# )

# google = GoogleWrapper()
# res, filename, filesize = google.generate_audio(
#     "../audio/",
#     "Hi my name is Jacob and I have crippling eczema",
#     "en-US-Wavenet-A",
#     0,
# )

amazon = AmazonWrapper()
res, filename, filesize = amazon.generate_audio(
    "../audio/", "Hi my name is Jacob and I have crippling eczema", "Joanna", 0
)
