import os, time
import pandas as pd
from .utils import abbreviate_book_name_in_full_reference, get_train_test_split_from_verse_list, embed_batch
import logging
logger = logging.getLogger('uvicorn')

def get_dataframes(target_language_code=None):
    """Get source data dataframes (literalistic english Bible and macula Greek/Hebrew)"""
    bsb_bible_df = pd.read_csv('data/bsb-utf8.txt', sep='\t', names=['vref', 'content'], header=0)
    bsb_bible_df['vref'] = bsb_bible_df['vref'].apply(abbreviate_book_name_in_full_reference)
    macula_df = pd.read_csv('data/combined_greek_hebrew_vref.csv') # Note: csv wrangled in notebook: `create-combined-macula-df.ipynb`
    
    if target_language_code:
        target_tsv = get_target_vref_df(target_language_code)
        target_df = get_target_vref_df(target_language_code)
        return bsb_bible_df, macula_df, target_df

    else:
        return bsb_bible_df, macula_df

def get_vref_list(book_abbreviation=None):
    vref_url = 'https://raw.githubusercontent.com/BibleNLP/ebible/main/metadata/vref.txt'
    if not os.path.exists('data/vref.txt'):
        os.system(f'wget {vref_url} -O data/vref.txt')

    with open('data/vref.txt', 'r') as f:
        
        if book_abbreviation:
            return [i.strip() for i in f.readlines() if i.startswith(book_abbreviation)]
        
        else:
            return list(set([i.strip().split(' ')[0] for i in f.readlines()]))

def get_target_vref_df(language_code, drop_empty_verses=False):
    """Get target language data by language code"""
    if not len(language_code) == 3:
        return 'Invalid language code. Please use 3-letter ISO 639-3 language code.'
    
    language_code = language_code.lower().strip()
    language_code = f'{language_code}-{language_code}'
    
    target_data_url = f'https://raw.githubusercontent.com/BibleNLP/ebible/main/corpus/{language_code}.txt'
    path = f'data/{language_code}.txt'
    
    if not os.path.exists(path):
        try:
            os.system(f'wget {target_data_url} -O {path}')
        except:
            return 'No data found for language code. Please check the eBible repo for available data.'

    with open(path, 'r') as f:
        target_text = f.readlines()
        target_text = [i.strip() for i in target_text]

    vref_url = 'https://raw.githubusercontent.com/BibleNLP/ebible/main/metadata/vref.txt'
    if not os.path.exists('data/vref.txt'):
        os.system(f'wget {vref_url} -O data/vref.txt')

    with open('data/vref.txt', 'r') as f:
        target_vref = f.readlines()
        target_vref = [i.strip() for i in target_vref]

    target_tsv = [i for i in list(zip(target_vref, target_text))]
    
    if drop_empty_verses:
        target_tsv = [i for i in target_tsv if i[1] != '']
    
    target_df = pd.DataFrame(target_tsv, columns=['vref', 'content'])
    
    return target_df

from pandas import DataFrame as DataFrameClass

def create_lancedb_table_from_df(df: DataFrameClass, table_name, content_column_name='content'):
    """Turn a pandas dataframe into a LanceDB table."""
    start_time = time.time()
    logger.info('Creating LanceDB table...', color='green')
    import lancedb
    from lancedb.embeddings import with_embeddings
    
    logger.error(f'Creating LanceDB table: {table_name}, {df.head}')
    
    # rename 'content' field as 'text' as lancedb expects
    try:
        df = df.rename(columns={content_column_name: 'text'})
    except:
        assert 'text' in df.columns, 'Please rename the content column to "text" or specify the column name in the function call.'
    
    # mkdir lancedb if it doesn't exist
    if not os.path.exists('./lancedb'):
        os.mkdir('./lancedb')
    
    # Connect to LanceDB
    db = lancedb.connect("./lancedb")
    
    table = get_table_from_database(table_name)
    
    if not table:
        # If it doesn't exist, create it
        
        df_filtered = df[df['text'].str.strip() != '']
        data = with_embeddings(embed_batch, df_filtered.sample(10000)) # FIXME: I can't process the entirety of the bsb bible for some reason. Something is corrupt or malformed in the data perhaps
        # data = with_embeddings(embed_batch, df_filtered) 

        # data = with_embeddings(embed_batch, df)
        
        table = db.create_table(
            table_name,
            data=data,
            mode="create",
        )
          
    else:
        table = db.open_table(table_name)
    
    print('LanceDB table created. Time elapsed: ', time.time() - start_time, 'seconds.')
    return table  
    
