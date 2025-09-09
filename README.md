# Audible AAX to Per-Chapter MP3 Converter

Convert Audible `.aax` audiobooks into individual MP3 files for each chapter. Includes both command-line and web interfaces.

## Features

- **Per-chapter conversion**: Each chapter becomes a separate MP3 file
- **Batch processing**: CLI for multiple files
- **Web interface**: Simple upload and download
- **Quality options**: Configurable MP3 encoding quality
- **Chapter naming**: Automatic chapter title extraction
- **ZIP packaging**: Convenient download of all chapters

## Requirements

- **System**: macOS/Linux with Python 3.9+
- **Audio**: `ffmpeg` and `ffprobe` (install via `brew install ffmpeg`)
- **Browser**: Firefox + geckodriver for activation key retrieval
- **Activation bytes**: Your personal Audible decryption key

## Quick Start

### 1. Install Dependencies

```bash
# Install system requirements
brew install ffmpeg firefox geckodriver

# Create Python environment
python3 -m venv ~/pyenv/aax2mp3
source ~/pyenv/aax2mp3/bin/activate

# Clone this repo and install Python packages
git clone https://github.com/artvandelay/audible-aax-to-mp3.git
cd audible-aax-to-mp3
pip install -r requirements.txt
```

### 2. Get Your Activation Bytes

Your activation bytes are a personal decryption key tied to your Audible account.

```bash
# Clone the activation tool
git clone https://github.com/inAudible-NG/audible-activator.git

# Set the path and run the helper
export AUDIBLE_ACTIVATOR_DIR=$(pwd)/audible-activator
AUDIBLE_REGION=us bash scripts/get_activation_bytes.sh
```

**Supported regions**: `us`, `uk`, `au`, `in`, `de`, `fr`, `jp`

The script will:
1. Open Firefox for Audible login
2. Handle authentication (including 2FA if enabled)  
3. Print your activation bytes (8 hex characters, e.g., `40d0ec08`)

### 3. Configure Environment

```bash
# Copy and edit configuration
cp env.example .env

# Edit .env file:
# ACTIVATION_BYTES=40d0ec08  # Your activation bytes from step 2
# FLASK_SECRET_KEY=your-random-secret
# MP3_QUALITY=2  # 0=best quality, 9=smallest size
```

### 4. Convert Your Audiobooks

**Command Line:**
```bash
# Activate environment
source ~/pyenv/aax2mp3/bin/activate

# Convert a single audiobook
python3 cli/aax_chapter_convert.py /path/to/your/book.aax

# Output will be in: output/book_chapters_mp3/
# ZIP file at: output/book_chapters_mp3.zip
```

**Web Interface:**
```bash
# Start the web server
bash scripts/run_web_tmux.sh

# Open http://localhost:5000 in your browser
# Upload .aax file, choose quality, download ZIP
```

## Project Structure

```
audible-aax-to-mp3/
├── cli/                    # Command-line interface
│   └── aax_chapter_convert.py
├── lib/                    # Core conversion logic
│   └── converter.py
├── web/                    # Web interface
│   ├── app.py
│   └── templates/
├── scripts/                # Helper scripts
│   ├── get_activation_bytes.sh
│   └── run_web_tmux.sh
├── requirements.txt        # Python dependencies
├── env.example            # Environment template
└── README.md
```

## Troubleshooting

**"activation_bytes value needs to be 4 bytes" error:**
- Ensure your activation bytes are exactly 8 hex characters
- Re-run the activation script to get fresh bytes

**"ffmpeg not found" error:**
- Install: `brew install ffmpeg`

**Firefox/geckodriver issues:**
- Install: `brew install firefox geckodriver`
- Check versions are compatible

**Permission denied on scripts:**
- Make executable: `chmod +x scripts/*.sh`

## Advanced Usage

**Custom output directory:**
```bash
python3 cli/aax_chapter_convert.py book.aax --out /custom/path
```

**Different quality settings:**
```bash
python3 cli/aax_chapter_convert.py book.aax --quality 0  # Best quality
python3 cli/aax_chapter_convert.py book.aax --quality 9  # Smallest size
```

**Batch processing multiple files:**
```bash
for file in *.aax; do
    python3 cli/aax_chapter_convert.py "$file"
done
```

## Legal Notice

This tool is for personal use with your own legally purchased Audible audiobooks. It does not circumvent DRM but uses your own activation key to decrypt content you already own. Please respect copyright and do not distribute converted files.

## References

- [FFmpeg Audible AAX Documentation](https://ffmpeg.org/ffmpeg-all.html#Audible-AAX)
- [audible-activator Project](https://github.com/inAudible-NG/audible-activator)
- [Audible Terms of Use](https://www.audible.com/conditions-of-use)
