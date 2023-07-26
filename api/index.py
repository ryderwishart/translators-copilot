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

