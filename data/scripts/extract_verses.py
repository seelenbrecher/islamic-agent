import argparse
import json
import markdown

from bs4 import BeautifulSoup

def read_markdown_file(filepath):
    """
    Reads a Markdown file and returns the HTML rendered content.

    Args:
        filepath (str): The path to the Markdown file.

    Returns:
        str: The HTML content, or None on error.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            markdown_content = file.read()  # Read the entire file content
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)
        return html_content
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"An error occurred while reading or processing the file: {e}")
        return None
    
    
def get_headings_and_paragraph(html_content):
    """
    Parses the HTML content and extracts all Heading 1 tags and the first paragraph.

    Args:
        html_content (str): The HTML content to parse.

    Returns:
        tuple: A tuple containing a list of Heading 1 text contents and the first paragraph text,
               or ([], None) on error or if no matching elements are found.
    """
    paragraphs = []

    try:
        soup = BeautifulSoup(html_content, 'html.parser')  # Use BeautifulSoup to parse HTML

        # Find the first <p> tag
        p_tags = soup.find_all('p')
        for p_tag in p_tags:
            paragraphs.append(p_tag.text.strip())

        return paragraphs

    except Exception as e:
        print(f"An error occurred while parsing the HTML: {e}")
        return []


def main(args):
    surahs_info = json.load(open(args.surah_info_data, 'r'))
    surahs_translation = json.load(open(args.surah_translation_data, 'r'))
    
    verses_md = read_markdown_file(args.verses_data)
    verses = get_headings_and_paragraph(verses_md)
    
    num_surah = 114
    data = []
    for i in range(1, 115):
        surah_num = str(i)
        surah_info = surahs_info[surah_num]
        surah_translation = surahs_translation[surah_num]
        
        surah_verses = verses[surah_info['start']-1:surah_info['end']]
        
        for verse_id, verse in enumerate(surah_verses):
            data.append({
                'surah_id': i,
                'surah_n_ayah': surah_info['nAyah'],
                'surah_info_revelation_order': surah_info['revelationOrder'],
                'surah_name': surah_translation['name'],
                'surah_name_en': surah_translation['translation'],
                'verse_id': verse_id+1,
                'verse': verse,
            })
    
    with open(f'{args.output_data}', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verses_data', default='raw_data/en-ahmedali-tanzil.md')
    parser.add_argument('--surah_info_data', default='raw_data/surah.json')
    parser.add_argument('--surah_translation_data', default='raw_data/en-qurancom.json')
    parser.add_argument('--output_data', default='quran_data/verses.json')
    args = parser.parse_args()
    main(args)