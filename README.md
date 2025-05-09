# Trustworthy Islamic Agent: A Graph-Based RAG for Islamic Content Using a Quran ontology
This is the implementation of islamic agent from: [medium](https://medium.com/@maulanaanab/trustworthy-islamic-agent-a-graph-based-rag-for-islamic-content-using-a-quran-ontology-be7e1d729315), 
an agent that utilize a graph-based RAG on quran ontology.

The agent is developed using LangGraph and serve using telegram bot.

## Data source:
Quran Ontology: https://corpus.quran.com/

Quran Translation: Data is taken from [data-quran repository](https://github.com/hablullah/data-quran) which licensed under CC BY-NC-ND 4.0 and collected by Hablullah team from various sources, e.g. Tanzil, QuranEnc, etc.


To reproduce:
## Install dependencies

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Data Preparation

Generate verses and concept embeddings:
```
cd data
python scripts/generate_concept_embeddings.py
python scripts/generate_verses_embeddings.py
```

## Run chatbot
```
python main.py
```

## Benchmarking

Benchmarking files are inside `./benchmarking`

`islam-qa-dataset` folder contains [islamic qa-dataset](https://www.kaggle.com/datasets/mamun18/islam-qa-dataset)

`output_gpt_4o` folder contains output using gpt4o-mini

`output_all_quran` folder contains output from our islamic agent

To run the benchmarking:

```
bash benchmarking/run_all_quran.sh
bash benchmarking/run_gpt_4o.sh
```
