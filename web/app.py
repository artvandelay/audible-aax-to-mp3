import os
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from dotenv import load_dotenv

from lib.converter import convert_aax_to_mp3_by_chapter, create_zip_from_directory

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024 * 1024  # 4 GB


def is_valid_activation_bytes(value: str) -> bool:
    return isinstance(value, str) and len(value) == 8 and all(c in "0123456789abcdefABCDEF" for c in value)


@app.route("/", methods=["GET"]) 
def index():
    default_key = os.environ.get("ACTIVATION_BYTES", "")
    default_quality = os.environ.get("MP3_QUALITY", "2")
    return render_template("index.html", default_key=default_key, default_quality=default_quality)


@app.route("/convert", methods=["POST"]) 
def convert():
    file = request.files.get("aax")
    activation_bytes = (request.form.get("activation_bytes") or os.environ.get("ACTIVATION_BYTES", "")).strip()
    quality = (request.form.get("quality") or os.environ.get("MP3_QUALITY", "2")).strip()

    if not file or file.filename == "":
        flash("Please choose an .aax file.")
        return redirect(url_for("index"))

    if not is_valid_activation_bytes(activation_bytes):
        flash("Activation bytes must be 16 hex characters.")
        return redirect(url_for("index"))

    if not file.filename.lower().endswith(".aax"):
        flash("File must have .aax extension.")
        return redirect(url_for("index"))

    with tempfile.TemporaryDirectory() as tmpdir:
        aax_path = os.path.join(tmpdir, file.filename)
        file.save(aax_path)

        base_name = Path(file.filename).stem
        out_dir = os.path.join(tmpdir, f"{base_name}_chapters_mp3")
        os.makedirs(out_dir, exist_ok=True)

        try:
            convert_aax_to_mp3_by_chapter(
                aax_path=aax_path,
                activation_bytes=activation_bytes,
                output_directory=out_dir,
                audio_quality=quality,
            )
        except Exception as exc:
            flash(f"Conversion failed: {exc}")
            return redirect(url_for("index"))

        zip_path = os.path.join(tmpdir, f"{base_name}_chapters_mp3.zip")
        create_zip_from_directory(out_dir, zip_path)
        return send_file(zip_path, as_attachment=True, download_name=os.path.basename(zip_path))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
