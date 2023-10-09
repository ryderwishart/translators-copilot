
## run script example: python alignments/process-ranges-for-alignments.py tpiOTNT-gpt-3.5-turbo-instruct_20230922.jsonl

import os
import re
import json
import argparse
from fuzzywuzzy import process
from tqdm import tqdm
from typing import List, Dict, Union, Optional, Any, NamedTuple
import requests

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process alignment files.')
parser.add_argument('filepath', help='the file to process')
args = parser.parse_args()

# First Script
def assign_macula_tokens_by_vref(normalize_data: list[Dict[str, Any]]) -> List[Dict[str, Any]]:
    
    macula_data: Dict[str, List[Dict[str, Union[str, int]]]] = {}
    if not os.path.exists('data/sources/macula-hebrew.tsv'):
        os.system('wget https://github.com/Clear-Bible/macula-hebrew/raw/main/TSV/macula-hebrew.tsv -O data/sources/macula-hebrew.tsv')
    with open('data/sources/macula-hebrew.tsv', 'r') as file:
        next(file)
        for line in tqdm(file):
            parts = line.strip().split('\t')
            xml_id, ref, text = parts[0], parts[1], parts[3]
            vref = ref.split('!')[0]
            if vref not in macula_data:
                macula_data[vref] = []
            macula_data[vref].append({'text': text, 'id': xml_id})
    if not os.path.exists('data/sources/macula-greek-SBLGNT.tsv'):
        os.system('wget https://github.com/Clear-Bible/macula-greek/raw/main/SBLGNT/tsv/macula-greek-SBLGNT.tsv -O data/sources/macula-greek-SBLGNT.tsv')
    with open('data/sources/macula-greek-SBLGNT.tsv', 'r') as file:
        next(file)
        for line in tqdm(file):
            parts = line.strip().split('\t')
            xml_id, ref, text = parts[0], parts[1], parts[8]
            vref = ref.split('!')[0]
            if vref not in macula_data:
                macula_data[vref] = []
            macula_data[vref].append({'text': text, 'id': xml_id})

    processed_data: List[Dict[str, Any]] = []
    # with open(f'data/alignments/{filename}', 'r') as file:
    for data in tqdm(normalize_data):
        # data = json.loads(line)
        vref = data['vref']
        if vref in macula_data:
            data['macula']['token_ids'] = macula_data[vref]
        processed_data.append(data)
    return processed_data


# Second Script
class RangeResult(NamedTuple):
    startPosition: int
    endPosition: int
    dummy_content: str
    
macula_tokens_not_matched = 0

def find_ranges(dummy_content: str, text: str) -> RangeResult:
    global macula_tokens_not_matched
    text_not_found_in_content_value = RangeResult(startPosition=-1, endPosition=-1, dummy_content=dummy_content)
    if not isinstance(text, str):
        print("text is not string", text)
        return text_not_found_in_content_value
    if not isinstance(dummy_content, str):
        print("dummy_content is not string", text)
        return text_not_found_in_content_value
    
    start_position = dummy_content.find(text)

    if start_position != -1:
        end_position = start_position + len(text)
        dummy_content = dummy_content[:start_position] + '*' * len(text) + dummy_content[end_position:]
        return RangeResult(startPosition=start_position, endPosition=end_position - 1, dummy_content=dummy_content)
    else:
        words = dummy_content.split()
        if words:
            closest_match, score = process.extractOne(text, words) or (None, 0)
            typed_closest_match = str(closest_match)
            
            if score > 30:
                start_position = dummy_content.find(typed_closest_match)
                end_position = start_position + len(typed_closest_match)
                dummy_content = dummy_content[:start_position] + '*' * len(typed_closest_match) + dummy_content[end_position:]
                return RangeResult(startPosition=start_position, endPosition=end_position - 1, dummy_content=dummy_content)
            else: 
                macula_tokens_not_matched  = macula_tokens_not_matched + 1
                return text_not_found_in_content_value
        else:
            return text_not_found_in_content_value


