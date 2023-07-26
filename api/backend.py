import os, time
import pandas as pd
from .utils import abbreviate_book_name_in_full_reference, get_train_test_split_from_verse_list, embed_batch
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


