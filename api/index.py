from typing import Union, List
import pandas as pd
from fastapi import FastAPI, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
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

# get a single verse with source text and gloss, bsb english, and target language
@app.get("/api/verse/{full_verse_ref}&{language_code}")
def get_verse(full_verse_ref: str, language_code: str):
    return backend.get_verse_triplet(full_verse_ref, language_code, bsb_bible_df, macula_df)

# get the entire bible with source text and gloss, bsb english, and target language
@app.get("/api/bible/{language_code}")
def get_bible(language_code: str):
    """
    Get the entire Bible from bsb_bible_df, 
    AND macula_df (greek and hebrew)
    AND target_vref_data (target language)
    
    e.g., http://localhost:3000/api/bible/aai
    """
    
    target_vref_df = backend.get_target_vref_df(language_code)
    
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

# endpoint to get table info
@app.get("/api/db_info")
def get_db_info():
    output = []
    
    db = lancedb.connect("./lancedb")
    table_names = db.table_names()
    
    for name in table_names:
        table = db.open_table(name).to_pandas()
        output.append({
            'name': name,
            'columns': list(table.columns),
            'num_rows': len(table)
        })
    
    return output

@app.get("/api/populate_db/{target_language_code}")
def populate_db(target_language_code: str, background_tasks: BackgroundTasks):
    """
    Populate database based on language code (3-char ISO 639-3 code).
    Pulls data from bsb_bible_df, macula_df, and a target language scraped from the ebible corpus.
    """
    
    # Check if db exists
    if os.path.exists('./lancedb'):
        if f'{target_language_code}.lance' in os.listdir('./lancedb'):
            return {"status": "Database already exists. Please delete the database and try again."}
    
    if target_language_code.startswith('init'): # To initialize databases
        logger.info('Initializing Greek/Hebrew and English vectorstores...')
        background_tasks.add_task(backend.create_lancedb_table_from_df, bsb_bible_df, 'bsb_bible') # load_database loads up the macula and bsb tables by default if they don't exist... Probably should make this less magical in the future
        return {"status": "Database initialization started... takes about 45 seconds for 10 lines of text and ~300 seconds for the whole Bible, so be patient!"}
    
    logger.info('Populating database...')
    background_tasks.add_task(backend.load_database, target_language_code)
    return {"status": "Database population started... takes about 45 seconds for 10 lines of text and ~300 seconds for the whole Bible, so be patient!"}

@app.get("/api/query/{language_code}/{query}&limit={limit}")
def call_query_endpoint(language_code: str, query: str, limit: str = '10'):
    return backend.query_lancedb_table(language_code, query, limit=limit)

# User should be able to submit vref + source language + target language to a /api/translation-prompt-builder/ endpoint
@app.get("/api/translation-prompt-builder")
def get_translation_prompt(vref: str, target_language_code: str, source_language_code: str=None, bsb_bible_df=None, macula_df=None):
    """Get a forward-translation few-shot prompt for a given vref, source, and target language code."""
    
    # Decode URI vref
    vref = urllib.parse.unquote(vref)
    print(f'vref: {vref}')
    return backend.build_translation_prompt(vref, target_language_code, source_language_code=source_language_code, bsb_bible_df=bsb_bible_df, macula_df=macula_df, number_of_examples=3)

@app.get("/api/vrefs/?book={book}")
def get_vrefs(book: str):
    """Get a list of vrefs from the ebible corpus."""
    return backend.get_vref_list(book)

@app.get("/api/vrefs")
def get_vrefs():
    """Get a list of vrefs from the ebible corpus."""
    return backend.get_vref_list()