def range_align_macula_tokens(processed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    print(processed_data[0])
    for data in processed_data:
        content: str = data['macula']['content']
        dummy_content = content[:]
        tokens: List[Dict[str, Any]] = data['macula'].get('token_ids', [])
        for i, token in enumerate(tokens):
            if i > 1000:  # arbitrary number, adjust as needed
                print(f"Breaking after {i} iterations for vref {data['vref']}.")
                break
            text = token['text']
            if text == '':
                continue  # Skip empty tokens
            range = find_ranges(dummy_content, text)
            if isinstance(range, RangeResult):
                dummy_content = range.dummy_content  # Update the dummy_content for the next iteration
                token['range'] = {"startPosition": range.startPosition, "endPosition": range.endPosition}
            else:
                print(f"Error for vref {data['vref']}: {range}")

    return processed_data



# Third Script
def range_align_generated_alignments_to_vers(processed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for data in tqdm(processed_data):
        bsb_content = data['bsb']['content']
        macula_content = data['macula']['content']
        target_content = data['target']['content']
        alignment: Any = data.get('alignments') if 'alignments' in data else data.get('alignment') # Handle both 'alignments' and 'alignment' keys
        
        # Check if alignment is None or a string (which means there was an error), and skip processing if it is
        if alignment is None or isinstance(alignment, str):
            print(f"Skipping vref {data['vref']} due to error or None value in alignment data: {alignment}")
            continue
        
        for align in tqdm(alignment):
            for phrase in ['English phrase', 'Macula phrase', 'Target phrase']:
                original_text = align.get(phrase, None)
                if original_text is None:
                    print(f"Warning: Missing key '{phrase}' for vref {data['vref']}")
                    continue
                content = {
                    'English phrase': bsb_content,
                    'Macula phrase': macula_content,
                    'Target phrase': target_content
                }[phrase]
                if not isinstance(content, str):
                    print(f"Error: content is not a string (phrase: {phrase}) (vref: {data['vref']}) content: {content}")
                    continue  # Skip None values
                if content == '':
                    print(f"Error: content is empty string (phrase: {phrase}) (vref: {data['vref']})")  # This is a string, not a list
                    continue  # Skip empty strings
                dummy_content = str(content[:])
                ranges = find_ranges(dummy_content, original_text)
                align[phrase] = {
                    'original-text-value': original_text,
                    'ranges': [{"startPosition": ranges.startPosition, "endPosition": ranges.endPosition}]
                }
    return processed_data


def clean_brackets(s: str) -> str:
    """Remove brackets from a string."""
    return s.replace("[", "").replace("]", "").strip()


def clean_value(value: Any) -> Any:
    """Clean up a value based on its type."""
    if value is None:
        return ""
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, list):
        return [str(v) if isinstance(v, dict) else clean_brackets(v) for v in value]
    else:
        return clean_brackets(value)


def normalize_key(key: str) -> str:
    """Normalize a key based on its contents."""
    key_mappings = {
        "Hebrew": "Macula phrase",
        "Greek": "Macula phrase",
        "Macula": "Macula phrase",
        "English": "English phrase",
        "Spanish": "Target phrase",
        "French": "Target phrase",
        "Tok": "Target phrase"
        # Add more mappings as needed.
    }

    for phrase, normalized in key_mappings.items():
        if phrase in key:
            return normalized
    return key  # default if no matching phrase is found


def normalize_phrases(filepath: str) -> List[Dict[str, Any]]:
    processed_data = []

    with open(f'{filepath}', 'r') as file:
        for line in file:
            # Before parsing JSON, clean up specific keys and values
            # Find "Hebrew phrase" and "Greek phrase" keys and rename them to "Macula phrase"
            line = re.sub(r'"(Hebrew|Greek) phrase":', r'"Macula phrase":', line)
            
            data = json.loads(line)
            if 'alignments' in data:
                normalized_alignments = []

                for alignment in data['alignments']:
                    new_alignment = {}
                    for key, value in alignment.items():
                        clean_key = clean_brackets(key)
                        new_key = normalize_key(clean_key)
                        new_alignment[new_key] = clean_value(value)

                    normalized_alignments.append(new_alignment)

                data["alignments"] = normalized_alignments
            processed_data.append(data)

    return processed_data


def fetch_alignment_keys(normalize_data: list[Dict[str, Any]]) -> set:
    keys = set()

    data = normalize_data
    for entry in data:
        if 'alignments' in entry:
            for alignment in entry['alignments']:
                keys.update(alignment.keys())
                break # end loop once one set is found

    return keys



# Main processing
normalize_data = normalize_phrases(args.filepath)
keys = fetch_alignment_keys(normalize_data)
processed_data = assign_macula_tokens_by_vref(normalize_data)
processed_data = range_align_macula_tokens(processed_data)
final_processed_data = range_align_generated_alignments_to_vers(processed_data)

# Writing the final output
output_filepath = f'{os.path.splitext(args.filepath)[0]}_final_output.jsonl'
print(f"{macula_tokens_not_matched} macula tokens were not matched")
with open(output_filepath, 'w') as outfile:
    for data in final_processed_data:
        outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
