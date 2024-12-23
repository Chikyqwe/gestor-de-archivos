import os
import time
from flask import Flask, render_template_string, request, send_file, Response
import yt_dlp
from pydub import AudioSegment
import threading
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

app = Flask(__name__)

def remove_list_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'list' in query_params:
        query_params.pop('list')
        parsed_url = parsed_url._replace(query=urlencode(query_params, doseq=True))
        return urlunparse(parsed_url)
    return url

def download_video(url):
    url = remove_list_from_url(url)
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.%(ext)s',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return 'video.mp4'
    except Exception as e:
        return f"Error al descargar el video: {str(e)}"

def mp4_to_mp3(input_file, output_file):
    try:
        audio = AudioSegment.from_file(input_file, format="mp4")
        audio.export(output_file, format="mp3")
        os.remove(input_file)
        return output_file
    except Exception as e:
        return str(e)

def delete_file_after_delay(file_path, delay=30):
    time.sleep(delay)
    if os.path.exists(file_path):
        os.remove(file_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        if video_url:
            video_path = download_video(video_url)
            if "Error" in video_path:
                return render_template_string("""
                    <html>
                    <body>
                        <h1>Error al descargar el video</h1>
                        <p>{{ video_path }}</p>
                        <a href="/">Volver</a>
                    </body>
                    </html>
                """, video_path=video_path)

            input_path = "video.mp4"
            output_path = os.path.splitext(input_path)[0] + ".mp3"
            output_mp3 = mp4_to_mp3(input_path, output_path)
            if output_mp3.endswith('.mp3'):
                threading.Thread(target=delete_file_after_delay, args=(output_mp3, 30), daemon=True).start()
                return send_file(output_mp3, as_attachment=True)
            else:
                return render_template_string("""
                    <html>
                    <body>
                        <h1>Error al convertir el archivo</h1>
                        <p>{{ output_mp3 }}</p>
                        <a href="/">Volver</a>
                    </body>
                    </html>
                """, output_mp3=output_mp3)
        else:
            return render_template_string("""
                <html>
                <body>
                    <h1>Error</h1>
                    <p>Por favor, ingrese una URL válida.</p>
                    <a href="/">Volver</a>
                </body>
                </html>
            """)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Descargador de Videos YouTube</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                padding: 20px;
                text-align: center;
            }
            .container {
                width: 100%;
                max-width: 500px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            input[type="text"] {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
        <script>
            function clearInputAfterDelay() {
                const input = document.getElementById('video_url');
                setTimeout(() => {
                    input.value = '';
                }, 2000);
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1>Descargador de Videos YouTube</h1>
            <form action="/" method="POST" onsubmit="clearInputAfterDelay()">
                <input type="text" id="video_url" name="video_url" placeholder="Inserte la URL del video" required>
                <button type="submit">Convertir a MP3</button>
            </form>
        </div>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(debug=True)
