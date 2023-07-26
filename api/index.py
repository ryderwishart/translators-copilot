from fastapi import FastAPI

app = FastAPI()


bsb_bible_df, macula_df = get_dataframes() # Store these in global state

@app.get("/api/python")
def read_root():
    return {"Hello": "World"}

# get bsb verse by ref
@app.get("/api/bsb_verses/{full_verse_ref}")
def read_item(full_verse_ref: str):
    """
    Get verse from bsb_bible_df (Berean Standard Bible)
    e.g., http://localhost:3000/api/bsb_verses/GEN%202:19
    """
    print('debug: ', bsb_bible_df.head())
    verse = bsb_bible_df[bsb_bible_df['vref'] == full_verse_ref]
    entry_number_of_verse = verse.index[0]
    verse_output = {
        'verse_number': int(entry_number_of_verse),
        'vref': verse['vref'][entry_number_of_verse],
        'content': verse['content'][entry_number_of_verse]
    }
    return verse_output

# get macula verse by ref
@app.get("/api/macula_verses/{full_verse_ref}")
def read_macula_verse_item(full_verse_ref: str):
    """
    Get verse from macula_greek_df and macula_hebrew_df
    e.g., http://localhost:3000/api/macula_verses/GEN%202:19
    or NT: http://localhost:3000/api/macula_verses/ROM%202:19
    """
    print('full_verse_ref', full_verse_ref)
    verse = macula_df[macula_df['vref'] == full_verse_ref]
    entry_number_of_verse = verse.index[0]
    verse_output = {
        'verse_number': int(entry_number_of_verse),
        'vref': verse['vref'][entry_number_of_verse],
        'content': verse['content'][entry_number_of_verse]
    }
    return verse_output

# get target language data by language code
@app.get("/api/target_vref_data/{language_code}")
def read_target_language_item(language_code: str, drop_empty_verses: bool = False):
    """
    Get target language data by language code
    e.g., http://localhost:3000/api/target_vref_data/aai
    """
    target_vref_data = get_target_vref_df(language_code, drop_empty_verses=drop_empty_verses)
    return target_vref_data

# get a single verse with source text and gloss, bsb english, and target language
@app.get("/api/verse/{full_verse_ref}&{language_code}")
def get_verse(full_verse_ref: str, language_code: str):
    """
    Get verse from bsb_bible_df, 
    AND macula_df (greek and hebrew)
    AND target_vref_data (target language)
    
    e.g., http://localhost:3000/api/verse/GEN%202:19&aai
    or NT: http://localhost:3000/api/verse/ROM%202:19&aai
    """
    bsb_row = bsb_bible_df[bsb_bible_df['vref'] == full_verse_ref]
    macula_row = macula_df[macula_df['vref'] == full_verse_ref]
    target_df = get_target_vref_df(language_code)
    target_row = target_df[target_df['vref'] == full_verse_ref]
    
    return {
        'bsb': {
            'verse_number': int(bsb_row.index[0]),
            'vref': bsb_row['vref'][bsb_row.index[0]],
            'content': bsb_row['content'][bsb_row.index[0]]
        },
        'macula': {
            'verse_number': int(macula_row.index[0]),
            'vref': macula_row['vref'][macula_row.index[0]],
            'content': macula_row['content'][macula_row.index[0]]
        },
        'target': {
            'verse_number': int(target_row.index[0]),
            'vref': target_row['vref'][target_row.index[0]],
            'content': target_row['content'][target_row.index[0]]
        }
    }

# get the entire bible with source text and gloss, bsb english, and target language
@app.get("/api/bible/{language_code}")
def get_bible(language_code: str):
    """
    Get the entire Bible from bsb_bible_df, 
    AND macula_df (greek and hebrew)
    AND target_vref_data (target language)
    
    e.g., http://localhost:3000/api/bible/aai
    """
    import json 
    
    target_vref_df = get_target_vref_df(language_code)
    
    output = []
    for i in range(len(bsb_bible_df)):
        bsb_row = bsb_bible_df.iloc[i]
        macula_row = macula_df.iloc[i]
        target_row = target_vref_df.iloc[i]
        
        output.append({
            'bsb': {
                'verse_number': int(bsb_row.name),
                'vref': bsb_row['vref'],
                'content': bsb_row['content']
            },
            'macula': {
                'vref': macula_row['vref'],
                'verse_number': int(macula_row.name),
                'content': macula_row['content']
            },
            'target': {
                'verse_number': int(target_row.name),
                'vref': target_row['vref'],
                'content': target_row['content']
            }
        })
    
    # Save output to disk as `data/triples/{language_code}.json`
    if not os.path.exists('data/triples'):
        os.mkdir('data/triples')
        
    with open(f'data/triples/{language_code}.json', 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    
    return True