def load_database(target_language_code=None):
    print('Loading dataframes...')
    if target_language_code:
        print(f'Loading target language data for {target_language_code}...')
        bsb_bible_df, macula_df, target_df = get_dataframes(target_language_code)
    else:
        print('No target language code specified. Loading English and Greek/Hebrew data only.')
        bsb_bible_df, macula_df = get_dataframes()
        target_df = None
    
    print('Creating English tables...')
    english_table_name = 'bsb_bible'
    create_lancedb_table_from_df(bsb_bible_df, english_table_name)
    
    print('Creating Greek/Hebrew tables...')
    macula_table_name = 'macula'
    create_lancedb_table_from_df(macula_df, macula_table_name)
    
    if target_df is not None:
        print('Creating target language tables...')
        create_lancedb_table_from_df(target_df, target_language_code)

    print('Database populated.')
    return True
    
def get_table_from_database(table_name):
    """
    Returns a table by name. 
    Use '/api/db_info' endpoint to see available tables.
    """
    import lancedb
    db = lancedb.connect("./lancedb")
    table_names = db.table_names()
    if table_name not in table_names:
        logger.error(f'''Table {table_name} not found. Please check the table name and try again.
                     Available tables: {table_names}''')
        return None

    table = db.open_table(table_name)
    return table

def get_verse_triplet(full_verse_ref: str, language_code: str, bsb_bible_df, macula_df):
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

def query_lancedb_table(language_code: str, query: str, limit: str='10'):
    """Get similar sentences from a LanceDB table."""
    limit = int(limit) # I don't know if this is necessary. The FastAPI endpoint might infer an int from the query param if I typed it that way
    table = get_table_from_database(language_code)
    query_vector = embed_batch([query])[0]
    if not table:
        return {'error':'table not found'}
    result = table.search(query_vector).limit(limit).to_df().to_dict()
    if not result.values():
        return []
    texts = result['text']
    scores = result['score']
    vrefs = result['vref']
    
    output = []
    for i in range(len(texts)):
        output.append({
            'text': texts[i],
            'score': scores[i],
            'vref': vrefs[i]
        })
        
    return output

def build_translation_prompt(vref, target_language_code, source_language_code=None, bsb_bible_df=None, macula_df=None, number_of_examples=3, backtranslate=False):
    """Build a prompt for translation"""
    if bsb_bible_df is None or bsb_bible_df.empty or macula_df is None or macula_df.empty: # build bsb_bible_df and macula_df only if not supplied (saves overhead)
        bsb_bible_df, macula_df, target_df = get_dataframes(target_language_code=target_language_code)
    if source_language_code:
        _, _, source_df = get_dataframes(target_language_code=source_language_code)
    else:
        source_df = bsb_bible_df
    
    # Query the LanceDB table for the most similar verses to the source text (or bsb if source_language_code is None)
    table_name = source_language_code if source_language_code else 'bsb_bible'
    query = source_df[source_df['vref']==vref]['content'].values[0]
    original_language_source = macula_df[macula_df['vref']==vref]['content'].values[0]
    print(f'Query result: {query}')
    similar_verses = query_lancedb_table(table_name, query, limit=number_of_examples)
    
    triplets = [get_verse_triplet(similar_verse['vref'], target_language_code, bsb_bible_df, macula_df) for similar_verse in similar_verses]
    
    # Initialize an empty dictionary to store the JSON objects
    json_objects = {}
    
    for triplet in triplets:
        # Create a JSON object for each triplet with top-level keys being the VREFs
        json_objects[triplet["bsb"]["vref"]] = {
            'Greek/Hebrew Source': triplet["macula"]["content"],
            'English Reference': triplet["bsb"]["content"],
            'Target': triplet["target"]["content"]
        }
    
    # Add the source verse Greek/Hebrew and English reference to the JSON objects
    json_objects[vref] = {
        'Greek/Hebrew Source': original_language_source,
        'English Reference': query,
        'Target': ''
    }
        
    return json_objects


# def build_discriminator_evaluation_prompt(