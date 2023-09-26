from typing import Union, List, Optional
import pandas as pd
from fastapi import FastAPI, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import time
import os, json, urllib
import lancedb
from pydantic import BaseModel
from . import backend
from .utils import get_full_book_name, get_book_abbreviation, embed_batch
from .types import Message, RequestModel, TranslationTriplet
import requests
import logging

logger = logging.getLogger('uvicorn')

app = FastAPI()


bsb_bible_df, macula_df = backend.get_dataframes() # Store these in global state

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
    logger.info('debug: ', bsb_bible_df.head())
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
    logger.info('full_verse_ref', full_verse_ref)
    verse = macula_df[macula_df['vref'] == full_verse_ref]
    entry_number_of_verse = verse.index[0]
    verse_output = {
        'verse_number': int(entry_number_of_verse),
        'vref': verse['vref'][entry_number_of_verse],
        'content': verse['content'][entry_number_of_verse]
    }
    return verse_output

# get target language data by language code
# @app.get("/api/target_vref_data/{language_code}")
# def read_target_language_item(language_code: str, drop_empty_verses: bool = False):
#     """
#     Get target language data by language code
#     e.g., http://localhost:3000/api/target_vref_data/aai
#     """
#     target_vref_data = get_target_vref_df(language_code, drop_empty_verses=drop_empty_verses)
#     return target_vref_data

@app.get("/api/download_triplets")
async def download_triplets(target_language_code: str, file_suffix: Optional[str] = None, force: bool=False):
    print(f'target_language_code: {target_language_code}')
    filename = f"{target_language_code}_triplets.json"
    
    verse_triplets = {}
    book_list = backend.get_vref_list()
    for book in book_list:
        vref_list = backend.get_vref_list(book)
        # print(f'vref_list: {vref_list[:10]}')

        for vref in vref_list:
            verse_triplet = backend.get_verse_triplet(vref, target_language_code, bsb_bible_df, macula_df)
            # print('verse_triplet', verse_triplet)
            if verse_triplet is not None:
                verse_triplets[vref] = verse_triplet
    print(len(verse_triplets), 'verse triplets')
    json_str = json.dumps(verse_triplets)

    # Write the json_str to a file
    with open(filename, 'w') as f:
        f.write(json_str)
    


    # return FileResponse(
    #     filename,
    #     media_type="application/json",
    #     headers={
    #         "Content-Disposition": f"attachment; filename={filename}"
    #     }
    # )
    return {"status": "Download started. Check back later for results."}

# get a single verse with source text and gloss, bsb english, and target language
@app.get("/api/verse/{full_verse_ref}&{language_code}")
def get_verse(full_verse_ref: str, language_code: str):
    return backend.get_verse_triplet(full_verse_ref, language_code, bsb_bible_df, macula_df)

@app.get("/api/bible")
async def get_bible(language_code: str, file_suffix: Optional[str], force: Optional[bool], background_tasks: BackgroundTasks):
    """
    Get the entire Bible from bsb_bible_df, 
    AND macula_df (greek and hebrew)
    AND target_vref_data (target language)
    
    e.g., http://localhost:3000/api/bible/aai
    """
    
    filename = f'data/bible/{language_code}{file_suffix}.json'
    
    # If the file exists and we're not forcing a reprocess, return it
    if os.path.exists(filename) and not force:
        return FileResponse(
            filename,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={language_code}.json"
            }
        )
    
    # Otherwise, start the long-running process in the background
    background_tasks.add_task(process_bible, language_code, file_suffix)
    return {"status": "Processing started. Check back later for results."}

