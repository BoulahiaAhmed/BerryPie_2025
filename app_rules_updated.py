import streamlit as st
from chatbot import BerryPieChatbot
from groq_models_v2 import fca_checker_results, video_card_generation, reviewed_transcript
from video_processing import transcribe_audio_with_whisper, extract_audio_from_video, video_media_processing
import time
import os
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher


default_system_message = """
You are a compliance officer. Your task is to review the following rule and verify whether the provided sales deck complies with it.
Be flexible and not very strict when reviewing the sales deck. Tend to validate rules more than refuse.
The rule should be considered violated only if the sales deck completely disregards it, in all other cases, accept and validate compliance.

Provide your evaluation in JSON format with the following fields:
- rule_name (str): The name or identifier of the rule being evaluated.
- label (bool): Return true if the sales deck complies with the rule, otherwise return false.
- part (list[str]): List of specific text parts from the sales deck that relate directly to the rule, and if the sales deck is missing text related to the rule violation, simply add: "no related content for this rule
- suggestion (list[str]): A list of recommended changes or improvements for each text mentioned in part. If no changes are needed and the rule is fully respected, leave this field empty.

Ensure the output is following this JSON schema:
{
  "rule_name": "",
  "label": true OR false,
  "part": [],
  "suggestion": []
}
"""

fca_handbook_full_names = [
    "Financial Services and Markets Act (FSMA)",
    "FCA Consumer Credit sourcebook (CONC)",
    "FCA Principles for Businesses (PRIN)",
    "FCA Conduct of Business Sourcebook (COBS)",
    "Financial promotions on social media"
] # used for user interface only

fca_handbook_list = ["FSMA", "FCA CONC", "FCA PRIN", "FCA COBS", "Financial promotions on social media"]

Clear_Fair_and_Not_Misleading = {
    'rule_name': "Clear, Fair, and Not Misleading",
    'handbooks': [fca_handbook_list[1], fca_handbook_list[2], fca_handbook_list[3], fca_handbook_list[4]],
    'rule_text': "The video's content must be presented clearly, fairly, and in a way that doesn't mislead viewers. This applies to the overall message, the presentation of risks and benefits, and any claims or statements made."
}

Transparent_and_Fair_Terms_and_Comparisons = {
    'rule_name': "Transparent and Fair Terms and Comparisons",
    'handbooks': [fca_handbook_list[1], fca_handbook_list[3]],
    'rule_text': "The video content must use terms like 'guaranteed,' 'protected,' or 'secure' only if they are fully backed by clear, accurate information, with any risks clearly highlighted. For products with complex fees or payments, provide enough detail to ensure viewers understand the costs. Comparisons with other products should be fair, balanced, and easy to understand."
}

Disclosure_of_Risks_for_Credit_and_BNPL_Offers = {
    'rule_name': "Disclosure of Risks for Credit and BNPL Offers",
    'handbooks': [fca_handbook_list[1], fca_handbook_list[3]],
    'rule_text': "In case of video content promoting 'Buy Now, Pay Later' (BNPL) or credit offers, any risks must be clearly disclosed. This includes interest rates after promotions, conditions where interest may apply, and potential impacts on credit ratings. For debt solutions, explain any possible increase in the total payable amount, changes in repayment terms, or credit rating effects."
}

Risk_Warnings = {
    'rule_name': "Risk Warnings",
    'handbooks': [fca_handbook_list[1], fca_handbook_list[3], fca_handbook_list[4]],
    'rule_text': "The video must include clear and prominent risk warnings, especially if it features high-cost short-term credit (HCSTC) products or high-risk investments (HRIs). These warnings should be easily visible and understandable, not hidden in captions or supplementary text."
}

Consumer_Understanding = {
    'rule_name': "Consumer Understanding",
    'handbooks': [fca_handbook_list[2], fca_handbook_list[4]],
    'rule_text': "The video should be designed to be easily understood by its target audience. It should avoid using jargon or complex language, particularly when targeting retail clients. The information should be presented in a way that avoids confusion and empowers viewers to make informed decisions."
}

