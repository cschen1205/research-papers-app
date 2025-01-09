from scholarly import scholarly, ProxyGenerator
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import os
import json
import time
import arxiv

#### [GPT Generated] Extract metadata from Google scholar profile
def scrape_scholar_profile(author_name):
    papers_metadata = []

    ## [Manual Added] Load from existing file if available
    if os.path.exists(f"meta_{author_name}.json"):
        with open(f"meta_{author_name}.json", "r") as json_file:
            return json.load(json_file)
    ## End Manual Added
    
    print(f"Fetching metadata for: {author_name}")
    author = scholarly.search_author(author_name)
    author = scholarly.fill(next(author))

    print(f"Name: {author['name']}, Affiliation: {author['affiliation']}, len(publications): {len(author['publications'])}")
    records_len = 0
    for publication in author['publications']:
        ## [Manual Added] sleep for 0.4 seconds to avoid blocking
        time.sleep(0.4)
        ## End Manual Added
        
        pub = scholarly.fill(publication)
        paper_data = {
            'title': pub.get('bib', {}).get('title', ''),
            'abstract': pub.get('bib', {}).get('abstract', ''),
            'year': pub.get('bib', {}).get('pub_year', ''),
            'citation_count': pub.get('num_citations', ''),
            'author': pub.get('bib', {}).get('author', ''),
            'url': pub.get('url', ''),
        }
        papers_metadata.append(paper_data)
        
        ## [Manual Added] Save metadata every 5 records
        records_len += 1
        if records_len % 5 == 0:
            print(f"Fetched metadata for {records_len} papers")
            with open(f"meta_{author_name}.json", "w") as json_file:
                json.dump(papers_metadata, json_file)
        ## End Manual Added
        
    print(f"Fetched metadata for all papers: {len(papers_metadata)}")
    with open(f"meta_{author_name}.json", "w") as json_file:
            json.dump(papers_metadata, json_file)
    return papers_metadata

#### [GPT Generated] Download PDF and Extract Metadata function (Not used as it is not reliable)
# Function to search for a paper on arXiv
def search_arxiv_by_title(title):
    # print(f"Searching arXiv for: {title}")
    url = f"http://export.arxiv.org/api/query?search_query=all:{title}&start=0&max_results=1"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "xml")
        entry = soup.find("entry")
        if entry:
            pdf_url = entry.find("id").text.replace("abs", "pdf")
            print(f"Found on arXiv: {pdf_url}")
            return pdf_url
    # print(f"Paper not found on arXiv: {title}")
    return None

# [GPT Generated] Download Papers
def download_pdf(url, output_dir, title):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(output_dir, f"{title}.pdf")
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(response.content)
            print(f"Downloaded: {title}")
            return file_path
        else:
            print(f"Failed to download: {url}")
            return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None

# [GPT Generated] Extract Abstract and Keywords from PDF
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None

# [GPT Generated] Extract Index Terms/Keywords and Abstract
def parse_text_for_metadata(text):
    keywords, abstract = "", ""
    # Simple keyword/abstract parsing (can be improved with NLP tools)
    if "keywords" in text.lower():
        keywords = text.split("Keywords")[1].split("\n")[0]
    if "index terms" in text.lower():
        keywords = text.split("Index Terms")[1].split("\n")[0]
    if "abstract" in text.lower():
        abstract = text.split("Abstract")[1].split("\n")[0]
    if keywords.startswith(":") or keywords.startswith("—"):
        keywords = keywords[1:].strip()
    if abstract.startswith(":") or abstract.startswith("—"):
        abstract = abstract[1:].strip()
    return keywords, abstract
#### End of Download PDF and Extract Metadata function


## [Manual Added] Extract these items that "keywords" is empty into a separate JSON file
def cut_file(file_name):
    if os.path.exists(f"{file_name}.json"):
        with open(f"{file_name}.json", "r") as json_file:
            papers_metadata = json.load(json_file)
            t = [p for p in papers_metadata if "keywords" not in p or len(p["keywords"]) == 0]
            with open(f"meta_empty.json", "w") as m_json:
                json.dump(t, m_json)
                
