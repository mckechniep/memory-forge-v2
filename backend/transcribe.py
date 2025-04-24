import sys
import os
import tempfile
import whisper
from process import process

# This script transcribes an MP3 audio file to text and processes it according to specified parameters.
# It requires 5 command-line arguments to run properly.

# Check if the correct number of command-line arguments is provided
if len(sys.argv) < 6:
    print("Usage: python transcribe.py <mp3_path> <title> <instruction> <mode> <output_path>")
    sys.exit(1)

# Extract command-line arguments
# mp3_path: Path to the MP3 file to transcribe
mp3_path = sys.argv[1]
# title: Title for the transcribed content
title = sys.argv[2]
# instruction: Instructions for processing the transcription
instruction = sys.argv[3]
# mode: Processing mode (RAG or SFT)
mode = sys.argv[4]
# output_path: Where to save the final processed output
output_path = sys.argv[5]

# Initialize the Whisper speech recognition model
# The "small" model balances accuracy and resource usage
print("Transcribing with Whisper...")
model = whisper.load_model("small")

# Perform the actual transcription of the audio file
# This converts the speech in the MP3 to text
result = model.transcribe(mp3_path)

# Save the transcribed text to a temporary file
# This creates a text file that will be used for further processing
with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as tmp:
    tmp.write(result["text"])
    txt_path = tmp.name

# Process the transcription according to the specified mode
# This converts the raw transcription into a structured JSONL format
# The format depends on whether it's for RAG (Retrieval Augmented Generation)
# or SFT (Supervised Fine-Tuning)
final_output = process(txt_path, title, instruction, mode, output_path)

# Indicate completion and show the result
print("Done!")
print(final_output)