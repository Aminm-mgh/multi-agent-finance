import re

class TextExtractor:
    def extract_narrative(self, raw_text: str) -> str:
        # Remove XBRL/XML blocks
        text = re.sub(r'<[^>]+>', ' ', raw_text)
        
        # Remove lines that look like XBRL metadata
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip lines that are mostly symbols or codes
            if len(re.findall(r'[a-zA-Z\s]', line)) < len(line) * 0.5:
                continue
            
            # Skip very short lines
            if len(line) < 30:
                continue
            
            # Skip lines with XBRL patterns
            if any(pattern in line for pattern in ['xbrltype', 'nsuri', 'localname', 'auth_ref', 'gaap_', 'us-gaap']):
                continue
                
            clean_lines.append(line)
        
        return '\n'.join(clean_lines)