Avoidance_of_High_Pressure_Selling = {
    'rule_name': "Avoidance of High-Pressure Selling",
    'handbooks': [fca_handbook_list[1]],
    'rule_text': "The video should not employ high-pressure tactics or create an undue sense of urgency. Viewers should be given adequate time to consider their options without feeling pressured or manipulated."
}

rules_list = [Clear_Fair_and_Not_Misleading, Transparent_and_Fair_Terms_and_Comparisons, Disclosure_of_Risks_for_Credit_and_BNPL_Offers, Risk_Warnings, Consumer_Understanding, Avoidance_of_High_Pressure_Selling]

@st.cache_resource
def get_book_rule_status_and_suggestion(handbook_name: str, transcript_review_output: dict):
    handbook_rules_names = []
    for rule in rules_list:
        if handbook_name in rule['handbooks']:
            handbook_rules_names.append(rule["rule_name"])
    handbook_rules_status = {rule_name: "Respected" for rule_name in handbook_rules_names}
    for suggestion in transcript_review_output['suggestions']:
        if suggestion['not_respected_rule'] in handbook_rules_names:
            handbook_rules_status[suggestion['not_respected_rule']] = {'responsible_parts':suggestion['responsible_parts'], 
                                                                        'suggestions':suggestion['suggestions']}
    return handbook_rules_status


global transcript_text
transcript_text = ""


