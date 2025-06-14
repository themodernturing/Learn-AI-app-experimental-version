import getpass
import gradio as gr
import openai
import random
import speech_recognition as sr
import logging
import re
import tempfile
from gtts import gTTS
import time
import os
import threading

# Prompt for OpenAI API key at the very start
openai_key = getpass.getpass("🔑 Please enter your OpenAI API key: ")
if not openai_key or not openai_key.startswith("sk-"):
    raise ValueError("A valid OpenAI API key must be provided to run this app.")

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Keep DEBUG for troubleshooting
client = openai.OpenAI(api_key=openai_key)
MODEL = "gpt-3.5-turbo-0125"

# --- AI Learning Mode: Grade-specific explanations and real-life applications ---
AI_CONCEPTS = [
    {
        "concept": "Artificial Intelligence",
        "explanation_3": "AI is like a smart robot that learns by watching you play! It can copy what you do to get better every day. 🤖",
        "explanation_4": "AI means computers can learn from examples and do tasks like humans! They practice a lot to become smarter. 🌟",
        "explanation_5": "AI is when computers learn from data and make decisions like people! They use lots of examples to improve over time. 🚀",
        "explanation_6": "Artificial Intelligence helps computers learn from data, recognize patterns, and think like humans! They get better by practicing with lots of examples. 💡",
        "application_3": "AI helps your phone unlock when it sees your face in Lahore! 😄",
        "application_4": "AI makes video games in Pakistan smarter with fun computer players! 🎮",
        "application_5": "AI powers voice assistants like Siri to help you in Karachi! 🔊",
        "application_6": "AI helps doctors in Islamabad find diseases in X-rays fast! 🩺"
    },
    {
@@ -683,54 +685,64 @@ def clear_all(grade, subject):
        gr.update(visible=False),  # speak_btn
        gr.update(visible=False),  # audio_out
        gr.update(visible=False),  # speak_funfact_btn
        gr.update(visible=False),  # audio_funfact_out
        gr.update(visible=False),  # real_life_app_btn
        gr.update(visible=False),  # next_concept_btn
        gr.update(visible=False),  # btn_ai_exit
        gr.update(visible=False),  # ai_header
        gr.update(visible=False),  # ai_progress
        gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),  # mic_instructions
        gr.update(label="💡 Fun Fact or Real-Life Example", value="", visible=False),  # fun_fact_output
        gr.update(value="", visible=False),  # next_instruction
        gr.update(visible=False)   # clear_output_btn
    )
    input_state = update_input_state(grade, subject)
    logging.debug(f"clear_all took {time.time() - start_time} seconds")
    return reset_outputs + input_state

def tts_output(text):
    start_time = time.time()
    if not text.strip():
        logging.debug(f"tts_output took {time.time() - start_time} seconds")
        return None
    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            logging.debug(f"tts_output took {time.time() - start_time} seconds")
            return fp.name
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp.name)
        temp.close()

        def remove_later(path):
            try:
                time.sleep(5)
                os.remove(path)
            except Exception as e:
                logging.error(f"Error deleting temp file {path}: {e}")

        threading.Thread(target=remove_later, args=(temp.name,), daemon=True).start()
        logging.debug(f"tts_output took {time.time() - start_time} seconds")
        return temp.name
    except Exception as e:
        logging.error(f"Error in tts_output: {e}")
        logging.debug(f"tts_output took {time.time() - start_time} seconds")
        return None

def show_speaker(text):
    start_time = time.time()
    result = gr.update(visible=bool(text.strip()))
    logging.debug(f"show_speaker took {time.time() - start_time} seconds")
    return result

