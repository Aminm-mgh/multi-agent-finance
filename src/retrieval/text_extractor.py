import re

class TextExtractor:
    def extract_narrative(self, raw_text: str) -> str:
        # Remove all XML/HTML tags
        text = re.sub(r'<[^>]+>', ' ', raw_text)
        
        # Remove lines with XBRL/technical patterns
        lines = text.split()
        
        # Rebuild into sentences by joining words
        # Filter out tokens that are clearly not narrative
        clean_words = []
        for word in lines:
            # Skip XBRL namespaces and URLs
            if 'http' in word or 'xbrl' in word.lower() or 'fasb.org' in word:
                continue
            # Skip pure numbers longer than 10 digits
            if re.match(r'^\d{10,}$', word):
                continue
            clean_words.append(word)
        
        # Join into text and split into chunks by period
        full_text = ' '.join(clean_words)
        return full_text