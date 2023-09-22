import json
import argparse
import os

def split_json_file(file_path, chunk_size):
    total_chunks = 0
    with open(file_path, 'r') as f:
        data = json.load(f)

    i = 0
    while i < len(data):
        chunk = []
        while len(chunk) < chunk_size and i < len(data):
            chunk.append(data[i])
            if data[i]['target']['content'] == '<range>':
                chunk_size += 1
            i += 1
        total_chunks += 1
        with open(f'{file_path}_{total_chunks}.json', 'w') as f:
            json.dump(chunk, f, ensure_ascii=False) # FIXME: there could still be an off-by-one issue if chunk 1 of a file is a <range> indicator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to split JSON data.')
    parser.add_argument('--data_path', type=str, default='data.json', help='Path to the data file')
    parser.add_argument('--chunk_size', type=int, default=1000, help='Size of each chunk')
    args = parser.parse_args()

    if not os.path.exists(args.data_path):
        print("Data file not found.")
    else:
        split_json_file(args.data_path, args.chunk_size)
