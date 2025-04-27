import argparse
import json
import requests
import queue

from bs4 import BeautifulSoup

ROOT_URL = 'https://corpus.quran.com'
CONCEPT_SUBURL = 'concept.jsp?id='
VERSES_SUBURL = 'search.jsp?q=con%3A'


def get_verse_list(concept_id):
    try:
        output = []
        
        for page in range(1, 6):
            response = requests.get(f"{ROOT_URL}/{VERSES_SUBURL}{concept_id}&s=2&page={page}")
            response.raise_for_status()  # Raise an exception for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')
            
            table = soup.find('table', class_='taf')
            if table is None:
                continue
            
            is_processed = False
            
            for tr in table.find_all('tr'):
                verses_loc = tr.find('td').find('span').text.strip()
                if verses_loc in output:
                    is_processed = True
                    break
                output.append(verses_loc)
            
            if is_processed:
                break
        
        
        return output

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    
def extract_data(concept_id):
    print(f"Process {concept_id}")
    try:
        response = requests.get(f"{ROOT_URL}/{CONCEPT_SUBURL}{concept_id}")
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        
        target_h4_values = ["Subcategories", "Related Concepts"]
        
        output = {
            'Definition': soup.find("p", class_="first").get_text().strip(), 
            'Subcategories': [], 
            'Related Concepts': [], 
            'Verses List': []}
        
        for h4_tag in soup.find_all('h4'):
            if h4_tag.text.strip() in target_h4_values:
                h4_text = h4_tag.text.strip()
                ul_element = h4_tag.find_next().find_next()
                
                if ul_element and ul_element.name == 'ul':
                    ul_data = []
                    for li_tag in ul_element.find_all('li'):
                        a_tag = li_tag.find('a')
                        if a_tag:
                            ul_data.append({'id': a_tag.get('href').split('?id=')[1], 'name': a_tag.text.strip()})
                    output[h4_text] = ul_data
        
        
        for li_tag in soup.find_all('li'):
            a_tag = li_tag.find('a')
            if a_tag and a_tag.text.strip() == 'Verse List':
                verses_list_raw = get_verse_list(concept_id)
                verses_list = []
                for verse in verses_list_raw:
                    verse = verse.replace('(', '').replace(')', '')
                    surah_id = int(verse.split(':')[0])
                    verse_id = int(verse.split(':')[1])
                    verses_list.append({'surah_id': surah_id, 'verse_id': verse_id})
                
                output['Verses List'] = verses_list

        return output

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
def main(args):
    output = {}
    visited = set()
    
    q = queue.Queue()
    q.put(args.root_id)
    visited.add(args.root_id)
    cnt = 0
    
    while not q.empty():
        cnt += 1
        
        if cnt % 30 == 0:
            with open(f'{args.output_data}', 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=4)
        
        concept_id = q.get()
        extracted_data = extract_data(concept_id)
        
        output[concept_id] = extracted_data
        
        for concept in extracted_data['Subcategories']:
            if concept['id'] not in visited:
                visited.add(concept['id'])
                q.put(concept['id'])
        
        for concept in extracted_data['Related Concepts']:
            if concept['id'] not in visited:
                visited.add(concept['id'])
                q.put(concept['id'])
                
    with open(f'{args.output_data}', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
        

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_id', default='concept')
    parser.add_argument('--output_data', default='quran_data/ontology_1.json')
    args = parser.parse_args()
    main(args)
    