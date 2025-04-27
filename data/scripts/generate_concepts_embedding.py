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
    ontologies_data = json.load(open(args.concepts_file, 'r'))
    N = len(ontologies_data)
    
    client = OpenAI(api_key=args.openai_api_key)
    
    concept_definitions = []
    for step, concept in enumerate(ontologies_data):
        text = f"{concept}. Definition: {ontologies_data[concept]['Definition']}"
        concept_definitions.append(text)
        
    embeddings = get_embeddings(concept_definitions, client)
        
    with open(args.out_embedding_file, 'wb') as f:
        pickle.dump(embeddings, f)
    
    


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--concepts_file', default='quran_data/ontology.json')
    parser.add_argument('--out_embedding_file', default='quran_data/ontology_embedding.pkl')
    parser.add_argument('--openai_api_key', default='')
    parser.add_argument('--n_context', default=2)
    args = parser.parse_args()
    main(args)
