import openai
import os 
import json
import random

openai.api_key = os.environ['OPENAI_API_KEY']
openai.organization = 'org-TKu0EilyBURjOa59qJxK0hHb' # FIXME: use env

MAX_RETRIES = 2

### PARSE ARGS ###

import argparse

# Create the argument parser
parser = argparse.ArgumentParser(description='Script to parse command line arguments.')

# Add the arguments
parser.add_argument('--run_name', type=str, default='default_run', help='Name of the run')
parser.add_argument('--data_path', type=str, default='/Users/ryderwishart/translators-copilot/data/bible/spapddpt.json', help='Path to the data file')
parser.add_argument('--model', type=str, default='gpt-3.5-turbo-instruct', help='Name of the model')
parser.add_argument('--n', type=int, default=5, help='Number of verses to sample')

# Parse the arguments
args = parser.parse_args()

# Print the parsed arguments
print(f"Run Name: {args.run_name}")
print(f"Data Path: {args.data_path}")
print(f"Model: {args.model}")
print(f"Number of Verses to Sample: {args.n}")



data = args.data_path
bible_name = args.run_name
selected_model = args.model


### ALIGNMENT FUNCTIONS ###
def generate_broad_greek_alignment_prompt(verse):
    bsb, macula, target = verse['bsb']['content'], verse['macula']['content'], verse['target']['content']
    try:
        return f'''Here are some general facts to note about Spanish:
Spanish is a fusional language, ensure correct affix attachment; follow SVO order; mark verbs for tense, aspect, mood.
For translating from Greek: replace Greeks's three-gender system with Spanish's two-gender system, ensuring agreement; shift to SVO order; adapt Greek Voice/Aspect/Mood markings to Spanish system.

Translation style:
The Spanish translation is  a literal translation trying to stick closely to the Greek word order, but there may occasionally be instances where Spanish phrases differ to produce a more natural translation.

Here is a sentence:
Spanish: —¿Qué es lo que ha pasado? —preguntó. Ellos respondieron: —Lo de Jesús de Nazaret. Era un profeta poderoso en obras y en palabras delante de Dios y de todo el pueblo.
English: And He said to them What things; - And they said to Him The things concerning Jesus of Nazareth, who was a man a prophet mighty in deed and word before - God and all the people,
Greek: καὶ εἶπεν αὐτοῖς Ποῖα;οἱ δὲ εἶπαν αὐτῷ Τὰ περὶ Ἰησοῦ τοῦ Ναζαρηνοῦ,ὃς ἐγένετο ἀνὴρ προφήτης δυνατὸς ἐν ἔργῳ καὶ λόγῳ ἐναντίον τοῦ Θεοῦ καὶ παντὸς τοῦ λαοῦ,

Here is a phonological, semantic, orthographic alignment of that sentence:
```
[
    {{
        "Spanish phrase": "—preguntó.",
        "English phrase": "And He said to them",
        "Greek phrase": "καὶ εἶπεν αὐτοῖς"
    }},
    {{
        "Spanish phrase": "¿Qué es lo que ha pasado?",
        "English phrase": "What things;",
        "Greek phrase": "Ποῖα;"
    }},
    {{
        "Spanish phrase": "Ellos respondieron",
        "English phrase": "And they said to Him",
        "Greek phrase": "οἱ δὲ εἶπαν αὐτοῖς"
    }},
    {{
        "Spanish phrase": "—Lo de Jesús de Nazaret.",
        "English phrase": "The things concerning Jesus of Nazareth,",
        "Greek phrase": "Τὰ περὶ Ἰησοῦ τοῦ Ναζαρηνοῦ"
    }},
    {{
        "Spanish phrase": "Era un profeta poderoso", 
        "English phrase": "who was a man a prophet mighty", 
        "Greek phrase": "ὃς ἐγένετο ἀνὴρ προφήτης δυνατὸς"
    }},
        "Spanish phrase": "en obras y en palabras",
        "English phrase": "in deed and word",
        "Greek phrase": "ἐν ἔργῳ καὶ λόγῳ"
    {{
        "Spanish phrase": "delante de Dios y de todo el pueblo.",
        "English phrase": "before - God and all the people",
        "Greek phrase": "ἐναντίον τοῦ Θεοῦ καὶ παντὸς τοῦ λαοῦ"
    }}
]
```

Please also align the following sentence. Avoid including multiple phrases in a single alignment unit. You may need to break phrases  on commas or other major punctuation, including enclosing quotation marks. But you may also need to break a phrase along conjunctions or other words that typically mark the start of a new phrase:

Spanish Phrase: {target}
English Phrase: {bsb}
Greek Phrase: {macula}
'''
    except Exception as e:
        print('Error on Greek alignment prompt generation.', e)
        return 'ERROR'