# Define the main function
def main_app():
    # Set the title of the app
    st.image("./logo.png", width=200)
    st.markdown("<h1 style='text-align: center;'>Audio-Visual Compliance Checker 🔍📋</h1>", unsafe_allow_html=True)
    st.divider()
    st.subheader("🎬 Video Upload, Audio Extraction, and Transcription")

    # File uploader for video files
    video_file = st.file_uploader("Upload a Video", type=["mp4", "mov", "avi", "mkv"])

    if video_file is not None:
        # Create the directory if it doesn't exist
        temp_video_dir = "temp_video"
        os.makedirs(temp_video_dir, exist_ok=True)
        # Save the uploaded video to the directory
        temp_video_path = os.path.join(temp_video_dir, video_file.name)
        with open(temp_video_path, "wb") as f:
            f.write(video_file.read())
        
        if video_file is not None:
            # Create the directory for the audio if it doesn't exist
            temp_audio_dir = "temp_audio"
            os.makedirs(temp_audio_dir, exist_ok=True)
            # Define the path for the extracted audio file
            temp_audio_path = os.path.join(temp_audio_dir, "extracted_audio.mp3")
            # Extract audio from the video
            audio_path = extract_audio_from_video(temp_video_path, temp_audio_path)
        
        st.success("Audio extracted successfully!")

        # Display the video
        st.video(video_file)

        # Transcribe the audio using Whisper
        st.write("Transcribing audio...")
        sales_deck = transcribe_audio_with_whisper(audio_path)
        st.text_area("Video Transcript:", sales_deck, height=400)
    
    # Initialization
    if 'sales_deck' not in st.session_state:
        st.session_state['sales_deck'] = sales_deck

    # st.divider()
    # st.subheader('✨ AI Model Selection')
    # # Dropdown to select the model
    # appearing_model_name = st.radio("Select Model", ['llama-3.1-70b', 'llama-3.2-90b', 'mixtral-8x7b', 'gemma2-9b'], horizontal=True)

    # if appearing_model_name == 'llama-3.1-70b':
    #     model_name = 'llama-3.1-70b-versatile'
    #     st.info("Rate limit: 30 Request Per Minute")

    # if appearing_model_name == 'llama-3.2-90b':
    #     model_name = 'llama-3.2-90b-text-preview'
    #     st.info("Rate limit: 30 Request Per Minute")

    # if appearing_model_name == 'mixtral-8x7b':
    #     model_name = 'mixtral-8x7b-32768'
    #     st.info("Rate limit: 30 Request Per Minute")

    # if appearing_model_name == 'gemma2-9b':
    #     model_name = 'gemma2-9b-it'
    #     st.info("Rate limit: 30 Request Per Minute")

    # default model selected 'llama-3.2-90b-text-preview'
    model_name = 'llama-3.3-70b-versatile'

    # New rules section (no user interference)
    st.divider()
    st.subheader('👮 AI FCA Officer: Compliance Handbooks List')

    st.write("The AI officer will automatically check and verify the rules related to these compliance Handbooks:")

    # Create an expander for the rules section
    with st.expander("📜 View the list of FCA Compliance Handbooks", expanded=False):
        for i, elm in enumerate(fca_handbook_full_names):
            st.write(f"**{elm}**")

    system_message = default_system_message
    st.divider()
    st.subheader('🚦 Running Compliance Checker for Audio/Visual Analysis')
    st.write("Our AI-powered Compliance Checker will analyze your audio and visual content for regulatory compliance, offering corrections for any detected issues before publishing.")
    # Call the generate function
    generate_output = st.button('Check Compliance')
    if generate_output:
        start = time.time()
        with st.spinner(text="Reviewing In progress..."):
            with ThreadPoolExecutor() as executor:
                # Submit both tasks to run in parallel
                future_transcript = executor.submit(fca_checker_results, rules_list, system_message, model_name, sales_deck)
                future_video = executor.submit(video_media_processing, temp_video_path)
                
                # Get results
                transcript_review_output = future_transcript.result()
                video_review_output = future_video.result()
                output = {'transcript_review_output': transcript_review_output, 'video_review_output': video_review_output}

        end = time.time()

        st.write(f"Reviewing Duration: {end-start:.2f} seconds")

        st.subheader("Audio Media reviewing results")
        for handbook in fca_handbook_list:
            if handbook in output['transcript_review_output']['not_respected_fca_handbooks']:
                with st.expander(f"{handbook} ❌", expanded=False):
                    handbook_rules_status = get_book_rule_status_and_suggestion(handbook, transcript_review_output)
                    for rule in handbook_rules_status.keys():
                        if isinstance(handbook_rules_status[rule], str):
                            st.write(f"{rule} ✔️")
                        else:
                            st.write(f"{rule} ❌")
                            with st.popover("Responsible Parts & Suggestions"):
                                for i, part in enumerate(handbook_rules_status[rule]['responsible_parts']):
                                    st.write(f"{i+1} Part to modify: {part}")
                                    st.write(f"Suggestion: {handbook_rules_status[rule]['suggestions'][i]}")
                                    st.divider()
            else:
                with st.expander(f"{handbook} ✔️", expanded=False):
                    handbook_rules_status = get_book_rule_status_and_suggestion(handbook, transcript_review_output)
                    for rule in handbook_rules_status.keys():
                        st.write(f"{rule} ✔️")

        st.subheader("Video Media reviewing results")
        disclaimer_status = output['video_review_output']["disclaimer_is_exist"]
        disclaimer_text = output['video_review_output']["disclaimer_text"]
        if disclaimer_status:
            st.write("Disclaimer Exist ✔️")
            st.write("Disclaimer: ", disclaimer_text)
        else:
            st.write("No disclaimer found! Please add one ⚠️")
        print(len(output['transcript_review_output']['not_respected_fca_handbooks']))
        if len(output['transcript_review_output']['not_respected_fca_handbooks']) > 0:

            print("heeeeeee")
            # Title of the section
            st.subheader('🎥 Compliance Video Transcript Generator')

            # New component to display and edit the video transcript
            st.write("Here is the generated transcript for your video. Feel free to edit it if necessary.")

            def filter_fca_handbooks(dict_list):
                # Create a new list of dicts with only the required keys
                filtered_list = []
                
                for output_dict in dict_list:
                    # Extract the 'not_respected_rules' and 'suggestions' fields
                    filtered_dict = {
                        'not_respected_rules': output_dict.get('not_respected_rules'),
                        'suggestions': output_dict.get('suggestions')
                    }
                    filtered_list.append(filtered_dict)
                
                return filtered_list

            # use the previous function to keep only the parts and suggestions in the dict
            partes_and_suggestions_to_follow = filter_fca_handbooks(output['transcript_review_output']['suggestions'])

            print("--------------------------------------------------")
            print(partes_and_suggestions_to_follow)
            print("--------------------------------------------------")

            def get_word_differences(original, modified):
                # Split the strings into lists of words
                original_words = original.split()
                modified_words = modified.split()
                
                # Use SequenceMatcher to get a list of matched and unmatched segments
                matcher = SequenceMatcher(None, original_words, modified_words)
                result = ""
                
                for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                    if tag == 'equal':
                        # Words are the same in both strings
                        result += " ".join(original_words[i1:i2]) + " "
                    elif tag == 'replace' or tag == 'insert':
                        # Words in the modified string that differ or are new
                        result += "<span style='color: green;'>" + " ".join(modified_words[j1:j2]) + "</span> "
                    # We ignore deletions from the original string to focus on added/modified words
                
                return result.strip()

            # Assuming transcript_text is generated from the reviewed_transcript function
            transcript_text = reviewed_transcript(sales_deck, partes_and_suggestions_to_follow, model_name)

            # Highlight the modified words
            highlighted_transcript = get_word_differences(sales_deck, transcript_text)

            # Display with Streamlit, setting `unsafe_allow_html=True` to allow HTML rendering
            st.markdown(f"<p style='font-size: 18px;'>{highlighted_transcript}</p>", unsafe_allow_html=True)

            # with st.expander(f"Edit the video transcript if needed:", expanded=False):

            #     # Create a text area for the user to view and modify the transcript
            #     modified_text = st.text_area('Modify here:', transcript_text, height=400)

            # Step 4: Provide download button for saving the modified transcript
            def generate_txt_file(content):
                return content

            # Create a download button for the user
            st.download_button(
                label="Download Transcript as .txt",
                data=generate_txt_file(transcript_text),
                file_name="modified_transcript.txt",
                mime="text/plain"
            )
        else:
            st.write("You video respect all the rules congrats!")

    st.divider()
    st.subheader('🏷️ Product Card Generation')
    st.write("Let our AI generates metadata for your video!")
    generate_model_card = st.button('Product card')
    if generate_model_card:
        with st.spinner(text="Generation In progress..."):
            video_card = video_card_generation(sales_deck, model_name)
        st.markdown(video_card)


