import argparse
import faiss
import numpy as np
import pickle


def main(args):
    embeddings = pickle.load(open(args.embedding_file, 'rb'))
    embeddings = np.array(embeddings)
    dim = embeddings.shape[-1]
    
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    faiss.write_index(index, args.out_index_file)
    


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--embedding_file', default='quran_data/ontology_embedding.pkl')
    parser.add_argument('--out_index_file', default='quran_data/verses_ontology_index.faiss')
    args = parser.parse_args()
    main(args)