import os
from dotenv import load_dotenv
import tempfile
import time
import edge_tts
import asyncio
from moviepy import (
    TextClip,
    AudioFileClip,
    CompositeVideoClip,
    VideoFileClip,
    concatenate_videoclips,
    ImageClip
)
from PIL import Image, ImageDraw
import re
import whisper
import numpy as np
import requests

def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from a filename for Windows."""
    filename = re.sub(r'[\\/*?:"<>|]', "", filename)  # Remove invalid chars
    filename = filename.strip()  # Remove leading/trailing spaces
    return filename

def clean_text_for_narration(text: str) -> str:
    """Removes URLs and other artifacts from text before narration."""
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text, flags=re.MULTILINE)
    # You can add other cleaning steps here, like removing markdown
    return text.strip()

load_dotenv()

# Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Edge-TTS voice settings (FREE!)
VOICE_MALE = "en-US-GuyNeural"      # Male voice
VOICE_FEMALE = "en-US-JennyNeural"  # Female voice

# Minecraft clip location and output resolution
MINECRAFT_CLIP = os.getenv("MINECRAFT_CLIP_PATH", "minecraft_loop.mp4")
OUTPUT_SIZE = (1080, 1920)  # Portrait mode

# Font size settings (customize these!)
TITLE_FONT_SIZE = 55  # Font size for title on card
TIKTOK_HANDLE_FONT_SIZE = 32  # Font size for TikTok handle
SUBTITLE_FONT_SIZE = 80  # Font size for subtitles
SUBTITLE_STROKE_WIDTH = 4  # Outline thickness for subtitles

# Subtitle position settings
# Vertical position options:
#   - Number (pixels from top): e.g., 1500, 1600, 1700
#   - OUTPUT_SIZE[1] - 400 = 400px from bottom (default)
#   - OUTPUT_SIZE[1] - 300 = 300px from bottom (higher)
#   - OUTPUT_SIZE[1] - 500 = 500px from bottom (lower)
#   - OUTPUT_SIZE[1] // 2 = center of screen
SUBTITLE_VERTICAL_POSITION = OUTPUT_SIZE[1] - 400  # 400px from bottom (default)

# Horizontal position: "center", "left", "right", or ("center", SUBTITLE_VERTICAL_POSITION)
SUBTITLE_HORIZONTAL_POSITION = "center"  # Keep centered horizontally

# Whisper model (loaded once)
WHISPER_MODEL = None

def load_whisper_model():
    """Load Whisper model (only once)."""
    global WHISPER_MODEL
    if WHISPER_MODEL is None:
        print("Loading Whisper model (this may take a moment)...")
        WHISPER_MODEL = whisper.load_model("base")  # Options: tiny, base, small, medium, large
        print("✓ Whisper model loaded")
    return WHISPER_MODEL

def group_words_into_chunks(word_timestamps, words_per_chunk=3):
    """Group word timestamps into chunks for subtitle display."""
    chunks = []
    
    for i in range(0, len(word_timestamps), words_per_chunk):
        chunk_words = word_timestamps[i:i + words_per_chunk]
        
        if chunk_words:
            chunk = {
                'text': ' '.join([w['word'] for w in chunk_words]),
                'start': chunk_words[0]['start'],
                'end': chunk_words[-1]['end']
            }
            chunks.append(chunk)
    
    return chunks


def detect_narrator_gender(text):
    """Use Gemini AI to detect if the narrator is male or female."""
    try:
        # Use the same stable model as scripter.py for consistency
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}"
        
        headers = {"Content-Type": "application/json"}
        
        prompt = f"""Analyze this Reddit story and determine the gender of the narrator/storyteller.

Story:
{text}

Respond with ONLY one word: either "male" or "female"
Base your answer on:
- First-person pronouns and context
- References to relationships (my wife/husband, boyfriend/girlfriend)
- Any explicit mentions of gender
- Overall context clues