async def process_bible(language_code: str, file_suffix: Optional[str] = None): 
    target_vref_df = backend.get_target_vref_df(language_code, file_suffix=file_suffix)
    
    output = []
    for vref in bsb_bible_df['vref']:
        bsb_row = bsb_bible_df[bsb_bible_df['vref'] == vref]
        macula_row = macula_df[macula_df['vref'] == vref]
        target_row = target_vref_df[target_vref_df['vref'] == vref]
        
        output.append({
            'vref': vref,
            'bsb': {
                'vref': bsb_row['vref'].values[0] if not bsb_row.empty else '',
                'content': bsb_row['content'].values[0] if not bsb_row.empty else ''
            },
            'macula': {
                'vref': macula_row['vref'].values[0] if not macula_row.empty else '',
                'content': macula_row['content'].values[0] if not macula_row.empty else ''
            },
            'target': {
                'vref': target_row['vref'].values[0] if not target_row.empty else '',
                'content': target_row['content'].values[0] if not target_row.empty else ''
            }
        })
    
    # Save output to disk as `data/bible/{language_code}.json`
    if not os.path.exists('data/bible'):
        os.mkdir('data/bible')
        
    with open(f'data/bible/{language_code}{file_suffix}.json', 'w') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    
    # Return the file as a download
    return FileResponse(
        f'data/bible/{language_code}{file_suffix}.json',
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={language_code}.json"
        }
    )

# endpoint to get table info
@app.get("/api/db_info")
def get_db_info():
    output = []
    
    db = lancedb.connect("./lancedb")
    table = db.open_table('verses').to_pandas()
    
    # Get unique languages in the table
    languages = table['language'].unique()
    
    output.append({
        'name': 'verses',
        'columns': list(table.columns),
        'num_rows': len(table),
        'languages': languages.tolist()
    })
    
    return output

@app.get("/api/populate_db")
def populate_db(target_language_code: str, file_suffix: str, background_tasks: BackgroundTasks):
    """
    Populate database based on language code (3-char ISO 639-3 code).
    Pulls data from bsb_bible_df, macula_df, and a target language scraped from the ebible corpus.
    """
    
    # Check if db exists
    if os.path.exists('./lancedb'):
        db = lancedb.connect("./lancedb")
        try:
            table = db.open_table('verses').to_pandas()
            if target_language_code in table['language'].unique():
                return {"status": "Language already exists in the database. Please delete the language data and try again."}
        except:
            if target_language_code.startswith('init'): # To initialize databases
                logger.info('Initializing Greek/Hebrew and English vectorstores...')
                background_tasks.add_task(backend.create_lancedb_table_from_df, bsb_bible_df, 'verses') # load_database loads up the macula and bsb tables by default if they don't exist... Probably should make this less magical in the future
                return {"status": f"Database initialization started for {target_language_code + file_suffix}... takes about 45 seconds for 10 lines of text and ~300 seconds for the whole Bible, so be patient!"}
    
    logger.info('Populating database...')
    background_tasks.add_task(backend.load_database, target_language_code, file_suffix)
    return {"status": "Database population started... takes about 45 seconds for 10 lines of text and ~300 seconds for the whole Bible, so be patient!"}


@app.get("/api/query/{language_code}/{query}&limit={limit}")
def call_query_endpoint(language_code: str, query: str, limit: str = '10'):
    return backend.query_lancedb_table(language_code, query, limit=limit)

# User should be able to submit vref + source language + target language to a /api/translation-prompt-builder/ endpoint
@app.get("/api/translation-prompt-builder")
def get_translation_prompt(vref: str, target_language_code: str, source_language_code: str='', bsb_bible_df=None, macula_df=None, number_of_examples: int = 3):
    """Get a forward-translation few-shot prompt for a given vref, source, and target language code."""
    
    # Decode URI vref
    vref = urllib.parse.unquote(vref)
    print(f'vref: {vref}')
    return backend.build_translation_prompt(vref, target_language_code, source_language_code=source_language_code, bsb_bible_df=bsb_bible_df, macula_df=macula_df, number_of_examples=number_of_examples)

@app.get("/api/vrefs/?book={book}")
def get_vrefs(book: str):
    """Get a list of vrefs from the ebible corpus."""
    return backend.get_vref_list(book)

