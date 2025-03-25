import re
import requests
import httpx
import asyncio


def extract_voynich_data(text, url):
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

        if line.startswith('<f'):
            parts = line.split('>')
            prefix = parts[0] + '>'
            text = parts[1]
            words = text.split('.')
            cleaned_words = []
            for word in words:
                cleaned_word = re.sub(r'[{!=-]+$', '', word)  # Remove trailing hyphens, !, =
                cleaned_word = re.sub(r'\{.*?\}', '', cleaned_word) #remove anything between curly braces including the braces
                cleaned_word = re.sub(r'-', '', cleaned_word) #remove any hyphens inside the words
                cleaned_words.append(cleaned_word)

            transformed_text = ' '.join(cleaned_words) + '.'
            voynich_lines.append(prefix + transformed_text)
        else:
            voynich_lines.append(line)

    return {
        "subject": subject,
        "page": page,
        "voynich_text": voynich_lines
    }


async def fetch_text_async(url: str) -> str:
    """Retrieves a text file from a URL asynchronously."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.text
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}.")
            return None
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            return None
        except Exception as generic:
            print(f"A generic error occured: {generic}")
            return None

async def main():
    url = "https://www.voynich.nu/q02/f014v_tr.txt"
    
    text_content = await fetch_text_async(url)
    data = extract_voynich_data(text_content, url)

    for line in data['voynich_text']:
        print(line)

if __name__ == "__main__":
    asyncio.run(main())
