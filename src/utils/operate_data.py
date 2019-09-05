import re

def cut_sentence(sample: Dict[str, str], grade: str = None):
    article = sample["body"]
    # pattern = re.compile(r".*?[。！？\(…{2}\)][”’》）]?")
    pattern = re.compile(r"[^!?。！？…]*\?[”’》）]?|[^!?。！？…]*![”’》）]?|[^!?。！？…]*。[”’》）]?|[^!?。！？…]*！[”’》）]?|[^!?。！？…]*？[”’》）]?|[^!?。！？…]*…{1,2}[”’》）]?")
    sentences = []
    paragraphs = [paragraph for paragraph in article.split('\n') if len(paragraph) > 0]
    for paragraph in paragraphs:
        paragraph_sentences = []
        double_quote_count = 0
        single_quote_count = 0
        book_title_count = 0
        parenthesis_count = 0
        temp_sentences = re.findall(pattern, paragraph.strip())
        for sentence in temp_sentences:
            paragraph_sentences.append(sentence)
            left_double_quotes = re.findall(r'“', sentence)
            right_double_quotes = re.findall(r'”', sentence)
            left_single_quotes = re.findall(r'‘', sentence)
            right_single_quotes = re.findall(r'’', sentence)
            left_book_title = re.findall(r'《', sentence)
            right_book_title = re.findall(r'》', sentence)
            left_parenthesis = re.findall(r'\(', sentence)
            right_parenthesis = re.findall(r'\)', sentence)
            double_quote_count = double_quote_count + len(left_double_quotes) - len(right_double_quotes)
            single_quote_count = single_quote_count + len(left_single_quotes) - len(right_single_quotes)
            book_title_count = book_title_count + len(left_book_title) - len(right_book_title)
            parenthesis_count = parenthesis_count + len(left_parenthesis) - len(right_parenthesis)
            if double_quote_count == 0 and single_quote_count == 0 and book_title_count == 0 and parenthesis_count == 0:
                sentences.append(''.join(paragraph_sentences))
                paragraph_sentences = []
    sentences = [{"id": sample["id"], "title": sample["title"], "category": sample["category"], "grade": grade, "sentence": sentence, "sequence_order": i} for i, sentence in enumerate(sentences)]
    return sentences