def generate_broad_hebrew_alignment_prompt(verse):
    bsb, macula, target = verse['bsb']['content'], verse['macula']['content'], verse['target']['content']
    try:
        return f'''Here are some general facts to note about Spanish:
Spanish is a fusional language, ensure correct affix attachment; follow SVO order; mark verbs for tense, aspect, mood.
For translating from Hebrew: shift to SVO order; adapt Hebrew Voice/Aspect/Mood markings to Spanish system.

Translation style:
The Spanish translation is  a literal translation trying to stick closely to the Hebrew word order, but there may occasionally be instances where Spanish phrases differ to produce a more natural translation.

Here is a sentence:
Spanish: Pero la tierra estaba desolada y vacía, y había oscuridad sobre la superficie del abismo. El Espíritu de ʼElohim se movía sobre la superficie de las aguas.
English: Now the earth was formless and void, and darkness was over the surface of the deep. And the Spirit of God was hovering over the surface of the waters.
Hebrew: וְהָאָ֗רֶץ הָיְתָ֥ה תֹ֨הוּ֙ וָבֹ֔הוּ וְחֹ֖שֶׁךְ עַל־פְּנֵ֣י תְה֑וֹם וְר֣וּחַ אֱלֹהִ֔ים מְרַחֶ֖פֶת עַל־פְּנֵ֥י הַמָּֽיִם׃

Here is a phonological, semantic, orthographic alignment of that sentence:
```
[
    {{
        "Spanish phrase": "Pero la tierra",
        "English phrase": "Now the earth",
        "Hebrew phrase": "וְהָאָ֗רֶץ",
    }},
    {{
        "Spanish phrase": "estaba desolada",
        "English phrase": "was formless",
        "Hebrew phrase": "הָיְתָ֥ה תֹ֨הוּ֙",
    }},
    {{
        "Spanish phrase": "y vacía,",
        "English phrase": "and void,",
        "Hebrew phrase": "וָבֹ֔הוּ"
    }},
    {{
        "Spanish phrase": "y había oscuridad",
        "English phrase": "and darkness",
        "Hebrew phrase": "וְחֹ֖שֶׁךְ",
    }},
    {{
        "Spanish phrase": "sobre la superficie",
        "English phrase": "was over the surface",
        "Hebrew phrase": "עַל־פְּנֵ֣י",
    }},
    {{
        "Spanish phrase": "del abismo.",
        "English phrase": "of the deep.",
        "Hebrew phrase": "תְה֑וֹם"
    }},
    {{
        "Spanish phrase": "El Espíritu de ʼElohim",
        "English phrase": "And the Spirit of God",
        "Hebrew phrase": "וְר֣וּחַ אֱלֹהִ֔ים",
    }},
    {{
        "Spanish phrase": "se movía",
        "English phrase": "was hovering",
        "Hebrew phrase": "מְרַחֶ֖פֶת",
    }},
    {{
        "Spanish phrase": "sobre la superficie de las aguas.",
        "English phrase": "over the surface of the waters.",
        "Hebrew phrase": "עַל־פְּנֵ֥י הַמָּֽיִם׃"
    }}
]
```

Please also align the following sentence. Avoid including multiple phrases in a single alignment unit. You may need to break phrases  on commas or other major punctuation, including enclosing quotation marks. But you may also need to break a phrase along conjunctions or other words that typically mark the start of a new phrase:

Spanish: {target}
English: {bsb}
Hebrew: {macula}
'''
    except Exception as e:
        # print('Error on Hebrew alignment prompt generation.', e)
        return 'ERROR'
    
