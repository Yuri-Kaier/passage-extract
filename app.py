import re

def extract_translatable_strings(passage):
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