if 'sales_deck' in st.session_state:
    transcript = st.session_state['sales_deck']
else:
    transcript = ""

# Initialize chatbot
@st.cache_resource
def get_chatbot():
    return BerryPieChatbot(transcript)


chatbot = get_chatbot()


# Define your chatbot page
def chatbot_page():
    st.title("Virtual Assistant")
    
    # Chat message history container
    chat_container = st.container()

    # Display the previous conversation if exists
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Show chat history
    for message in st.session_state.messages:
        if message['role'] == 'user':
            chat_container.chat_message("user").write(message['content'])
        else:
            chat_container.chat_message("assistant").write(message['content'])

    # Input chat message
    if prompt := st.chat_input("Hello, How can we help you?"):
        # Append user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get the chatbot's response
        response = chatbot.chat(prompt)
        
        # Append assistant's response to history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Redisplay the chat
        for message in st.session_state.messages:
            if message['role'] == 'user':
                chat_container.chat_message("user").write(message['content'])
            else:
                chat_container.chat_message("assistant").write(message['content'])


# Main function that controls the app
def main():
    # Use radio buttons as tabs
    tab = st.radio("Navigation", ["Main App", "Chatbot"], index=0, horizontal=True)

    # Display corresponding page based on the selected tab
    if tab == "Main App":
        main_app()
    elif tab == "Chatbot":
        chatbot_page()


# Run the app
if __name__ == "__main__":
    main()