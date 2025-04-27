import argparse
import copy
import json
import pickle

from openai import OpenAI


def get_embeddings(texts, client, batch_size=32):
    results = []
    for i in range(0, len(texts), batch_size):
        batch_end = min(i + batch_size, len(texts))
        batches = texts[i:batch_end]
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=batches,
            encoding_format="float"
        )
        results.extend([x.embedding for x in response.data])
       
    return results

def main(args):
    """
    Add context and embed each verses
    """
    verses_data = json.load(open(args.verses_file, 'r'))
    N = len(verses_data)
    
    surahs_info = json.load(open(args.surah_info, 'r'))
    surahs_translation = json.load(open(args.surah_translation, 'r'))
    
    client = OpenAI(api_key=args.openai_api_key)
    
    verses_with_contexts = []
    for step, verse in enumerate(verses_data):
        new_verse = copy.deepcopy(verse)
        surah_id = new_verse['surah_id']
        surah_info = surahs_info[str(surah_id)]
        surah_translation = surahs_translation[str(surah_id)]
        
        start_context = step - args.n_context
        start_context = max(min(start_context, N-1), 0)
        
        while verses_data[start_context]['surah_id'] != surah_id:
            start_context += 1
        
        end_context = step + args.n_context
        end_context = max(min(end_context, N-1), 0)
        
        while verses_data[end_context]['surah_id'] != surah_id:
            end_context -= 1
            
        text = [x['verse'] for x in verses_data[start_context:end_context+1]]
        text = ' '.join(text)
        
        verse_with_context_text = f"""
This verse is taken from surah {surah_id} - {surah_translation['name']}, which mean {surah_translation['translation']}.
This surah is has {surah_info['nAyah']} ayah, from {surah_info['start']} until {surah_info['end']}.
This surah was revealed in the {surah_info['type']} order, in {surah_info['revelationOrder']}.
The quran verse surah {surah_translation['name']} ayah {verses_data[start_context]['verse_id']} to {verses_data[end_context]['verse_id']} said that = {text}""".strip()
        
        
        new_verse['verse_with_context'] = verse_with_context_text
        
        verses_with_contexts.append(new_verse)
        
    embeddings = get_embeddings([x['verse_with_context'] for x in verses_with_contexts], client)
    
    with open(f'{args.out_verses_file}', 'w', encoding='utf-8') as f:
        json.dump(verses_with_contexts, f, ensure_ascii=False, indent=4)
        
    with open(args.out_embedding_file, 'wb') as f:
        pickle.dump(embeddings, f)
    
    


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verses_file', default='quran_data/verses.json')
    parser.add_argument('--surah_info', default='raw_data/surah.json')
    parser.add_argument('--surah_translation', default='raw_data/en-qurancom.json')
    parser.add_argument('--out_verses_file', default='quran_data/verses_with_context.json')
    parser.add_argument('--out_embedding_file', default='quran_data/verses_embedding.pkl')
    parser.add_argument('--openai_api_key', default='')
    parser.add_argument('--n_context', default=2)
    args = parser.parse_args()
    main(args)
