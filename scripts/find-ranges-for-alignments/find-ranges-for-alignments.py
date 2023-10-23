import os
import re
import json
import argparse
from fuzzywuzzy import process, fuzz
from nltk.util import ngrams
from tqdm import tqdm
from typing import List, Dict, Union, Optional, Any, NamedTuple
import requests

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Process alignment files.')
parser.add_argument('filepath', help='the file to process')
args = parser.parse_args()

print(f"Processing {args.filepath}")

MASK_TOKEN = '*'

# Define a NamedTuple for range results
class RangeResult(NamedTuple):
    startPosition: int
    endPosition: int
    dummy_content: str

# Define a global variable to keep track of unmatched tokens
macula_tokens_not_matched = 0

def download_file(url: str, output_path: str) -> None:
    """Download a file if it does not exist."""
    if not os.path.exists(output_path):
        os.system(f'wget {url} -O {output_path}')

def load_tsv_data(filepath: str, text_index: int) -> Dict[str, List[Dict[str, Union[str, int]]]]:
    """Load data from a TSV file and return a dictionary."""
    data: Dict[str, List[Dict[str, Union[str, int]]]] = {}
    with open(filepath, 'r') as file:
        next(file)
        # for line in tqdm(file):
        for line in file:
            parts = line.strip().split('\t')
            xml_id, ref, text = parts[0], parts[1], parts[text_index]
            vref = ref.split('!')[0]
            if vref not in data:
                data[vref] = []
            data[vref].append({'text': text, 'id': xml_id})
    return data

