from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import openai
import pprint as pp
import re

VIDEO_LINK = 'https://www.youtube.com/watch?v=ZW3dcu8H4gI'

# Take video link and extract video ID
def extract_youtube_video_id(url):
    # Define the regular expression pattern
    pattern = r'(?<=v=)([\w-]+)'

    # Use re.search to find the match in the URL
    match = re.search(pattern, url)

    if match:
        url_video_id = match.group(1)
        return url_video_id
    else:
        return None

# Assign video ID from given link to video_id
# to be passed to transcript function
video_id = extract_youtube_video_id(VIDEO_LINK)

# Must be a single transcript.
transcript = YouTubeTranscriptApi.get_transcript(video_id)

formatter = TextFormatter()

formatted = formatter.format_transcript(transcript)

# Now we can write it out to a file.
with open('test_output_file.txt', 'w', encoding='utf-8') as text_file:
    text_file.write(formatted)

openai.api_key = "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"
messages = [{"role": "system", "content": "You are a video transcription assistant, you will be provided a "
                                          "transcript of a youtube video - you task it to summarize the content and "
                                          "present it back to a user in a clear and concise way. Present a brief "
                                          "overview of the video and a summary of the main points of the video. End "
                                          "with a short conclusion"}]

with open('test_output_file.txt', 'r') as f:
    lines = f.read().replace('\n', '')

if lines:
    messages.append(
        {"role": "user", "content": lines},
    )
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
reply = chat.choices[0].message.content
pp.pprint(f"ChatGPT: {reply}")
messages.append({"role": "assistant", "content": reply})
