import os

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

import openai

import re
import datetime

from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs

import asyncio
from concurrent.futures import ThreadPoolExecutor

import aiohttp

executor = ThreadPoolExecutor()

# PENDING:
# Secrets management for openAI api Key


OPEN_AI_KEY = 'secret_key'

# Agent profile to be passed as starter prompt
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


# Function takes a URL for a YouTube video and parses the returned HTML request for the video title
async def get_video_title(video_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(video_url) as response:
            html = await response.text()
            soup = bs(html, "html.parser")
            title = soup.find("meta", itemprop="name")["content"]
            return title


# Takes the video idea from the extract function and returns the formatted transcript of the video
# The transcript is then written to a text file for storage and to be read by the gpt function.
# The function stores the returned transcript.txt file in a directory called transcript_archive
# If the directory does not exist, then the function creates it
# This function will return the file directory path, with the file extension, of the returned transcript
async def get_transcript(video_id):
    loop = asyncio.get_event_loop()
    formatted_transcript = await loop.run_in_executor(executor, get_transcript_sync, video_id)
    ts = datetime.datetime.now()
    ts_string = ts.strftime('%Y-%m-%d %H:%M:%S.%f')
    file_name = f'formatted_returned_transcript_{ts_string}_{str(video_id)}'
    directory = 'transcript_archive'
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, f'{file_name}.txt')
    with open(file_path, 'w', encoding='utf-8') as text_file:
        text_file.write(formatted_transcript)
    return file_path


def get_transcript_sync(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatter = TextFormatter()
    formatted_transcript = formatter.format_transcript(transcript)
    return formatted_transcript


# Function takes file containing the transcript of the YouTube video and the initial AGENT_PROFILE
# and passes both to be appended to a list of dicts called messages.
# The function closes and deleted the video transcript file.
async def gpt_function(output_file_name):
    openai.api_key = OPEN_AI_KEY
    messages = [{"role": "system", "content": AGENT_PROFILE}]
    with open(output_file_name, 'r') as f:
        lines = f.read().replace('\n', '')
    if lines:
        messages.append({"role": "user", "content": lines})

        loop = asyncio.get_event_loop()
        reply = await loop.run_in_executor(executor, get_gpt_reply, messages)

        messages.append({"role": "assistant", "content": reply})
        f.close()
        os.remove(output_file_name)
        return reply


# Function passes messages list to chatGPT for response, then returns the first of the responses from the returned
# body of the responses.
def get_gpt_reply(messages):
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return chat.choices[0].message.content
