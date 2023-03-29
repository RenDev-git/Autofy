import io
import os
import moviepy.editor as mp
from pytube import YouTube
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TALB,APIC
from PIL import Image, ImageOps
import requests
# Replace 'https://www.youtube.com/watch?v=sujCA6c1oqc' with the URL of the YouTube video you want to download
yt = YouTube(input("Insert a Youtube Url :"))

# Get the first stream that only contains audio
audio_stream = yt.streams.filter(only_audio=True).first()

# Download the audio stream to the current working directory
audio_stream.download()

# Get the filename of the downloaded file
filename = audio_stream.default_filename

# Remove the file extension from the filename
name, extension = os.path.splitext(filename)

# Use MoviePy to convert the downloaded MP4 file to an MP3 file
clip = mp.AudioFileClip(filename)
clip.write_audiofile(name + ".mp3")

# Remove the downloaded MP4 file
os.remove(filename)

# Load the MP3 file
audiofile = MP3(name + ".mp3", ID3=ID3)

# Set the artist and album metadata tags
audiofile.tags.add(TPE1(encoding=3, text=yt.author))
audiofile.tags.add(TALB(encoding=3, text=yt.publish_date.strftime('%Y-%m-%d')))

# Save the changes to the file
audiofile.save()
# Get the thumbnail URL of the YouTube video
thumbnail_url = yt.thumbnail_url

# Download the thumbnail image to the current working directory
thumbnail_filename = f"{name}.jpg"
with open(thumbnail_filename, "wb") as thumbnail_file:
    thumbnail_file.write(requests.get(thumbnail_url).content)

# Open the thumbnail image with Pillow
with Image.open(thumbnail_filename) as img:
    # Crop the image to 1:1 scale in the center
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
    
    # Resize the image to 500x500 pixels
    img = img.resize((500, 500))

    # Save the cropped and resized image to a BytesIO object
    image_bytes = io.BytesIO()
    img.save(image_bytes, format="JPEG")
    image_bytes.seek(0)

    # Add the image as an album cover to the MP3 file
    album_cover = APIC(mime="image/jpeg", type=3, desc=u"Cover", data=image_bytes.read())
    audiofile.tags.add(album_cover)
    audiofile.save()

# Remove the thumbnail image file
os.remove(thumbnail_filename)

print("Conversion and metadata tagging complete!")
