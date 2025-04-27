import argparse
import json
import os
import sys
import tqdm

from dotenv import load_dotenv

load_dotenv()

sys.path.append('.')
from AllQuran import AllQuran
all_quran = AllQuran()

def main(args):
    data = json.load(open(args.in_file))
    
    for x in tqdm.tqdm(data):
        question = x['question']
        x['predicted_answer'] = all_quran.answer(question)
        
    with open(f'{args.out_file}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_file')
    parser.add_argument('--out_file')
    args = parser.parse_args()
    main(args)