Response (one word only):"""

        body = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            data = response.json()
            gender = data["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
            
            print(f"✓ Gemini detected narrator gender: {gender}")
            
            if "female" in gender:
                print("  → Using female voice")
                return VOICE_FEMALE
            else:
                print("  → Using male voice")
                return VOICE_MALE
        else:
            print(f"⚠ Gemini API error: {response.status_code}")
            print("  → Using default male voice")
            return VOICE_MALE
            
    except Exception as e:
        print(f"⚠ Gender detection failed: {e}")
        print("  → Using default male voice")
        return VOICE_MALE


def expand_abbreviations_for_tts(text):
    """Expands common Reddit abbreviations in text for better TTS narration."""
    abbreviations = {
        "TIFU": "Today I Fucked Up",
        "AITA": "Am I the Asshole",
        "TL;DR": "TLDR",
        "OP": "Original Poster",
        "IMO": "In My Opinion",
        "IMHO": "In My Humble Opinion",
        "ELI5": "Explain Like I'm Five",
        "NSFW": "Not Safe For Work",
        "SFW": "Safe For Work",
    }
    # This regex ensures we only replace whole words
    for abbr, full_text in abbreviations.items():
        # Use a word boundary regex to avoid replacing parts of words
        text = re.sub(r'\b' + re.escape(abbr) + r'\b', full_text, text, flags=re.IGNORECASE)
    return text


async def generate_tts_async(text, filename, voice_id):
    """Generate speech using Edge-TTS (async)"""
    # The `edge-tts` library does not support custom SSML tags like `<break>`.
    # However, it does support rate, volume, and pitch adjustments via its constructor.
    # We'll increase the rate by 15% for a more engaging pace.
    # The text passed to this function is already prepared.
    communicate = edge_tts.Communicate(text, voice=voice_id, rate="+15%")
    await communicate.save(filename)


def text_to_speech(text, filename="voiceover.mp3"):
    """Generate speech and return the audio file path."""
    try:
        # Detect narrator gender and select appropriate voice
        voice_id = detect_narrator_gender(text)

        # Create a version of the script with abbreviations expanded for narration
        speech_text = expand_abbreviations_for_tts(text)
        # Replace periods with commas for a shorter, more natural pause.
        speech_text_with_commas = speech_text.replace('.', ',')

        # Generate with Edge-TTS at a faster rate
        print(f"Generating voiceover with {voice_id} (with optimized pauses)...")
        asyncio.run(generate_tts_async(speech_text_with_commas, filename, voice_id))

        print(f"Voiceover saved as {filename}")
        return filename
    except Exception as e:
        print("Error generating voiceover:", e)
        return None


def get_actual_title_duration(transcription_result, title_text):
    """Use Whisper to find the actual duration of the title narration."""
    # Get all words from title (normalize for comparison)
    title_words = [w.lower().strip() for w in title_text.split()]
    
    # Find where the title ends in the transcription
    all_words = []
    for segment in transcription_result.get('segments', []):
        if 'words' in segment:
            for word_info in segment['words']:
                all_words.append({
                    'word': word_info['word'].strip().lower(),
                    'end': word_info['end']
                })
    
    if not all_words:
        # Fallback to estimation if Whisper fails
        return (len(title_words) / 3.0) + 0.5
    
    # Find the last word of the title in the transcription
    title_end_time = 0
    words_matched = 0
    
    for i, word in enumerate(all_words):
        if words_matched < len(title_words):
            # Check if this word matches the current title word
            if title_words[words_matched] in word['word'] or word['word'] in title_words[words_matched]:
                words_matched += 1
                title_end_time = word['end']
        else:
            break
    
    # Add small buffer (0.3 seconds) after last title word
    title_end_time += 0.3
    
    # If we didn't match enough words, fall back to estimation
    if words_matched < len(title_words) * 0.5:  # At least 50% match
        print(f"  Warning: Only matched {words_matched}/{len(title_words)} title words, using estimation")
        return (len(title_words) / 3.0) + 0.5
    
    return title_end_time


def loop_video_to_duration(video_clip, target_duration):
    """Loop a video clip to match the target duration."""
    video_duration = video_clip.duration
    
    if video_duration >= target_duration:
        # If video is longer than needed, just trim it
        return video_clip.subclipped(0, target_duration)
    
    # Calculate how many times we need to loop
    num_loops = int(target_duration / video_duration) + 1
    
    # Create copies of the clip for looping
    clips_to_loop = []
    for _ in range(num_loops):
        clips_to_loop.append(video_clip.copy())
    
    looped = concatenate_videoclips(clips_to_loop, method="compose")
    
    # Trim to exact duration
    final_clip = looped.subclipped(0, target_duration)
    
    # Clean up intermediate clips
    looped.close()
    
    return final_clip


def create_title_card(title_text, tiktok_name, font_path, duration):
    """Create a stylized title card with rounded corners and shadow."""
    # Card dimensions
    card_width = 900
    card_height = 400
    corner_radius = 30
    
    # Create card with shadow using PIL
    shadow_offset = 15
    img_width = card_width + shadow_offset * 2
    img_height = card_height + shadow_offset * 2
    
    # Create image with transparency
    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw shadow (offset, darker, semi-transparent)
    shadow_color = (0, 0, 0, 120)
    draw.rounded_rectangle(
        [shadow_offset + 8, shadow_offset + 8, card_width + shadow_offset + 8, card_height + shadow_offset + 8],
        radius=corner_radius,
        fill=shadow_color
    )
    
    # Draw main card (white with slight transparency)
    card_color = (255, 255, 255, 240)
    draw.rounded_rectangle(
        [shadow_offset, shadow_offset, card_width + shadow_offset, card_height + shadow_offset],
        radius=corner_radius,
        fill=card_color
    )
    
    # --- Add PFP Placeholder ---
    # Draw a solid black circle in the top-left corner of the card
    pfp_radius = 25
    pfp_position = (shadow_offset + 30 + pfp_radius, shadow_offset + 30 + pfp_radius)
    draw.ellipse(
        [pfp_position[0] - pfp_radius, pfp_position[1] - pfp_radius, 
         pfp_position[0] + pfp_radius, pfp_position[1] + pfp_radius],
        fill="black"
    )

    # Use a temporary file for the card image to avoid race conditions
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_card:
        card_path = temp_card.name

    img.save(card_path)
    
    # Create ImageClip from the card
    card_clip = ImageClip(card_path).with_duration(duration).with_position("center")
    
    # --- Use a better font for the title and handle ---
    title_font = font_path.get('luckiest_guy') or font_path.get('default')
    handle_font = font_path.get('default') # Keep handle font simple

    # Create TikTok handle text (top-left of card)
    try:
        tiktok_text = TextClip(
            text=tiktok_name, 
            font_size=TIKTOK_HANDLE_FONT_SIZE, 
            color="black", 
            font=handle_font,
        ).with_duration(duration).with_position(
            (pfp_position[0] + pfp_radius + 15, pfp_position[1] - (TIKTOK_HANDLE_FONT_SIZE / 2))
        )
    except Exception as e:
        print(f"Error creating TikTok handle text clip: {e}")
        tiktok_text = None
    
    # Create title text (center of card)
    try:
        title_clip = TextClip(
            text=title_text,
            font_size=TITLE_FONT_SIZE,
            color="black",
            font=title_font,
            size=(card_width - 80, card_height - 40),
            method="caption"
        ).with_duration(duration).with_position("center")
    except Exception as e:
        print(f"Error creating title text clip: {e}")
        title_clip = None
    
    # Combine card and text
    clips = [card_clip]
    if tiktok_text:
        clips.append(tiktok_text)
    if title_clip:
        clips.append(title_clip)
    
    final_card = CompositeVideoClip(clips, size=OUTPUT_SIZE)

    # Clean up the temporary image file after creating the clip
    if os.path.exists(card_path):
        os.remove(card_path)

    return final_card


def create_subtitle_clips_with_whisper(transcription_result, font_path, title_duration):
    """Create synchronized subtitle clips using Whisper word timestamps."""
    # The transcription is already done. We just need to extract the words.
    word_timestamps = []
    for segment in transcription_result.get('segments', []):
        if 'words' in segment and segment['words']:
            for word_info in segment['words']:
                word_timestamps.append({
                    'word': word_info.get('word', '').strip(),
                    'start': word_info.get('start', 0),
                    'end': word_info.get('end', 0)
                })

    print(f"\n=== SUBTITLE DEBUG ===")
    print(f"Total words transcribed: {len(word_timestamps)}")
    print(f"Title duration: {title_duration:.2f}s")
    
    if not word_timestamps:
        print("ERROR: No word timestamps found!")
        return []
    
    # Show first few words for debugging
    print(f"First 5 words: {word_timestamps[:5]}")
    
    # Filter out words that appear during the title card
    words_after_title = [w for w in word_timestamps if w['start'] >= title_duration]
    
    print(f"Words after title: {len(words_after_title)}")
    
    if not words_after_title:
        print("WARNING: No words found after title duration, using all words")
        words_after_title = word_timestamps
    
    # Group words into chunks (3 words per subtitle)
    chunks = group_words_into_chunks(words_after_title, words_per_chunk=3)
    
    print(f"Total chunks created: {len(chunks)}")
    
    subtitle_clips = []
    
    # Use Luckiest Guy font if available
    subtitle_font = font_path.get('luckiest_guy') or font_path.get('default')
    print(f"Using subtitle font: {subtitle_font}")
    
    for i, chunk in enumerate(chunks):
        start_time = chunk['start']
        duration = chunk['end'] - chunk['start']
        
        # Create subtitle clip with Luckiest Guy font
        try:
            subtitle = TextClip(
                text=chunk['text'],
                font_size=SUBTITLE_FONT_SIZE,
                color="white",
                font=subtitle_font,
                stroke_color="black",
                stroke_width=SUBTITLE_STROKE_WIDTH,
                method="caption",
                size=(OUTPUT_SIZE[0] - 100, None)
            ).with_position("center").with_duration(duration).with_start(start_time)
            
            subtitle_clips.append(subtitle)
            print(f"  ✓ Chunk {i+1}: '{chunk['text'][:40]}' at {start_time:.2f}s for {duration:.2f}s")
        except Exception as e:
            print(f"  ✗ ERROR creating subtitle chunk {i}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"Successfully created {len(subtitle_clips)} subtitle clips")
    print(f"=== END DEBUG ===\n")
    
    return subtitle_clips


def get_font_path():
    """Find font files, prioritizing a local 'fonts' directory."""
    result = {'default': None, 'luckiest_guy': None}
    local_font_dir = "fonts"

    # Define expected font filenames
    default_font_file = "Arial.ttf"
    luckiest_guy_font_file = "LuckiestGuy-Regular.ttf" # Adjust if your filename is different

    # Check for local fonts first
    local_default_path = os.path.join(local_font_dir, default_font_file)
    if os.path.exists(local_default_path):
        result['default'] = local_default_path

    local_luckiest_path = os.path.join(local_font_dir, luckiest_guy_font_file)
    if os.path.exists(local_luckiest_path):
        result['luckiest_guy'] = local_luckiest_path

    # Fallback for default font if not found locally
    if not result['default']:
        # On Linux, moviepy can often find a default font like 'Liberation-Sans'
        result['default'] = "Arial" # Let moviepy try to find it

    print(f"Using default font: {result['default']}")
    print(f"Using Luckiest Guy font: {result['luckiest_guy'] or 'NOT FOUND - will use default'}")
    
    return result


def create_video_with_minecraft(audio_file, title_text, transcription_result, minecraft_clip_path, title_duration, output_file="final_video.mp4", tiktok_name="MyTikTok"):
    audio = AudioFileClip(audio_file)

    # Load and loop Minecraft video to match audio length
    minecraft_clip = VideoFileClip(minecraft_clip_path)
    minecraft_clip = loop_video_to_duration(minecraft_clip, audio.duration)
    minecraft_clip = minecraft_clip.resized(new_size=OUTPUT_SIZE)

    # Get font paths
    font_paths = get_font_path()
    
    # Create stylized title card with TikTok handle (only shows during title narration)
    title_card = create_title_card(title_text, tiktok_name, font_paths, title_duration)

    # Create synced subtitle clips using Whisper (NEW: uses actual audio timestamps)
    subtitle_clips = create_subtitle_clips_with_whisper(transcription_result, font_paths, title_duration)

    # Compose final video
    all_clips = [minecraft_clip, title_card]
    all_clips.extend(subtitle_clips)
    
    final_clip = CompositeVideoClip(all_clips, size=OUTPUT_SIZE).with_audio(audio)
    print(f"Rendering video: {output_file}")
    # Optimized write_videofile for speed
    # preset='ultrafast' -> Greatly speeds up encoding at the cost of a larger file size.
    # threads=8 -> Increase if your CPU has more cores.
    # logger=None -> Disables the progress bar for a small speed-up.
    final_clip.write_videofile(output_file, 
                               fps=24, 
                               codec='libx264', 
                               audio_codec='aac', 
                               threads=10, 
                               preset='ultrafast')
    
    # Clean up clips
    audio.close()
    minecraft_clip.close()
    final_clip.close()


def make_video_from_script(title_text, narration_script, video_name="final_video.mp4", tiktok_name="MyTikTok"):
    """Main function to create video from script text."""
    # Use a temporary file for the audio to avoid race conditions
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    audio_file_path = temp_audio_file.name
    temp_audio_file.close() # Close the file so other processes can access it

    try:
        # 1. Generate voiceover
        generated_path = text_to_speech(narration_script, filename=audio_file_path)
        if not generated_path:
            print("Skipping video creation due to audio failure.")
            raise IOError("Failed to generate voiceover audio.")

        # 2. Transcribe the audio ONCE to get all word timestamps
        print("Performing one-time transcription for timestamps...")
        model = load_whisper_model()

        # Use the same text that was used for audio generation (with abbreviations expanded)
        # to ensure Whisper has the correct text to align with the audio.
        prompt_text = expand_abbreviations_for_tts(narration_script)
        narration_title = prompt_text.split('\n\n')[0]

        transcription_result = model.transcribe(audio_file_path, word_timestamps=True, language='en', initial_prompt=prompt_text)

        # 3. Calculate title duration from the transcription result
        title_duration = get_actual_title_duration(transcription_result, narration_title)

        # 4. Create video, passing the transcription result to avoid re-processing
        create_video_with_minecraft(
            audio_file_path,
            title_text=title_text,
            transcription_result=transcription_result,
            minecraft_clip_path=MINECRAFT_CLIP,
            title_duration=title_duration,
            output_file=video_name,
            tiktok_name=tiktok_name
        )
        
        print(f"✓ Video created successfully: {video_name}")
        print(f"  - Title card duration: {title_duration:.2f}s")

    finally:
        # Ensure temporary audio file is always cleaned up
        if os.path.exists(audio_file_path):
            try:
                os.remove(audio_file_path)
                print(f"Cleaned up temporary audio file: {audio_file_path}")
            except OSError as e:
                print(f"Error removing temporary audio file {audio_file_path}: {e}")