@app.get("/api/vrefs")
def get_vrefs():
    """Get a list of vrefs from the ebible corpus."""
    return backend.get_vref_list()

@app.get("/api/unique_tokens")
def get_unique_tokens(language_code: str):
    print(f'language_code: {language_code}')
    """Get a list of unique tokens from the ebible corpus texts by language code."""
    return backend.get_unique_tokens_for_language(language_code)


'''
example post body:
{
    "language_code": "aai",
    "size": 3,
    "n": 5,
    "string_filter": [
        "Ayu",
        "Paul",
        "Jesu",
        "Keriso",
        "ana",
        "akir",
        "wairafin",
        "tur",
        "abarin",
        "isan",
        "rubinu",
        "naatu",
        "Tur",
        "Gewasin",
        "binan",
        "isan",
        "God",
        "eafu",
        "atit"
    ]
}
'''
class NgramRequest(BaseModel):
    language_code: str
    size: int = 2
    n: int = 100
    string_filter: List[str] = []

@app.post("/api/ngrams")
def get_ngrams(request: NgramRequest):
    return backend.get_ngrams(request.language_code, size=request.size, n=request.n, string_filter=request.string_filter)


class EvaluateTranslationRequest(BaseModel):
    verse_triplets: dict[str, TranslationTriplet]
    hypothesis_vref: str

@app.post("/api/evaluate")
def evaluate_translation_prompt(request: EvaluateTranslationRequest):
    verse_triplets = request.verse_triplets
    hypothesis_vref = request.hypothesis_vref

    valid_vrefs = backend.get_vref_list(hypothesis_vref.split(' ')[0])
    
    print(f'valid_vrefs: {valid_vrefs[:10]}')
    if hypothesis_vref not in valid_vrefs:
        return {"status": f"You submitted vref {hypothesis_vref}, but this vref is not in the ebible corpus. See https://raw.githubusercontent.com/BibleNLP/ebible/main/metadata/vref.txt for valid vrefs."}
    
    prediction = backend.execute_discriminator_evaluation(verse_triplets, hypothesis_vref=hypothesis_vref)
    
    return {"input_received": verse_triplets, "hypothesis_vref": hypothesis_vref, "prediction": prediction}

@app.get("/api/evaluate_test")
def evaluate_translation_prompt_test():
    verse_triplets = {"ACT 13:47":{"Greek/Hebrew Source":"οὕτως γὰρ ἐντέταλται ἡμῖν ὁ Κύριος Τέθεικά σε εἰς φῶς ἐθνῶν τοῦ εἶναί σε εἰς σωτηρίαν ἕως ἐσχάτου τῆς γῆς.","English Reference":"For this is what the Lord has commanded us: ‘I have made you a light for the Gentiles, to bring salvation to the ends of the earth.’”","Target":"Anayabin Regah ana obaiyunen tur biti iti na’atube eo, ‘Ayu kwa ayasairi Ufun Sabuw hai marakaw isan, saise kwa i boro yawas kwanab kwanatit kwanan tafaram yomanin kwanatit.’"},"ACT 3:20":{"Greek/Hebrew Source":"ὅπως ἂν ἔλθωσιν καιροὶ ἀναψύξεως ἀπὸ προσώπου τοῦ Κυρίου καὶ ἀποστείλῃ τὸν προκεχειρισμένον ὑμῖν Χριστὸν Ἰησοῦν,","English Reference":"that times of refreshing may come from the presence of the Lord, and that He may send Jesus, the Christ, who has been appointed for you.","Target":"Nati namamatar ana veya, imaibo ayub ana fair bain baiboubun isan boro Regah wanawananamaim nan biya natit. Jesu, i ana Roubinineyan orot marasika kwa isa rurubin boro niyafar."},"LAM 2:13":{"Greek/Hebrew Source":"מָ֣ה אֲדַמֶּה־ לָּ֗ךְ הַבַּת֙ יְר֣וּשָׁלִַ֔ם מָ֤ה אַשְׁוֶה־ לָּךְ֙ וַאֲנַֽחֲמֵ֔ךְ בְּתוּלַ֖ת בַּת־ צִיּ֑וֹן כִּֽי־ גָד֥וֹל כַּיָּ֛ם שִׁבְרֵ֖ךְ מִ֥י יִרְפָּא־ לָֽךְ׃ס","English Reference":"What can I say for you? To what can I compare you, O Daughter of Jerusalem? To what can I liken you, that I may console you, O Virgin Daughter of Zion? For your wound is as deep as the sea. Who can ever heal you?","Target":""},"ROM 1:8":{"Greek/Hebrew Source":"Πρῶτον μὲν εὐχαριστῶ τῷ Θεῷ μου διὰ Ἰησοῦ Χριστοῦ περὶ πάντων ὑμῶν, ὅτι ἡ πίστις ὑμῶν καταγγέλλεται ἐν ὅλῳ τῷ κόσμῳ.","English Reference":"First, I thank my God through Jesus Christ for all of you, because your faith is being proclaimed all over the world.","Target":"This is the hypothesized verse translation."}}
    verse_triplets: dict[str, TranslationTriplet] = { k: TranslationTriplet(**v) for k, v in verse_triplets.items() }
    # return {"status": "Evaluation prompted", "input_received": verse_triplets, "hypothesis_vref": None, "hypothesis_key": None}
    return backend.execute_discriminator_evaluation(verse_triplets, hypothesis_vref='ROM 1:8')
  
