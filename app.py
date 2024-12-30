def extract_translatable_strings(passage):
    var_names = (f"var_{i}" for i in range(1, 1000))  # Adjust the range if needed

    def replace_plain_text(match):
        nonlocal var_names
        try:
            variable = next(var_names)  # Try to get the next variable name
        except StopIteration:
            raise ValueError(
                "Ran out of variable names while replacing plain text. Ensure enough variable names are available."
            )
        return f"<{variable}>"

    # Apply the replacement logic
    passage = re.sub(r"(?<!>)(?<!\\)([^\n<]+?)(?=<|$)", replace_plain_text, passage)

    # Extract variable definitions for the plain text
    var_definitions = {var_name: match.group(1).strip() for var_name, match in zip(var_names, re.finditer(r"(?<!>)(?<!\\)([^\n<]+?)(?=<|
