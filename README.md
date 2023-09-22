This application aims to provide a translation service for Bible verses. It uses a few-shot learning approach to generate translations based on a few examples. The application is designed to work with different languages, identified by their ISO 639-3 codes.

## Architecture

The application has several components:

1. Backend (`backend.py`): This part of the application handles data processing tasks such as fetching and preparing data, creating and querying databases, and building translation prompts. It also includes functions for evaluating the quality of translations.

2. API (`index.py`): This is the interface of the application. It provides endpoints for fetching verses, getting unique tokens for a language, populating the database, querying the database, and building translation prompts.

3. Frontend (various `page.tsx` routes and components such as `FewShotPrompt.tsx`): These files handle the user interface of the application. They display the translation prompts and the generated translations, and allow users to interact with the application.

The application fetches data from different sources and loads them into dataframes, including the Berean Standard Bible (`bsb_bible_df`), the Macula Greek/Hebrew Bible (`macula_df`), and a target language Bible (`target_vref_df`). It uses this data to generate translation prompts, which are then passed to a language model for translation. The application also includes functionality for evaluating the quality of the generated translations.

## Usage notes

Generate triplets for a given ebible target language: `http://localhost:3000/api/bible?language_code=tpi&file_suffix=OTNT&force=True`

Split the triplet file into chunks: `python3.10 notebooks/split_json_data.py --data_path=./data/bible/tpiOTNT.json --chunk_size=5000`

Pass in one of the chunks directly (run this in several terminals as needed, with a different chunk each time): `python3.10 notebooks/run_align.py --run_name=tpiOTNT-gpt35i --data_path='/Users/ryderwishart/translators-copilot/data/bible/tpiOTNT.json_1.json' --n=1`