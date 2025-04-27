import argparse
import json
import openai
import os
import tqdm

from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_answer(question):
    messages =  [{"role": "user", "content": f"You are an Ulama. Please answer the question related to Islam correctly. Question: {question}"}]
    response = client.chat.completions.create(model="gpt-4o-mini",messages=messages,n=1)
    return response.choices[0].message.content

def main(args):
    data = json.load(open(args.in_file))
    
    for x in tqdm.tqdm(data):
        question = x['question']
        x['predicted_answer'] = get_answer(question)
        
    with open(f'{args.out_file}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_file')
    parser.add_argument('--out_file')
    args = parser.parse_args()
    main(args)