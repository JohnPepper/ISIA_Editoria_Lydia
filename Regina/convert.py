from pydub import AudioSegment

# AudioSegment.converter = "/john_pepper/audio-orchestrator-ffmpeg/bin"
# AudioSegment.ffmpeg = "/john_pepper/audio-orchestrator-ffmpeg/bin"
# AudioSegment.ffprobe ="/john_pepper/audio-orchestrator-ffmpeg/bin"

def convert_to_mp3(file_path):
    sound = AudioSegment.from_file(file_path, format="ogg")
    sound.export(f"{file_path}.mp3", format="mp3", bitrate="128k")
