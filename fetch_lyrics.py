# from youtube_dl import YoutubeDL
from audio_processing import apply_effects
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from moviepy.editor import *
from syrics.api import Spotify
from moviepy.video.tools.subtitles import SubtitlesClip

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}


def getSongAudio(song_name):
    results = YoutubeSearch(song_name, max_results=2).to_dict()
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={results[1]["id"]}'])
    return results[1]["id"]


def getSongLyrics(song_name):
    sp = Spotify("AQD9rWYh5NyCQ_FKNh6vhGGE_68ah-WMn6SB18UJP53dhhn1O5jGIzCxfvfLS2_eS-lhQW5V4BOpMYbOaWIjKffKabvifAZMtC_Qub_rERBwXklTiZHX0qkAs2errrSaEe6_vzqblzowgtsMqkMctni7caUhhh-B")
    res = sp.search(song_name, "track", 1)
    lyrics = sp.get_lyrics(res['tracks']['items'][0]['id'])
    song = {}
    song['name'] = res['tracks']['items'][0]['name']
    song['artist'] = res['tracks']['items'][0]['artists'][0]['name']
    song['lyrics'] = lyrics['lyrics']
    song['duration_ms'] = res['tracks']['items'][0]['duration_ms']
    return song


def generateLyrics(lyrics, duration):
    subs = []
    tp = (0, int(lyrics[0]['startTimeMs'])/1000)
    temp = (tp, ".")
    subs.append(temp)
    for i in range(len(lyrics)-1):
        curr_line = lyrics[i]
        next_line = lyrics[i+1]
        subs.append(
            ((int(curr_line['startTimeMs'])/1000, int(next_line['startTimeMs'])/1000), curr_line['words']))
    subs.append(
        ((int(lyrics[-1]['startTimeMs'])/1000, int(duration)/1000), lyrics[-1]['words']))
    for i in range(len(subs)):
        if len(subs[i][1]) == 0:
            subs[i] = (subs[i][0], "...")
        if (len(subs[i][1].split(" ")) > 7):
            words = subs[i][1].split(" ")
            subs[i] = (subs[i][0], " ".join(words[:7]) +
                       "\n" + " ".join(words[7:]))
    return subs


def generator(txt):
    sub = TextClip(txt, fontsize=80, font="fonts/Modak-Regular.ttf", color='white')
    return sub


def generateSong(song_name):
    print("Fetching audio...")
    id = getSongAudio(song_name + " lyrics")
    print("Fetching lyrics...")
    song = getSongLyrics(song_name)
    song["subs"] = generateLyrics(song["lyrics"]['lines'], song["duration_ms"])
    song['location'] = id + ".wav"
    print("Applying 8D effect...")
    song['location'] = apply_effects(song['location'])
    subtitles = SubtitlesClip(song["subs"], generator)
    imgclip = ImageClip("bg.jpg").set_duration(
        int(song['duration_ms']) / 1000)

    audioclip = AudioFileClip(song['location'], fps=48000)
    videoclip = CompositeVideoClip(
        [imgclip, subtitles.set_position(("center", "center"))])
    videoclip = videoclip.set_audio(audioclip)
    return videoclip


def init():
    print("Initializing...")
    song_name = input("Enter song name: ")
    videoclip = generateSong(song_name)
    print("Generating video...")
    print("Select output choice: ")
    print("1. Preview")
    print("2. Save")
    choice = int(input("Enter choice: "))
    if choice == 1:
        videoclip.preview()
    elif choice == 2:
        print("Enter output file name: ")
        file_name = input("Enter file name: ")
        videoclip.write_videofile(file_name, fps=24, codec='libx264',
                                  audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, audio_bitrate='192k')
    
    print("Done!")

if __name__ == "__main__":
    init()
