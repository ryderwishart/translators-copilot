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


