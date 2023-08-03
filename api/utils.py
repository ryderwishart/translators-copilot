import logging

logger = logging.getLogger('uvicorn')

from sentence_transformers import SentenceTransformer

name="paraphrase-albert-small-v2"
model = SentenceTransformer(name)

# used for both training and querying
def embed_batch(batch):
    logger.info(f'Embedding batch of size {len(batch)}')
    try:
        return [model.encode(sentence) for sentence in batch]
    except Exception as e:
        print('Error:', e)
        return []


# Long book names to USFM (3 uppercase letters) format
book_name_mapping = {
    "Genesis": "GEN",
    "Exodus": "EXO",
    "Leviticus": "LEV",
    "Numbers": "NUM",
    "Deuteronomy": "DEU",
    "Joshua": "JOS",
    "Judges": "JDG",
    "Ruth": "RUT",
    "1 Samuel": "1SA",
    "2 Samuel": "2SA",
    "1 Kings": "1KI",
    "2 Kings": "2KI",
    "1 Chronicles": "1CH",
    "2 Chronicles": "2CH",
    "Ezra": "EZR",
    "Nehemiah": "NEH",
    "Esther": "EST",
    "Job": "JOB",
    "Psalms": "PSA",
    "Psalm": "PSA",
    "Proverbs": "PRO",
    "Ecclesiastes": "ECC",
    "Song of Solomon": "SNG",
    "Isaiah": "ISA",
    "Jeremiah": "JER",
    "Lamentations": "LAM",
    "Ezekiel": "EZK",
    "Daniel": "DAN",
    "Hosea": "HOS",
    "Joel": "JOL",
    "Amos": "AMO",
    "Obadiah": "OBA",
    "Jonah": "JON",
    "Micah": "MIC",
    "Nahum": "NAM",
    "Habakkuk": "HAB",
    "Zephaniah": "ZEP",
    "Haggai": "HAG",
    "Zechariah": "ZEC",
    "Malachi": "MAL",
    "Matthew": "MAT",
    "Mark": "MRK",
    "Luke": "LUK",
    "John": "JHN",
    "Acts": "ACT",
    "Romans": "ROM",
    "1 Corinthians": "1CO",
    "2 Corinthians": "2CO",
    "Galatians": "GAL",
    "Ephesians": "EPH",
    "Philippians": "PHP",
    "Colossians": "COL",
    "1 Thessalonians": "1TH",
    "2 Thessalonians": "2TH",
    "1 Timothy": "1TI",
    "2 Timothy": "2TI",
    "Titus": "TIT",
    "Philemon": "PHM",
    "Hebrews": "HEB",
    "James": "JAS",
    "1 Peter": "1PE",
    "2 Peter": "2PE",
    "1 John": "1JN",
    "2 John": "2JN",
    "3 John": "3JN",
    "Jude": "JUD",
    "Revelation": "REV"
}

reverse_book_name_mapping = {v:k for k, v in book_name_mapping.items()}

def get_full_book_name(book_abbreviation: str):
    return reverse_book_name_mapping(book_abbreviation)

def get_book_abbreviation(full_book_name: str):
    """Get abbreviated book name from full book name"""
    # Try to match the full_book_name directly in the mapping
    if full_book_name in book_name_mapping:
        return book_name_mapping[full_book_name]
    # If not found, try removing the leading number (if present)
    else:
        split_book_name = full_book_name.split(' ')
        if split_book_name[0].isdigit():
            full_book_name_without_number = ' '.join(split_book_name[1:])
            if full_book_name_without_number in book_name_mapping:
                return book_name_mapping[full_book_name_without_number]
    # If no match is found, return None
    return None

    
def abbreviate_book_name_in_full_reference(full_reference: str):
    import re
    # Note that some full book names include an initial number + whitespace
    # So we need to find this pattern ([a-zA-Z 1-9]+) (\d+):(\d+)
    try:
        book, ch, v = re.findall(r'([a-zA-Z 1-9]+) (\d+):(\d+)', full_reference)[0]
        book_abbreviation = get_book_abbreviation(book)
        return f'{book_abbreviation} {ch}:{v}'
    except:
        return full_reference
    
    
def get_train_test_split_from_verse_list(verse_refs: list):
    """Split Bible verse references into train and test sets"""
    from sklearn.model_selection import train_test_split
    train_list, test_list = train_test_split(verse_refs, test_size=0.2)
    return train_list, test_list