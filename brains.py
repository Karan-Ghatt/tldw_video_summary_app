import os

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

import openai

import re
import datetime

import pprint as pp

OPEN_AI_KEY = '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'

AGENT_PROFILE = '''
Imagine yourself as a skilled video transcription assistant with the 
responsibility of crafting a thorough and engaging summary for a YouTube 
video. Your task involves delivering a coherent and structured summary 
that encompasses the core theme, primary focus, essential takeaways, 
noteworthy specifics, and pivotal debates or viewpoints presented within 
the video. Organize your summary into three well-defined segments: a succinct 
introductory glimpse, an intricate breakdown of the content, and a succinct 
yet all-encompassing wrap-up. Make sure to employ clear headings for each 
segment to ensure a seamless flow.
'''

# Take video link then extracts and returns video ID
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

# Takes the video idea from the extract function and returns the formatted transcript of the video
# The transcript is then written to a text file for storage and to be read by the gpt function.
# The function stores the returned transcript.txt file in a directory called transcript_archive
# If the directory does not exist, then the function creates it
# This function will return the file directory path, with the file extension, of the returned transcript
def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatter = TextFormatter()
    formatted_transcript = formatter.format_transcript(transcript)
    ts = datetime.datetime.now()
    ts_string = ts.strftime('%Y-%m-%d %H:%M:%S.%f')
    file_name = f'formatted_returned_transcript_{ts_string}_{str(video_id)}'

    # Define the directory path
    directory = 'transcript_archive'

    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write formatted transcript to a text file in the specified directory
    with open(f'{directory}/{file_name}.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(formatted_transcript)

    return f'{directory}/{file_name}.txt'


# This function utilizes the OpenAI GPT-3.5 Turbo model to engage in a chat-based interaction.
# It reads text from an output file, incorporates it into a conversation with predefined system profile,
# and generates a response using the AI model. The response is then appended to the conversation.
def gpt_function(output_file_name):
    openai.api_key = OPEN_AI_KEY

    messages = [{"role": "system", "content": AGENT_PROFILE}]

    with open(output_file_name, 'r') as f:
        lines = f.read().replace('\n', '')

    if lines:
        messages.append(
            {"role": "user", "content": lines},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    # pp.pprint(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})
    return reply