book_idx = {'GEN': 1, 'EXO': 2, 'LEV': 3, 'NUM': 4, 'DEU': 5, 'JOS': 6, 'JDG': 7, 'RUT': 8, '1SA': 9, '2SA': 10,
 '1KI': 11, '2KI': 12, '1CH': 13, '2CH': 14, 'EZR': 15, 'NEH': 16, 'EST': 17, 'JOB': 18, 'PSA': 19, 'PRO': 20,
 'ECC': 21, 'SNG': 22, 'ISA': 23, 'JER': 24, 'LAM': 25, 'EZK': 26, 'DAN': 27, 'HOS': 28, 'JOL': 29, 'AMO': 30,
 'OBA': 31, 'JON': 32, 'MIC': 33, 'NAH': 34, 'HAB': 35, 'ZEP': 36, 'HAG': 37, 'ZEC': 38, 'MAL': 39, 'MAT': 40,
 'MRK': 41, 'LUK': 42, 'JHN': 43, 'ACT': 44, 'ROM': 45, '1CO': 46, '2CO': 47, 'GAL': 48, 'EPH': 49, 'PHP': 50,
 'COL': 51, '1TH': 52, '2TH': 53, '1TI': 54, '2TI': 55, 'TIT': 56, 'PHM': 57, 'HEB': 58, 'JAS': 59, '1PE': 60,
 '2PE': 61, '1JN': 62, '2JN': 63, '3JN': 64, 'JUD': 65, 'REV': 66}

def generate_broad_alignment_prompt(data_element):
    reference = data_element['vref']
    # print(reference)
    # print(book_idx[reference[:3]])
    if book_idx[reference[:3]] < 40:
        return generate_broad_hebrew_alignment_prompt(data_element)
    else:
        return generate_broad_greek_alignment_prompt(data_element)

def get_alignments_from_prompt_output(generated_texts):
  if generated_texts.rfind('```') != generated_texts.find('```'):
    start_index = generated_texts.find('```')
    end_index = generated_texts.rfind('```')
    json_data = generated_texts[start_index + 3:end_index]
  else:
    start_index = generated_texts.find('```')
    json_data = generated_texts[start_index + 3:]
  json_data = json_data.strip()
  # print(json_data)
  
  try:
    data = json.loads(json_data)
  except json.JSONDecodeError:
    # print("\rInvalid JSON data in the generated_texts string.", end='')
    return None
  return data

def align(prompt):
    
    formatted_prompt = ("You are LangAlignerGPT. Analyze the user-supplied alignment examples below and follow any instructions the user gives.\n"
                        f'{prompt}')

    max_retries = MAX_RETRIES
    for i in range(max_retries):
        try:
            response = openai.Completion.create(
              model=selected_model,
              prompt=formatted_prompt,
              temperature=0,
              api_key = os.environ['OPENAI_API_KEY'],
            )
            return response['choices'][0]['text']
        except (openai.error.APIConnectionError, openai.error.APIError) as e:
            if i < max_retries - 1:  # i is zero indexed
                continue
            else:
                return {"error": str(e)}


### LOAD DATA ###
    
with open(data, 'r') as f:
    json_data = json.loads(f.read())

json_data_sample = random.sample(json_data, args.n)

### ALIGN ###

for sample in json_data_sample:
    response = openai.Completion.create(
              model=selected_model,
              prompt=generate_broad_alignment_prompt(sample),
              temperature=0.3,
              api_key = os.environ['OPENAI_API_KEY'],
              max_tokens=1000
            )

    print(sample, response['choices'][0]['text'])