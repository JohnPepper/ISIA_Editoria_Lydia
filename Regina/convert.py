import pydub
from pydub import AudioSegment

pydub.AudioSegment.ffmpeg = "john_pepper/audio-orchestrator-ffmpeg"


def convert_to_mp3(file_path):
    sound = AudioSegment.from_file(file_path, format="ogg")
    sound.export(f"{file_path}.mp3", format="mp3", bitrate="128k")
