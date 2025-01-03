import streamlit as st
import re

def extract_translatable_strings(passage):
    """
    Extracts plain text from a passage and replaces it with variable placeholders.
    Returns the modified passage and a dictionary of variable definitions.
    """
    var_names = (f"var_{i}" for i in range(1, 1000))  # Adjust range if needed

    def replace_plain_text(match):
        nonlocal var_names
        try:
            variable = next(var_names)  # Get the next variable name
        except StopIteration:
            raise ValueError(
                "Ran out of variable names while replacing plain text. Ensure enough variable names are available."
            )
        return f"<{variable}>"

    # Replace plain text in the passage
    passage = re.sub(r"(?<!>)(?<!\\)([^\n<]+?)(?=<|$)", replace_plain_text, passage)

    # Extract variable definitions for the plain text
    var_definitions = {var_name: match.group(1).strip() for var_name, match in zip(
        (f"var_{i}" for i in range(1, 1000)), 
        re.finditer(r"(?<!>)(?<!\\)([^\n<]+?)(?=<|$)", passage)
    )}

    return passage, var_definitions


# Streamlit UI
st.title("Translatable Strings Extractor")

st.write("Paste your Twine passage below:")

# Input text area
input_passage = st.text_area(
    "Input Passage",
    placeholder="Paste your Twine passage here...",
    height=300
)

if st.button("Extract Translatable Strings"):
    if input_passage.strip():
        try:
            # Process the input and display the output
            modified_passage, var_definitions = extract_translatable_strings(input_passage)
            
            st.subheader("Modified Passage:")
            st.code(modified_passage, language="text")
            
            st.subheader("Variable Definitions:")
            st.json(var_definitions)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please paste a passage before clicking 'Extract Translatable Strings'.")
