import spacy

nlp = spacy.load("pt_core_news_sm")

def extract_keywords(question: str):
    doc = nlp(question)
    return [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
