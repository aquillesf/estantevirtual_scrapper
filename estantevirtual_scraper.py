import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
from datetime import datetime


BASE_URL = "https://www.estantevirtual.com.br/garimpepor/sebos-e-livreiros"

#browser real para evitar bot detection e redirecionamento para pages vazias
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def extract_initial_state(html: str) -> dict | None:

    soup = BeautifulSoup(html, "html.parser")

    #percorre o script do inline
    for script in soup.find_all("script", src=False):

        content = script.string or ""
        if "__INITIAL_STATE__" not in content:
            continue

        match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*\})", content, re.DOTALL)

        if match:

            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None

    return None


def fetch_page(page: int) -> dict | None:

    params = {"page": page} if page > 1 else {}

    try:
        response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        return extract_initial_state(response.text)
    
    except requests.RequestException as e:
        print(f"Erro na requisicao da pagina {page}: {e}")
        return None


def parse_sellers(state: dict) -> list[dict]:
    sellers_raw = state.get("SellersList", {}).get("sellers", [])
    result = []
    for s in sellers_raw:
        addr = s.get("address", {})
        review = s.get("reviewHeading", {})
        #puxa os sebos pelo id e pelo nome
        result.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "link": f"https://www.estantevirtual.com.br/sebos-e-livreiros/{s.get('normalizedName')}?sellerId={s.get('id')}",
            "location": {
                "city": addr.get("city", ""),
                "state": addr.get("state", ""),
            },
            "freeShipping": s.get("freeShipping", False),
            "memberSince": s.get("memberSince", ""),
            "rating": {
                "average": review.get("average", 0),
                "percentRecommended": review.get("percentRecommended", 0),
            },
        })
    return result


#criação da pasta files e salvamento do json
def save_json(filename: str, data: list):

    folder = "files"
    os.makedirs(folder, exist_ok=True)
    path = f"{folder}/{filename}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Salvo em {path}")


#iteração das pages e salvamento dos dados em um .json
def main(max_pages: int = None):
    state = fetch_page(1)
    if not state:
        return 0

    sellers_meta = state.get("SellersList", {})
    total_pages = sellers_meta.get("totalPages", 1)
    total_elements = sellers_meta.get("totalElements", 0)

    pages_to_scrape = min(total_pages, max_pages) if max_pages else total_pages
    print(f"Paginas disponiveis: {total_pages} | Coletando: {pages_to_scrape}\n")
    all_sellers = parse_sellers(state)

    for page in range(2, pages_to_scrape + 1):
        #pausa entre req
        time.sleep(1.5)

        print(f"Pagina {page}/{pages_to_scrape}...", end=" ", flush=True)
        state = fetch_page(page)

        if not state:
            continue

        sellers = parse_sellers(state)
        all_sellers.extend(sellers)
        print(f"{len(sellers)} novos (total: {len(all_sellers)})")

    #organização legal de arquivo por data
    today = datetime.today()

    filename = f"EV_{today.strftime('%d')}_{today.strftime('%b').upper()}_{today.strftime('%Y')}"
    save_json(filename, all_sellers)

    print(f"\nConcluido. {len(all_sellers)} sebos salvos.")


if __name__ == "__main__":
    #aqui é o seletor do max de pages que vc quer escolher
    main(max_pages=5)