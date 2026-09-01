import json

def append_dict_to_file(file_path, data_dict):
    # Open the file in append mode ('a') with utf-8 encoding
    with open(file_path, 'a', encoding='utf-8') as file:
        # Convert the dictionary to a JSON string and append it to the file
        file.write(json.dumps(data_dict, ensure_ascii=False))
        file.write('\n')  # Add a newline for each new dictionary entry
def append_text_to_file(file_path, text):
    # Open the file in append mode ('a') with utf-8 encoding
    with open(file_path, 'a', encoding='utf-8') as file:
        # Convert the dictionary to a JSON string and append it to the file
        file.write(text)
        file.write('\n')  # Add a newline for each new dictionary entry
