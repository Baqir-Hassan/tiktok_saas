# app/tasks/video_tasks.py
from celery import shared_task
import math
from celery.utils.log import get_task_logger
from app.scripter import generate_script_with_gemini
from app.video_maker import make_video_from_script, sanitize_filename, clean_text_for_narration
import os

logger = get_task_logger(__name__)

def save_to_tracking_file(filename, content):
    """Helper to save generated scripts for tracking."""
    tracking_folder = "tracking_files"
    os.makedirs(tracking_folder, exist_ok=True)
    file_path = os.path.join(tracking_folder, filename)
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(content + "\n")
        file.write("------------------------------------------------------------------------------------------\n\n")

def split_script_into_parts(script, num_parts):
    """Splits a script into a specified number of parts at paragraph breaks."""
    if num_parts <= 1:
        return [script]

    paragraphs = script.strip().split('\n\n')
    total_paragraphs = len(paragraphs)
    
    # Calculate the ideal number of paragraphs per part
    paragraphs_per_part = math.ceil(total_paragraphs / num_parts)
    
    parts = []
    start_index = 0
    for i in range(num_parts):
        # Ensure the last part takes all remaining paragraphs
        if i == num_parts - 1:
            end_index = total_paragraphs
        else:
            end_index = min(start_index + paragraphs_per_part, total_paragraphs)
        parts.append('\n\n'.join(paragraphs[start_index:end_index]))
        start_index = end_index
    
    return [part for part in parts if part] # Filter out empty parts

@shared_task(name="create_video_from_post", bind=True)
def create_video_from_post(self, post_data):
    """
    Celery task to generate a full video from a Reddit post dictionary.
    """
    title = post_data.get("title", "Untitled")
    text = post_data.get("text", "")
    
    # Clean the text to remove URLs before sending to Gemini
    cleaned_text = clean_text_for_narration(text)
    text_content = f"{title}\n{cleaned_text}"
    try:
        logger.info(f"TASK STARTED: Generating script for post: {title[:50]}...")
        script = generate_script_with_gemini(text_content)

        if not script:
            logger.error(f"TASK FAILED: Could not generate script for post: {title}")
            return f"Failed to generate script for {title}"

        # --- Video Splitting Logic ---
        word_count = len(script.split())
        WORDS_PER_MINUTE = 150  # Average narration speed
        narration_duration_minutes = word_count / WORDS_PER_MINUTE

        # If the video is less than 2 minutes, don't split it.
        # Otherwise, calculate parts to keep each part's length close to 1 minute.
        if narration_duration_minutes < 2:
            num_parts = 1
        else:
            num_parts = round(narration_duration_minutes)

        logger.info(f"Estimated narration: {narration_duration_minutes:.2f} mins. Splitting into {num_parts} part(s).")

        script_parts = split_script_into_parts(script, num_parts)

        script_content = f"Title:\n{title}\n\n{script}\n"
        save_to_tracking_file("generated_scripts.txt", script_content)
        logger.info("Script generated. Starting video creation...")

        for i, part_script in enumerate(script_parts):
            part_num = i + 1
            logger.info(f"--- Creating video for Part {part_num}/{len(script_parts)} ---")

            output_folder = "output_videos"
            os.makedirs(output_folder, exist_ok=True)
            sanitized_title = sanitize_filename(title[:30])
            
            if len(script_parts) > 1:
                video_filename = os.path.join(output_folder, f"{sanitized_title}_part{part_num}.mp4")
                # On-screen title: "(Part 1) My Story"
                on_screen_title = f"(Part {part_num}) {title}"
                # Narration script: "My Story, Part 1. The rest of the story..."
                narration_script = f"{title}, Part {part_num}.\n\n{part_script}"
            else:
                video_filename = os.path.join(output_folder, f"{sanitized_title}.mp4")
                on_screen_title = title
                narration_script = f"{title}\n\n{part_script}"

            tiktok_name = os.getenv("TIKTOK_HANDLE", "@YourTikTokHandle")

            make_video_from_script(title_text=on_screen_title, narration_script=narration_script, 
                                   video_name=video_filename, tiktok_name=tiktok_name)
            logger.info(f"TASK PART COMPLETE: Video '{video_filename}' created successfully.")

        return f"Created {len(script_parts)} video(s) for post '{title}'"
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating video for '{title}': {e}", exc_info=True)
        # This will mark the task as FAILED in Flower and other monitors.
        raise

@shared_task(name="ping")
def ping():
    return "pong"
