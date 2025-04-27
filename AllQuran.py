import os
import faiss
import json
import numpy as np

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from queue import Queue
from typing import Annotated, List
from typing_extensions import TypedDict

load_dotenv()
    
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_query: str
    relevant_verses: List[dict]

class AllQuran:
    def __init__(self, ):
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai", api_key=os.environ.get("OPENAI_API_KEY"))
        self.llm_embed = OpenAIEmbeddings(model="text-embedding-3-small", api_key=os.environ.get("OPENAI_API_KEY"))
        
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("call_llm", self._call_llm)
        graph_builder.add_node("evidence_retrieval", self._evidence_retrieval)
    
        graph_builder.add_edge(START, "evidence_retrieval")
        graph_builder.add_edge("evidence_retrieval", "call_llm")
        graph_builder.add_edge("call_llm", END)

        self.graph = graph_builder.compile()
        
        self.verses_index = faiss.read_index(os.environ.get("VERSES_INDEX_PATH"))
        self.verses_collections = json.load(open(os.environ.get("VERSES_COLLECTION_PATH"), 'r'))
        self.verses_collections_map = {}
        self.verses_collections_to_id = {}
        for step, verse in enumerate(self.verses_collections):
            surah_id = verse['surah_id']
            ayah_id = verse['verse_id']
            if surah_id not in self.verses_collections_map:
                self.verses_collections_map[surah_id] = {}
            self.verses_collections_map[surah_id][ayah_id] = verse
            
            if surah_id not in self.verses_collections_to_id:
                self.verses_collections_to_id[surah_id] = {}
            self.verses_collections_to_id[surah_id][ayah_id] = step
        
        self.top_k = int(os.environ.get("TOP_K"))
        
        self.concepts_index = faiss.read_index(os.environ.get("CONCEPTS_INDEX_PATH"))
        self.concepts_collections = json.load(open(os.environ.get("CONCEPTS_DATA"), 'r'))
        self.concepts_to_ids = [key for key in self.concepts_collections]
        
        
    def _call_llm(self, state: AgentState):
        prompt = f"You are given a question regarding Islam. Please answer the question thoroughly. For every answer you state, please give citation of the supporting verses, as well as where the verses can be found (name of the surah and number of ayah). I will provide some relevant verses to help you answer the question.\n\n"
        prompt += f"# Question: {state['user_query']}\n\n"
        prompt += f"# Relevant verses: \n\n"
        for verse in state['relevant_verses']:
            prompt += f"## {verse['verse_with_context']}"
        
        input_message = HumanMessage(content=prompt)
        
        response = self.llm.invoke(prompt)
        
        return {"messages": [input_message, response]}
    
    def _concept_based_rag(self, query_emb):
        scores, indexes = self.concepts_index.search(query_emb, 500)
        scores_with_index = [(float(score), self.concepts_to_ids[index]) for score, index in zip(scores[0], indexes[0]) if score <= 1.5]
        
        evidence = []
        visited_concepts = set()
        for score, concept_id in scores_with_index[:self.top_k]:
            concept = self.concepts_collections[concept_id]
            
            visited_concepts.add(concept_id)
            q = Queue()
            q.put(concept_id)
            
            while not q.empty():
                current_concept_id = q.get()
                current_concept = self.concepts_collections[current_concept_id]
                
                for verse in current_concept['Verses List']:
                    evidence.append(self.verses_collections_map[verse['surah_id']][verse['verse_id']])
                
                related_concepts = [x['id'] for x in current_concept['Subcategories']]
                related_concepts.extend([x['id'] for x in current_concept['Related Concepts']])
                
                neighbors = [x for x in scores_with_index if x[1] in related_concepts]
                
                if len(neighbors) > 0:
                    neighbors.sort(key=lambda item: item[0])
                    if neighbors[0][0] <= 1.5 and neighbors[0][1] not in visited_concepts:
                        visited_concepts.add(neighbors[0][1])
                        q.put(neighbors[0][1])
        
        return evidence
    
    def _evidence_retrieval(self, state: AgentState):
        query = state["user_query"]
        query_emb = self.llm_embed.embed_query(query)
        query_emb = np.array([query_emb])
        _, indexes = self.verses_index.search(query_emb, 10*self.top_k)
        
        top_k_evidence = [self.verses_collections[int(id)] for id in indexes[0][:self.top_k]]
        concept_based_evidence = self._concept_based_rag(query_emb)
        concept_based_evidence = [x for x in concept_based_evidence if self.verses_collections_to_id[x['surah_id']][x['verse_id']] in indexes][:self.top_k]
        
        evidence = top_k_evidence + concept_based_evidence
        
        return {
            "relevant_verses": evidence
        }
    
    def answer(self, query):
        response = self.graph.invoke({
            "messages": [],
            "user_query": query,
            "relevant_verses": [],
        })
        return response['messages'][-1].content


# def main():
#     all_quran = AllQuran()
#     print(all_quran.answer("Is destiny pre-defined or not in Islam?"))

# if __name__=='__main__':
    
#     main()