## [Manual Added] Update the orginal file with files from the cut_file function that has been updated by GPT 
def copy_back(from_file, to_file):
    if os.path.exists(f"{from_file}.json"):
        with open(f"{from_file}.json", "r") as json_file:
            papers_metadata = json.load(json_file)
            with open(f"{to_file}.json", "r") as to_json_file:
                to_metadata = json.load(to_json_file)
                
            for p in papers_metadata:
                for tp in to_metadata:
                    if p["title"] == tp["title"]:
                        tp["keywords"] = p["keywords"]
                        break
            with open(f"{to_file}2.json", "w") as m_json:
                json.dump(to_metadata, m_json)
                
## [Manual Added]  standardize the author names for consistency.
def replace_author_join(file_name):
    if os.path.exists(f"{file_name}.json"):
        with open(f"{file_name}.json", "r") as json_file:
            papers_metadata = json.load(json_file)
            for p in papers_metadata:
                if "author" in p:
                    p['author'] = p['author'].replace(";", ",")
                    p['author'] = p['author'].replace(" and ", ",")
                    p['author'] = p['author'].replace("YS Ong", "Yew-Soon Ong")
                    p['author'] = p['author'].replace("Yew Soon Ong", "Yew-Soon Ong")
            with open(f"{file_name}.json", "w") as m_json:
                json.dump(papers_metadata, m_json)
                
                
#### [GPT Generated] Search pdf file link from arxiv and then insert it into the metadata
## [GPT Generated] fetch pdf link from arxiv, save both the title and pdf link into a list
def fetch_arxiv_papers(query, max_results=10):
    # Search for papers
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = []
    for result in search.results():
        title = result.title
        pdf_link = result.pdf_url
        papers.append((title, pdf_link))
    
    return papers

## [GPT Generated] Load the metadata file and fetch the pdf link from arxiv
def load_papers(file_name):
    records_len = 0
    if os.path.exists(f"{file_name}.json"):
        with open(f"{file_name}.json", "r") as json_file:
            papers_metadata = json.load(json_file)
            for p in papers_metadata:
                ## [Manual Modified] If the url is empty, fetch the pdf link from arxiv, sleep for 0.2 seconds, and save the metadata every 5 records
                if "title" in p and p['url']=="" :
                    urls = fetch_arxiv_papers(p["title"], 1)
                    if len(urls) > 0:
                        p["url"] = urls[0]
                else:
                    continue
                time.sleep(0.2)
                records_len += 1
                if records_len % 5 == 0:
                    print(f"Fetched metadata for {records_len} papers")
                    with open(f"{file_name}2.json", "w") as m_json:
                        json.dump(papers_metadata, m_json)
                ## End Manual Modified
            with open(f"{file_name}2.json", "w") as m_json:
                json.dump(papers_metadata, m_json)
                
## [Manual Added] update the url in the metadata file, if the arxiv fetched paper link has the same file name with title, then keep it. Otherwise, remove it.
def update_paper_urls(file_name):
    if os.path.exists(f"{file_name}.json"):
        with open(f"{file_name}.json", "r") as json_file:
            papers_metadata = json.load(json_file)
            for p in papers_metadata:
                if "url" in p and len(p['url']) > 0:
                    if p['title'].lower() == p['url'][0].lower():
                        p['url'] = p['url'][1]
                    else:
                        print("wrong url: ", p['url'], p['title'])
                        p['url'] = ""
            with open(f"{file_name}2.json", "w") as m_json:
                json.dump(papers_metadata, m_json) 
  
                
# Main Script
if __name__ == "__main__":
    author_name = "***"  # Replace with the specific scholar's name
    # Scrape Metadata
    papers_metadata = scrape_scholar_profile(author_name)
    
    # [Manual Added] Manul run the below functions to process the categorizations and the meta data file
    # cut_file("meta")
    # copy_back("meta_updated", "meta_empty")
    # replace_author_join("meta_paper")
    # load_papers("meta_paper")
    # update_paper_urls("meta_paper")