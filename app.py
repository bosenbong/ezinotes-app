import streamlit as st
import openai
import os
from datetime import datetime, timedelta
import tempfile
from fpdf import FPDF

# Set your OpenAI API key
openai.api_key = "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"

st.set_page_config(page_title="EziNotes Mobile", layout="centered")
st.title("📋 EziNotes - Mobile Session Note Tool")

st.markdown("Upload a voice note, add session info, and generate a formatted note.")

# File uploader
audio_file = st.file_uploader("🎤 Upload voice note (.m4a, .mp3, .wav)", type=["m4a", "mp3", "wav"])

# Metadata inputs
participant = st.text_input("👤 Participant First + Last Initial (e.g., John S)")
time_range = st.text_input("⏰ Time Range (e.g., 8:30 AM – 9:30 AM)")
support_tag = st.selectbox(
    "📁 Support Type",
    ["assistance_with_daily_life", "social_participation", "transport", "unspecified"]
)
generate = st.button("🪄 Generate Session Note")

if generate and audio_file and participant:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_audio:
        temp_audio.write(audio_file.read())
        temp_audio_path = temp_audio.name

    with open(temp_audio_path, "rb") as f:
        transcript = openai.Audio.transcribe(model="whisper-1", file=f, response_format="text")

    today = datetime.today()
    date_today = today.strftime("%d %B %Y")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional assistant formatting support session notes to meet NDIS compliance.\n"
                "Your notes should follow this structure:\n"
                "- Start with 'NDIS Support Notes – [Participant Name]'\n"
                "- Include 'Date:' and optionally 'Time:'\n"
                "- Begin with a neutral arrival statement\n"
                "- List completed activities as bullet points\n"
                "- End with a summary paragraph noting participant's reported state or observations\n"
                "- Use phrasing such as 'reported feeling well' or 'was observed smiling'\n"
                "- Avoid assumptions or clinical language\n"
                "- Include 'Departure:' at the end if applicable\n"
                "Return only the formatted note in clear professional tone."
            )
        },
        {
            "role": "user",
            "content": (
                f"Transcript: {transcript}\n"
                f"Support Worker: Jarrad Bosenberg\n"
                f"Date: {date_today}\n"
                f"Time: {time_range}\n"
                f"If no participant name is clearly mentioned, leave it as '[Participant]'."
            )
        }
    ]

    response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
    formatted_note = response['choices'][0]['message']['content']

    st.subheader("📝 Generated Session Note:")
    st.code(formatted_note, language='markdown')
    st.download_button("⬇️ Download as TXT", formatted_note, file_name=f"{participant} - {date_today}.txt")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in formatted_note.split("\n"):
        pdf.multi_cell(0, 10, line)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        tmp_pdf_path = tmp_pdf.name

    with open(tmp_pdf_path, "rb") as f:
        st.download_button("⬇️ Download as PDF", f, file_name=f"{participant} - {date_today}.pdf")

    os.remove(temp_audio_path)
    os.remove(tmp_pdf_path)

elif generate:
    st.warning("Please upload a voice file and enter participant name.")
