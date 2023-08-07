from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import openai
import pprint as pp

video_id = 'Yz0uImGWaTk'

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
