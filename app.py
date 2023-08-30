from flask import Flask, render_template, request, send_from_directory
from flask_bootstrap import Bootstrap
from brains import extract_youtube_video_id, get_transcript, gpt_function, get_video_title
import logging



app = Flask(__name__)
bootstrap = Bootstrap(app)

logging.basicConfig(level=logging.DEBUG)



@app.route('/', methods=['GET', 'POST'])
async def index():
    error_message = None
    summary = None
    video_url = None
    video_name = None

    if request.method == 'POST':
        video_url = request.form['video_url']
        logging.debug(f'Video URL is {video_url}')
        video_id = extract_youtube_video_id(video_url)
        logging.debug(f'Video ID is {video_id}')

        if video_id:
            try:
                video_name = await get_video_title(video_url)
                logging.debug(f'Video Name is {video_name}')

                transcript_file = await get_transcript(video_id)
                logging.debug(f'Transcript file generated/n Location: {transcript_file}')

                summary = await gpt_function(transcript_file)
                logging.debug(f'Summary Generated: {summary[:7]}')

            except Exception as e:
                exp = str(e)
                print(exp[:69])
                if exp[:69] == "This model's maximum context length is 4097 tokens. However, your mes":
                    error_message = "An error has occurred: This video is too long, please choose a shorter video."
                else:
                    error_message = f"An error occurred: {str(e)}"
                    logging.debug(f'An error has occurred: {str(e)}')
        else:
            error_message = "Invalid YouTube URL. Please enter a valid video URL."

    return render_template('main_page.html', error_message=error_message, summary=summary, video_name=video_name)


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)



if __name__ == '__main__':
    app.run(debug=True)
