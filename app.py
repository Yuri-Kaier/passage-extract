import re
import string
import streamlit as st

def extract_translatable_strings(passage):
    var_names = iter(string.ascii_lowercase)
    var_map = {}

    def replace_dialogue(match):
        nonlocal var_names
        variable = next(var_names)
        var_map[variable] = match.group(1).strip()
        return f"</b>: {{{variable}}}</div>"

    passage = re.sub(r"</b>:\s*(.*?)</div>", replace_dialogue, passage)

    def replace_plain_text(match):
        nonlocal var_names
        variable = next(var_names)
        var_map[variable] = match.group(1).strip()
        return f" {{{{{variable}}}}} "

    passage = re.sub(r"(?<!>)(?<!\\)([^\n<]+?)(?=<|$)", replace_plain_text, passage)

    def replace_fork(match):
        nonlocal var_names
        variable = next(var_names)
        fork_text = match.group(1).strip()
        if "->" not in fork_text:
            fork_text = f"{fork_text}->{fork_text}"
        var_map[variable] = fork_text
        return f">>[{{{variable}}}]"

    passage = re.sub(r">>\[\[([^]]+?)\]\]", replace_fork, passage)
    var_definitions = [f"{var} = \"{text}\"" for var, text in var_map.items()]
    return passage, "\n".join(var_definitions)

st.title("Twine Passage Translatable Strings Extractor")

# Input section
twine_passage = st.text_area("Paste your Twine passage here:", height=300)

if st.button("Process Passage"):
    if twine_passage.strip():
        modified_passage, var_definitions = extract_translatable_strings(twine_passage)
        
        # Display results
        st.subheader("Modified Passage:")
        st.code(modified_passage, language="text")
        
        st.subheader("Variable Definitions:")
        st.code(var_definitions, language="text")
    else:
        st.error("Please enter a Twine passage.")