css = """
.input-panel {
    background-color: #e7f5ff;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
}
.output-panel {
    background-color: #fffbe6;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
}
.avatar {
@@ -814,68 +826,68 @@ Revolutionizing Education for Grades 3 to 6""")
            with gr.Row():
                ask_btn = gr.Button(
                    "✅ Ask Now!",
                    variant="primary",
                    elem_id="ask_button",
                    interactive=False
                )
                clear_btn = gr.Button(
                    "🧼 Clear",
                    variant="secondary",
                    elem_id="clear_button"
                )
        with gr.Column(elem_classes="output-panel"):
            ai_header = gr.Markdown("", visible=False)
            ai_progress = gr.Markdown("", visible=False)
            avatar = gr.Markdown("<div class='avatar' role='img' aria-label='Chatbot avatar'>🤖</div>", elem_id="avatar")
            response_output = gr.Textbox(
                label="My Classmate AI Says:",
                lines=5,
                elem_id="response_output",
                interactive=False
            )
            with gr.Row():
                gr.Markdown("")
                speak_btn = gr.Button("🔊 Listen", elem_id="speak_button", visible=False, size="sm")
            audio_out = gr.Audio(label="Listen", elem_id="audio_out", interactive=False, visible=False)
            audio_out = gr.Audio(label="Listen", elem_id="audio_out", interactive=False, visible=False, autoplay=True)
            fun_fact_btn = gr.Button(
                "🎈 Show Me a Fun Fact!", variant="primary", elem_id="fun_fact_button", visible=False
            )
            real_life_app_btn = gr.Button(
                "💡 Real-Life Application", variant="primary", elem_id="real_life_app_btn", visible=False
            )
            fun_fact_output = gr.Textbox(
                label="💡 Fun Fact or Real-Life Example",
                lines=3,
                elem_id="fun_fact_output",
                interactive=False,
                visible=False
            )
            with gr.Row():
                gr.Markdown("")
                speak_funfact_btn = gr.Button("🔊 Listen", elem_id="speak_funfact_btn", visible=False, size="sm")
            audio_funfact_out = gr.Audio(label="Listen", elem_id="audio_funfact_out", interactive=False, visible=False)
            audio_funfact_out = gr.Audio(label="Listen", elem_id="audio_funfact_out", interactive=False, visible=False, autoplay=True)
            with gr.Row():
                next_concept_btn = gr.Button("Next Concept", variant="primary", visible=False)
                btn_ai_exit = gr.Button("Exit AI Mode", variant="secondary", visible=False)
            next_instruction = gr.Markdown("", elem_classes="next-instruction", visible=False)
            with gr.Row():
                gr.Markdown("")
                clear_output_btn = gr.Button("🧼 Start New Question!", variant="primary", visible=False)

    gr.Markdown(
        """<div class='footer-note' role='contentinfo'>
    <strong>Made with ❤️ by <a href='https://astramentors.co' target='_blank'>Astra Mentors</a> | Contact: <a href='mailto:ceo@astramentors.com'>ceo@astramentors.com</a></strong>
    <br>
    <em>We respect your privacy. No student data is stored or shared.</em>
    </div>"""
    )

    grade.change(
        fn=update_input_state,
        inputs=[grade, subject],
        outputs=[question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn]
    )
    subject.change(
        fn=update_input_state,
        inputs=[grade, subject],
        outputs=[question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn]
@@ -1012,45 +1024,37 @@ Revolutionizing Education for Grades 3 to 6""")
            fun_fact_btn, ask_btn, avatar, grade, subject,
            speak_btn, audio_out, speak_funfact_btn, audio_funfact_out,
            real_life_app_btn, next_concept_btn, btn_ai_exit,
            ai_header, ai_progress, mic_instructions, fun_fact_output,
            next_instruction, clear_output_btn,
            question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn
        ]
    )
    clear_output_btn.click(
        fn=clear_all,
        inputs=[grade, subject],
        outputs=[
            response_output, fun_fact_output, question_input, audio_input,
            fun_fact_btn, ask_btn, avatar, grade, subject,
            speak_btn, audio_out, speak_funfact_btn, audio_funfact_out,
            real_life_app_btn, next_concept_btn, btn_ai_exit,
            ai_header, ai_progress, mic_instructions, fun_fact_output,
            next_instruction, clear_output_btn,
            question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn
        ]
    )
    speak_btn.click(
        fn=tts_output,
        inputs=response_output,
        outputs=audio_out
    ).then(
        fn=lambda _: gr.update(visible=True),
        inputs=None,
        outputs=audio_out
    )
    speak_funfact_btn.click(
        fn=tts_output,
        inputs=fun_fact_output,
        outputs=audio_funfact_out
    ).then(
        fn=lambda _: gr.update(visible=True),
        inputs=None,
        outputs=audio_funfact_out
    )

# Launch the app
if __name__ == "__main__":
    start_time = time.time()
    demo.launch(share=True)
    logging.debug(f"App launch took {time.time() - start_time} seconds")