def assign_macula_tokens_by_vref(normalize_data: list[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Assign macula tokens by vref."""
    # Download necessary files
    download_file('https://github.com/Clear-Bible/macula-hebrew/raw/main/TSV/macula-hebrew.tsv', 'data/sources/macula-hebrew.tsv')
    download_file('https://github.com/Clear-Bible/macula-greek/raw/main/SBLGNT/tsv/macula-greek-SBLGNT.tsv', 'data/sources/macula-greek-SBLGNT.tsv')

    # Load data from TSV files
    macula_data = load_tsv_data('data/sources/macula-hebrew.tsv', 3)
    macula_data.update(load_tsv_data('data/sources/macula-greek-SBLGNT.tsv', 8))

    processed_data: List[Dict[str, Any]] = []
    for data in tqdm(normalize_data):
    # for data in normalize_data:
        vref = data['vref']
        if vref in macula_data:
            data['macula']['token_ids'] = macula_data[vref]
        processed_data.append(data)
    return processed_data

def generate_ngrams(text, n):
    return [' '.join(gram) for gram in ngrams(text.split(), n)]

def find_best_match(text, choices):
    scores = [(choice, fuzz.WRatio(text, choice)) for choice in choices]
    scores = sorted(scores, key=lambda x: (x[1], len(x[0])), reverse=True)
    return scores[0] if scores else (None, 0)

def find_ranges(dummy_content: str, text: str) -> RangeResult:
    global macula_tokens_not_matched
    text_not_found_in_content_value = RangeResult(-1, -1, dummy_content)  # Dummy content, start, end

    if type(text) != str:
        return text_not_found_in_content_value
    
    # Initial simple search
    # FIXME: add some other simple use cases that might allow for strict string matching?
    start_position = dummy_content.find(text)
    if start_position != -1:
        end_position = start_position + len(text)
        dummy_content = dummy_content[:start_position] + MASK_TOKEN * len(text) + dummy_content[end_position:]
        # print(dummy_content)
        return RangeResult(start_position, end_position - 1, dummy_content)

    # If not found, generate N-grams and find the best match
    all_ngrams = []
    for n in range(1, 11):  # NOTE: check 1-grams to 10-grams
        all_ngrams.extend(generate_ngrams(dummy_content, n))

    closest_match, score = find_best_match(text, all_ngrams) # FIXME: we should add a distance penalty as a tie-breaker
    
    if score > 30:
        start_position = dummy_content.find(closest_match)
        end_position = start_position + len(closest_match)
        dummy_content = dummy_content[:start_position] + MASK_TOKEN * len(closest_match) + dummy_content[end_position:]
        # print(dummy_content)
        return RangeResult(start_position, end_position - 1, dummy_content)
    else:
        macula_tokens_not_matched = macula_tokens_not_matched + 1

    return text_not_found_in_content_value

def range_align_macula_tokens(processed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Align macula tokens by range."""
    # for data in processed_data:
    for data in tqdm(processed_data):
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

def range_align_generated_alignments_to_vers(processed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Align generated alignments to verses."""
    for data in tqdm(processed_data):
    # for data in processed_data:
        # print(f'Processing {data}')
        bsb_content = data['bsb']['content']
        macula_content = data['macula']['content']
        target_content = data['target']['content']
        
        dummy_content_dict = {
            'English phrase': str(bsb_content[:]) if isinstance(bsb_content, str) else '',
            'Macula phrase': str(macula_content[:]) if isinstance(macula_content, str) else '',
            'Target phrase': str(target_content[:]) if isinstance(target_content, str) else ''
        }
        
        alignment: Any = data.get('alignments') if 'alignments' in data else data.get('alignment') # Handle both 'alignments' and 'alignment' keys
        
        # Check if alignment is None or a string (which means there was an error), and skip processing if it is
        if alignment is None or isinstance(alignment, str):
            print(f"Skipping vref {data['vref']} due to error or None value in alignment data: {alignment}")
            continue
        
        # for align in tqdm(alignment):
        for align in alignment:
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
                dummy_content = dummy_content_dict[phrase]
                ranges = find_ranges(dummy_content, original_text)
                dummy_content_dict[phrase] = ranges.dummy_content
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


def normalize_phrases(filepath: str, test: str = '') -> List[Dict[str, Any]]:
    """Normalize phrases in a file or a test string."""
    processed_data = []

    if test != '':
        test = test.replace('\\', '\\\\\\')
        data = json.loads(test)
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

    else:
        with open(f'{filepath}', 'r') as file:
            for line in file:
                # Before parsing JSON, clean up specific keys and values
                # Find "Hebrew phrase" and "Greek phrase" keys and rename them to "Macula phrase"
                line = re.sub(r'"(Hebrew|Greek) phrase":', r'"Macula phrase":', line)
                line = re.sub(r'\\', r'\\\\\\', line)
                
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
    """Fetch alignment keys from normalized data."""
    keys = set()

    data = normalize_data
    for entry in data:
        if 'alignments' in entry:
            for alignment in entry['alignments']:
                keys.update(alignment.keys())
                break # end loop once one set is found

    return keys


test_data = '''{"vref": "GEN 1:11", "bsb": {"vref": "GEN 1:11", "content": "Then God said, “Let the earth bring forth vegetation: seed-bearing plants and fruit trees, each bearing fruit with seed according to its kind.” And it was so."}, "macula": {"vref": "GEN 1:11", "content": "וַיֹּ֣אמֶר אֱלֹהִ֗ים תַּֽדְשֵׁ֤א הָאָ֨רֶץ֙ דֶּ֔שֶׁא עֵ֚שֶׂב מַזְרִ֣יעַ זֶ֔רַע עֵ֣ץ פְּרִ֞י עֹ֤שֶׂה פְּרִי֙ לְמִינ֔וֹ אֲשֶׁ֥ר זַרְעוֹ־ ב֖וֹ עַל־ הָאָ֑רֶץ וַֽיְהִי־ כֵֽן׃"}, "target": {"vref": "GEN 1:11", "content": "Entonces ʼElohim dijo: Produzca la tierra vegetación: hierba que haga germinar semilla y árbol frutal que dé fruto sobre la tierra según su especie, cuya semilla esté en él. Y fue así."}, "alignments": [{"Spanish phrase": "Entonces ʼElohim dijo:", "English phrase": "Then God said,", "Hebrew phrase": "וַיֹּ֣אמֶר אֱלֹהִ֗ים"}, {"Spanish phrase": "Produzca la tierra vegetación:", "English phrase": "\\\"Let the earth bring forth vegetation:", "Hebrew phrase": "תַּֽדְשֵׁ֤א הָאָ֨רֶץ֙ דֶּ֔שֶׁא"}, {"Spanish phrase": "hierba que haga germinar semilla", "English phrase": "seed-bearing plants", "Hebrew phrase": "עֵשֶׂב מַזְרִיעַ זרע"}, {"Spanish phrase": "y árbol frutal que dé fruto sobre la tierra", "English phrase": "\\\"and fruit trees, each bearing fruit with seed according to its kind.\\\"", "Hebrew phrase": "\\\"עץ פרי עושה פרי למינו\\\""}, {"Spanish phrase": ", cuya semilla esté en él.", "English phrase": "\\\"And it was so.\\\"", "Hebrew phrase": "\\\"אשר זרעו בו. ויהי-כן\\\""}]}'''

# Main processing
if args.filepath == 'test':
    normalize_data = normalize_phrases('test', test=test_data)
else:
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

# TODO: add a coverage report for outputs like the following
'''
Error: content is not a string (phrase: English phrase) (vref: JHN 5:4) content: nan
Error: content is not a string (phrase: English phrase) (vref: JHN 5:4) content: nan
 85%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▏                       | 26364/31102 [02:29<00:05, 870.10it/s]Warning: Missing key 'Macula phrase' for vref JHN 8:8
Warning: Missing key 'Macula phrase' for vref JHN 8:8
Warning: Missing key 'Macula phrase' for vref JHN 8:8
 87%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                     | 26924/31102 [02:30<00:07, 580.87it/s]Skipping vref ACT 2:34 due to error or None value in alignment data: None
 87%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▍                   | 27210/31102 [02:31<00:05, 770.77it/s]Skipping vref ACT 8:37 due to error or None value in alignment data: None
 88%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▋                  | 27455/31102 [02:31<00:05, 722.11it/s]Skipping vref ACT 15:34 due to error or None value in alignment data: None
 89%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▍                 | 27607/31102 [02:31<00:04, 699.35it/s]Skipping vref ACT 19:41 due to error or None value in alignment data: None
 89%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▉                 | 27708/31102 [02:31<00:04, 779.56it/s]Skipping vref ACT 24:7 due to error or None value in alignment data: None
 90%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▋                | 27854/31102 [02:32<00:05, 565.76it/s]Skipping vref ACT 28:29 due to error or None value in alignment data: None
 91%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▊              | 28266/31102 [02:32<00:02, 1017.48it/s]Skipping vref ROM 16:24 due to error or None value in alignment data: None
 93%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▏          | 28940/31102 [02:32<00:01, 1485.82it/s]Error: content is empty string (phrase: Macula phrase) (vref: 2CO 13:14)
Error: content is empty string (phrase: Target phrase) (vref: 2CO 13:14)
Error: content is empty string (phrase: Macula phrase) (vref: 2CO 13:14)
Error: content is empty string (phrase: Target phrase) (vref: 2CO 13:14)
Error: content is empty string (phrase: Macula phrase) (vref: 2CO 13:14)
Error: content is empty string (phrase: Target phrase) (vref: 2CO 13:14)
Error: content is empty string (phrase: Macula phrase) (vref: 2CO 13:14)
Error: content is empty string (phrase: Target phrase) (vref: 2CO 13:14)
 94%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████▍        | 29389/31102 [02:33<00:00, 1891.57it/s]Warning: Missing key 'Macula phrase' for vref PHP 4:3
Warning: Missing key 'Macula phrase' for vref PHP 4:3
Warning: Missing key 'Macula phrase' for vref PHP 4:3
Warning: Missing key 'Macula phrase' for vref PHP 4:3
Warning: Missing key 'Macula phrase' for vref PHP 4:3
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 31102/31102 [02:34<00:00, 200.93it/s]
4242 macula tokens were not matched
'''