# @app.websocket("/api/test_feedback_loop")
# async def test_feedback_loop(websocket: WebSocket, vref: str = Query(...), target_language_code: str = Query(...), source_language_code: str = Query(None)):
#     await websocket.accept()
#     feedback_loop = backend.AILoop(
#         iterations=10,
#         function_a=lambda: backend.execute_fewshot_translation(vref, target_language_code, source_language_code),
#         function_b=backend.execute_discriminator_evaluation,
#     )
#     for result in feedback_loop:
#         await websocket.send_json(result)
#     await websocket.close()

@app.get('/api/translate')
def forward_translation_request(vref: str, target_language_code: str):
    translation = backend.Translation(vref, target_language_code=target_language_code)
    return str({'hypothesis': translation.get_hypothesis(), 'feedback': translation.get_feedback()})

import random
@app.get('/api/get_alignment')
def get_available_alignment(language_code=None, n=10):
    # return ../data/alignments/test_spanish.jsonl
    code = language_code if language_code else 'test_spanish'
    with open(f'data/alignments/{code}.jsonl', 'r') as f:
        
        # note that the data is jsonl, so we need to read it line by line
        
        data = f.readlines()
        # Check if n is greater than the length of data
        n = min(int(n), len(data))
        # Randomly sample n lines from the data
        random_indexes = random.sample(range(len(data)), n)
        data = [data[i] for i in random_indexes]
        # Map over each line and make restructure to match interface expected by frontend
        restructured_data = []
        for raw_line in data:
            line = json.loads(raw_line)
            restructured_alignments = []
            for alignment in line['alignments']:
                keys = list(alignment.keys())
                source_key = next((key for key in keys if 'Greek' in key or 'Hebrew' in key), None)
                bridge_key = next((key for key in keys if 'English' in key), None)
                target_key = next((key for key in keys if key != source_key and key != bridge_key), None)
                
                if source_key and bridge_key and target_key:
                    restructured_alignments.append({
                        'source': alignment[source_key],
                        'bridge': alignment[bridge_key],
                        'target': alignment[target_key]
                    })
            restructured_data.append({
                'vref': line['vref'],
                'alignments': restructured_alignments
            })
        return restructured_data

@app.get('/api/all_alignment_files')
def get_all_alignment_files():
    alignment_files = []
    def find_jsonl_files(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.jsonl'):
                    alignment_files.append(os.path.join(root, file))
    find_jsonl_files('data/alignments')
    return alignment_files
