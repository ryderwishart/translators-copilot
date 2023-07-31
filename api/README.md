# Python backend notes

## Setup

I have split the MACULA Hebrew CSV into three files, because it's huge, using this shell script:

```zsh
awk -v lines=$(wc -l < mh.csv | bc) -v parts=3 'NR == 1 {header = $0; next} {print > sprintf("part_" NR%parts ".csv")} END {for(i=0;i<parts;i++) system("cat <(echo \"" header "\") part_" i ".csv > final_part_" i ".csv")}' mh.csv
```

## Main simulation loop

The main simulation loop comprises multiple agents accomplishing complementary tasks in an iterative loop.

The goal of the loop is to iteratively refine not only the translation, but to do this by improving the prompt used to generate that translation.

### Simplest implementation

Translation agent has a file of source sentences - chunked by Greek and Hebrew syntax - and translates one chunk at a time (one chunk is stored per line in the `source_data_syntax_aware.txt` file).

Evaluation agent - "here's some working notes from a translator, including the data consulted and draft translation at the bottom. Please evaluate how well the draft represents the translation. These tokens {tokens} are unique to the draft, and do not occur elsewhere in the prompt, which suggests they are made up."

Translation agent tries to create a new prompt that will generate a similar translation, but without the made-up tokens.

## Backend

User supplies a [vref-format](https://github.com/BibleNLP/ebible/blob/main/README.md#data-format) data file (.txt or .tsv), with one verse per line, and the format `book chapter:verse\tVerse content in target language`. The backend builds a set of triplets by combining each supplied verse with the matching content from the Macula Greek and Hebrew datasets, with literalistic English glosses.

Optionally, split the triplets into train and test sets for non-native-speaker validation.

The backend then builds several vectorstores using the train data (which may be all the triplets or only the training subset). Each member of the triplet data (e.g., the English glosses, the Source text, and the Target text) comprises the vectorized content in its respective vectorstore, so that similar sentences can be retrieved for any member. These vectorstores are used to generate prompts for the translation agent.

```ad-note
NOTE: It would probably make sense to have appropriate embedding functions for each member, particularly the Greek (see paper by Kevin Krahn). Everything else can be embedded using something more generic.
```

The backend then generates a prompt for each verse, and the loop begins.

## Language Models

It probably makes sense to have two types of inference models available:

- Proprietary (OpenAI, Anthropic, etc.)
- Local (huggingface models served up using the [Text Generation Inference tool](https://huggingface.github.io/text-generation-inference/), to serve up a local endpoint; see [guide](https://vilsonrodrigues.medium.com/serving-falcon-models-with-text-generation-inference-tgi-5f32005c663b))

## Agent overview

### Forward translation agent

Translates the source text into the target language.

Has access to:

- the current source sentence in proper syntax chunks
- *n* most relevant completed translation pairs
- *n* lexical entries relevant to source sentence
- previous evaluations for the source sentence
- *n* more relevant evaluations to source sentence

Outputs:

- a translation draft
- the prompt used to generate the translation draft (including all of its example data)

### Evaluation agent

Evaluates translation drafts and provides feedback to the translation agent.

Has access to:

- the most recent translation draft
- the prompt used to generate the translation draft (including all of its example data)

Outputs:

- a critique of the translation draft that makes specific reference to the prompt and example data
- suggestions for improving the translation draft

#### Simplest evaluation option

Evaluate drafts of the test set using token validation and, perhaps, a combination of BLEU score and cosine similarity.

#### More complex evaluation option

The evaluation agent generates *n* questions about the current translation and back-translation drafts, and sends them to the evaluation API endpoint. On the basis of the responses, the evaluation agent offers a critique of the draft and suggests improvements.

### Backward translation agent

(leave out for now, but see local notes for implementation details)

## Currently developing

### Backend checklist

- [ ] `backend.py` - main backend script
- [ ] `build_vectorstore.py` - builds vectorstores from vref data
- [ ] `build_prompt.py` - builds prompts for each vref

### Frontend checklist


## Currently Developing

### Backend

Implemented via a python FastAPI backend for /api/ routes on a Next.js fullstack app. Example:

```api/index.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/python")
def hello_world():
    return {"message": "Hello World"}
```

- `file_upload.py`: Handles the user's upload of a TSV file in vref format.
  - `FileUpload` class: Manages the file upload process and validates the file format.
- `chroma_database_builder.py`: Constructs the chroma databases from the uploaded file.
  - `ChromaDatabaseBuilder` class: Creates and manages the chroma databases.
- `loop_initializer.py`: Initiates the main simulation loop.
  - `LoopInitializer` class: Sets up and starts the main simulation loop.

### Frontend

The frontend is implemented via Next.js. Example:

```app/layout.tsx
import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Create Next App',
  description: 'Generated by create next app',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
```

- `upload_interface.js`: Provides the user interface for file uploading.
  - `UploadInterface` class: Manages the user interface elements and interactions for file upload.
- `progress_display.js`: Displays the progress of the chroma database building and loop initiation.
  - `ProgressDisplay` class: Manages the display of progress updates to the user.

The primary goal is to develop a functioning prototype where the user can upload a TSV file in the vref format, the chroma databases are built, and the main simulation loop begins.
