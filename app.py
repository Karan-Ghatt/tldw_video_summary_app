from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from brains import extract_youtube_video_id, get_transcript, gpt_function
import logging

app = Flask(__name__)
bootstrap = Bootstrap(app)

logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    summary = None
    video_url = None

    if request.method == 'POST':
        video_url = request.form['video_url']
        logging.debug(f'Video URL is {video_url}')
        video_id = extract_youtube_video_id(video_url)
        logging.debug(f'Video ID is {video_id}')

        if video_id:
            try:
                transcript_file = get_transcript(video_id)
                logging.debug(f'Transcript file generated/n Location: {transcript_file}')
                summary = gpt_function(transcript_file)
                logging.debug(f'Summary Generated: {summary[:7]}')
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                logging.debug(f'An error has occurred: {str(e)}')
        else:
            error_message = "Invalid YouTube URL. Please enter a valid video URL."

    return render_template('main_page.html', error_message=error_message, summary=summary, video_url=video_url)

if __name__ == '__main__':
    app.run(debug=True)
