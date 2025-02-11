import streamlit as st
import re

def process_twine_passage(passage_name, twine_passage):
    """
    Processes a Twine passage to generate two output formats.

    Args:
        passage_name (str): The name of the Twine passage.
        twine_passage (str): The input Twine passage text.

    Returns:
        tuple: A tuple containing Output 1 (str) and Output 2 (str).
    """

    vars_section = ""
    text_content = twine_passage

    if "--" in twine_passage:
        parts = twine_passage.split("--", 1)
        vars_section = parts[0].strip() + "\n--"
        text_content = parts[1]

    dialogues = []
    forks_text = []

    # Extract dialogues from chat containers
    def extract_dialogue(match):
        dialogue_text = match.group(1).strip()
        dialogues.append(dialogue_text)
        return f"<b>{{variable_{len(dialogues)}}}</b>: {{variable_content_{len(dialogues)}}}"

    def replace_dialogue_vars(text):
        text = re.sub(r"<b>(.*?)</b>: (.*?)(?=\s*</div>)", lambda match: f"<b>{match.group(1)}</b>: {{variable_content_{dialogues_index.pop(0)}}}", text, flags=re.DOTALL)
        text = re.sub(r"<b>(.*?)</b>:(.*?)(?=</div>)", lambda match: f"<b>{match.group(1)}</b>: {{variable_content_{dialogues_index.pop(0)}}}", text, flags=re.DOTALL)
        return text


    processed_text_output1 = text_content

    dialogues_index = []
    dialogue_counter = 1

    # First pass to collect dialogues and forks in order
    temp_text = text_content
    dialogue_matches = []

    for match in re.finditer(r"<div class=\"chat-container.*?>(.*?)<div class=\"text-box.*?\">(.*?)</div>.*?</div>", temp_text, re.DOTALL):
        dialogue_text = re.search(r"<b>.*?</b>:(.*)", match.group(2), re.DOTALL)
        if dialogue_text:
            dialogues.append(dialogue_text.group(1).strip())
            dialogues_index.append(dialogue_counter)
            dialogue_counter += 1

    for match in re.finditer(r"<div class=\"chat-container-j.*?>(.*?)<div class=\"text-box-j.*?>(.*?)</div>.*?</div>", temp_text, re.DOTALL):
        dialogue_text = re.search(r"<b>.*?</b>:(.*)", match.group(2), re.DOTALL)
        if dialogue_text:
            dialogues.append(dialogue_text.group(1).strip())
            dialogues_index.append(dialogue_counter)
            dialogue_counter += 1

    # Replace dialogues with variables in Output 1
    dialogues_index_copy = dialogues_index[:] # Create a copy to avoid modifying the original in place
    processed_text_output1 = replace_dialogue_vars(processed_text_output1)


    forks = []
    fork_counter = 1
    forks_index = []

    def replace_forks_vars(text):
        def fork_replace(match):
            forks_index.append(fork_counter)
            nonlocal fork_counter
            fork_counter += 1
            fork_text_full = match.group(1)
            if "->" in fork_text_full:
                parts = fork_text_full.split("->", 1)
                fork_display_text = parts[0]
                fork_target = parts[1]
                forks_text.append(fork_display_text)
                return f">>{{variable_fork_{forks_index[-1]}}}->{fork_target}"
            else:
                forks_text.append(fork_text_full)
                return f">>{{variable_fork_{forks_index[-1]}}}->{fork_text_full}"

        return re.sub(r">>\s*\[\[(.*?)\]\]", fork_replace, text)

    processed_text_output1 = replace_forks_vars(processed_text_output1)


    output1_lines = []
    if vars_section:
        output1_lines.append(vars_section)

    var_char_dialogue = ord('a')
    var_map_dialogue = {}
    for i in range(len(dialogues)):
        var_name = chr(var_char_dialogue + i)
        var_map_dialogue[f"{{variable_content_{i+1}}}" ] = f"{{{var_name}}}"

    temp_output1 = processed_text_output1
    for old_var, new_var in var_map_dialogue.items():
        temp_output1 = temp_output1.replace(old_var, new_var)
    output1_lines.append(temp_output1.strip())


    var_char_fork = ord('h')
    var_map_fork = {}
    for i in range(len(forks_text)):
        var_name = chr(var_char_fork + i)
        var_map_fork[f"{{variable_fork_{i+1}}}" ] = f"{{{var_name}}}"


    temp_output1_fork = "\n".join(output1_lines)
    for old_var, new_var in var_map_fork.items():
        temp_output1_fork = temp_output1_fork.replace(old_var, new_var)
    output1 = temp_output1_fork


    note_content_lines = ["[note]"]

    dialogue_index_note = 0
    for match in re.finditer(r"<div class=\"chat-container.*?>(.*?)<div class=\"text-box.*?\">(.*?)</div>.*?</div>", text_content, re.DOTALL):
        dialogue_text = re.search(r"<b>.*?</b>:(.*)", match.group(2), re.DOTALL)
        if dialogue_text:
            speaker_match = re.search(r"<b>(.*?)</b>:", match.group(2), re.DOTALL)
            speaker = speaker_match.group(1) if speaker_match else "Narrator"
            note_content_lines.append(f"<b>{{{speaker}}}</b>: {dialogues[dialogue_index_note].strip()}")
            dialogue_index_note += 1

    for match in re.finditer(r"<div class=\"chat-container-j.*?>(.*?)<div class=\"text-box-j.*?>(.*?)</div>.*?</div>", text_content, re.DOTALL):
        dialogue_text = re.search(r"<b>.*?</b>:(.*)", match.group(2), re.DOTALL)
        if dialogue_text:
            speaker_match = re.search(r"<b>(.*?)</b>:", match.group(2), re.DOTALL)
            speaker = speaker_match.group(1) if speaker_match else "Narrator"
            note_content_lines.append(f"<b>{{{speaker}}}</b>: {dialogues[dialogue_index_note].strip()}")
            dialogue_index_note += 1


    fork_index_note = 0
    for match in re.finditer(r">>\s*\[\[(.*?)\]\]", text_content, re.DOTALL):
        fork_text_full = match.group(1)
        note_content_lines.append(forks_text[fork_index_note].strip())
        fork_index_note += 1

    note_content_lines.append("[continued]")
    note_section = "\n".join(note_content_lines)

    output1_with_note = output1 + "\n\n" + note_section


    output2_lines = []
    var_char_output2 = ord('a')
    for dialogue_item in dialogues:
        var_name = chr(var_char_output2)
        output2_lines.append(f"{passage_name}\t{var_name}\t{dialogue_item.strip()}")
        var_char_output2 += 1

    var_char_fork_output2 = ord('h')
    for fork_item in forks_text:
        var_name = chr(var_char_fork_output2)
        output2_lines.append(f"{passage_name}\t{var_name}\t{fork_item.strip()}")
        var_char_fork_output2 += 1


    output2 = "\n".join(output2_lines)

    return output1_with_note, output2

st.title("Twine Passage Processor")

uploaded_file = st.file_uploader("Upload your Twine passage text file (.txt)", type=["txt"])
passage_name_input = st.text_input("Enter Passage Name:")

if uploaded_file is not None and passage_name_input:
    try:
        twine_passage_text = uploaded_file.read().decode("utf-8")
        output1, output2 = process_twine_passage(passage_name_input, twine_passage_text)

        st.subheader("Output 1")
        st.code(output1, language="text") # Use st.code for better formatting of code-like text

        st.subheader("Output 2")
        st.code(output2, language="text") # Use st.code for better formatting of code-like text

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error("Please make sure your uploaded file is a valid text file and the passage name is provided.")
elif uploaded_file is not None and not passage_name_input:
    st.warning("Please enter the Passage Name.")
elif passage_name_input and uploaded_file is None:
    st.warning("Please upload a Twine passage text file.")
else:
    st.info("Upload a Twine passage text file and enter the Passage Name to process.")
