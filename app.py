import io
import os
import requests
from PIL import Image
from pytube import YouTube
import moviepy.editor as mp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TALB, APIC


# Get user input for the YouTube URL
url = input("Please enter a YouTube URL: ")
yt = YouTube(url)

# Downloading the video (Audio Only)
audio_stream = yt.streams.filter(only_audio=True).first()
audio_stream.download()
filename = audio_stream.default_filename

# File Conversion
name, extension = os.path.splitext(filename)
clip = mp.AudioFileClip(filename)
clip.write_audiofile(name + ".mp3")
os.remove(filename)




# Metatagging
audiofile = MP3(name + ".mp3", ID3=ID3)
audiofile.tags.add(TPE1(encoding=3, text=yt.author))
audiofile.tags.add(TALB(encoding=3, text=yt.publish_date.strftime('%Y-%m-%d')))
audiofile.save()

# Thumbnail 
thumbnail_url = yt.thumbnail_url
thumbnail_filename = f"{name}.jpg"
with open(thumbnail_filename, "wb") as thumbnail_file:
    thumbnail_file.write(requests.get(thumbnail_url).content)

with Image.open(thumbnail_filename) as img:
    width, height = img.size
    if width > height:
        left = (width - height) // 2
        upper = 0
        right = left + height
        lower = height
    else:
        left = 0
        upper = (height - width) // 2
        right = width
        lower = upper + width
    img = img.crop((left, upper, right, lower))
    img = img.resize((500, 500))

    
    image_bytes = io.BytesIO()
    img.save(image_bytes, format="JPEG")
    image_bytes.seek(0)

    # Adding the Album cover to the mp3
    album_cover = APIC(mime="image/jpeg", type=3, desc=u"Cover", data=image_bytes.read())
    audiofile.tags.add(album_cover)
    audiofile.save()

os.remove(thumbnail_filename)


print("The video has been downloaded and converted!")
