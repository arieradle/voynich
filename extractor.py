import re
import requests

def extract_voynich_data(url):
    response = requests.get(url)
    text = response.text

    # Infer folio from filename
    match_page = re.search(r'f(\d{3}[rv])', url)
    page = match_page.group(1) if match_page else "unknown"

    # Try to guess subject from folder name
    match_subject = re.search(r'voynich\.nu/([a-z0-9]+)/', url)
    subject_map = {
        "q01": "Herbal A",
        "q02": "Herbal B",
        "q03": "Biological",
        "q04": "Astrological",
        "q05": "Pharmaceutical",
        "q13": "Stars",
        "q20": "Text-only",
    }
    folder = match_subject.group(1) if match_subject else "unknown"
    subject = subject_map.get(folder, folder)

    # Parse lines with Voynichese
    voynich_lines = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Only keep Voynichese words
        parts = line.split()
        voynich_words = [word for word in parts if re.match(r"^[a-zA-Z0-9_]+$", word)]
        if voynich_words:
            voynich_lines.append(" ".join(voynich_words))

    return {
        "subject": subject,
        "page": page,
        "voynich_text": voynich_lines
    }

# Example usage
url = "https://www.voynich.nu/q02/f014v_tr.txt"
data = extract_voynich_data(url)

print(f"Subject: {data['subject']}")
print(f"Page: f{data['page']}")
print("Extracted Voynichese lines:")
for line in data['voynich_text']:
    print(line)
