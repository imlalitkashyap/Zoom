from flask import Flask, request, redirect, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "Alive",
        "usage": "Send GET request to /download?url=YOUR_ZOOM_LINK"
    })

@app.route('/download', methods=['GET'])
def download_video():
    zoom_url = request.args.get('url')
    
    if not zoom_url:
        return jsonify({"error": "URL parameter is missing"}), 400

    # yt-dlp options specifically tuned for Serverless (Fast & Minimal)
    ydl_opts = {
        'format': 'best',  # Best quality
        'quiet': True,     # Logs mat bharo
        'no_warnings': True,
        'noplaylist': True,
        'cachedir': '/tmp/', # Vercel me sirf /tmp folder writeable hota hai
        # Zoom ko human browser dikhane ke liye headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://zoom.us/'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Metadata extract karo par download mat karo (fastest method)
            info_dict = ydl.extract_info(zoom_url, download=False)
            
            # Direct video URL nikalo
            video_url = info_dict.get('url', None)
            
            if video_url:
                # 302 Redirect: User browser direct Zoom server se download karega
                return redirect(video_url, code=302)
            else:
                return jsonify({"error": "Could not extract video URL"}), 500

    except Exception as e:
        # Agar Zoom ne block kiya ya link invalid hai
        return jsonify({"error": str(e)}), 500

# Local testing ke liye (Vercel isko ignore karega)
if __name__ == '__main__':
    app.run(debug=True)
