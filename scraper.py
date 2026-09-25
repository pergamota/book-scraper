"""
Book Scraper
------------
Coleta título, preço, avaliação (em estrelas) e disponibilidade de todos os
livros do site https://books.toscrape.com, percorrendo todas as páginas de
catálogo, e salva o resultado em um arquivo CSV.

Este site foi criado especificamente para prática de web scraping, então
não há bloqueios, captcha ou termos de uso violados ao raspá-lo.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"

# O site representa a nota em estrelas como uma classe CSS por extenso
# (ex: class="star-rating Three"). Esse dicionário traduz para número.
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def get_soup(url: str) -> BeautifulSoup:
    """Faz a requisição HTTP e devolve o HTML já parseado."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # levanta erro se o status não for 200
    response.encoding = "utf-8"
    return BeautifulSoup(response.text, "lxml")


def parse_book(article) -> dict:
    """Extrai os dados de um único livro a partir do seu bloco <article>."""
    title = article.h3.a["title"]

    price_text = article.find("p", class_="price_color").text
    # o preço vem como "£51.77" -> remove o símbolo e converte para float
    price = float(price_text.replace("£", "").strip())

    rating_class = article.find("p", class_="star-rating")["class"]
    # a classe vem como ["star-rating", "Three"] -> pegamos o segundo item
    rating_word = rating_class[1]
    rating = RATING_MAP.get(rating_word, None)

    availability = article.find("p", class_="instock availability").text.strip()

    return {
        "title": title,
        "price_gbp": price,
        "rating": rating,
        "availability": availability,
    }


def scrape_all_pages() -> pd.DataFrame:
    """Percorre todas as páginas do catálogo até acabarem os livros."""
    all_books = []
    page = 1

    while True:
        url = BASE_URL.format(page)
        try:
            soup = get_soup(url)
        except requests.exceptions.HTTPError:
            break

        articles = soup.find_all("article", class_="product_pod")
        if not articles:
            # não há mais páginas -> encerra o loop
            break

        for article in articles:
            all_books.append(parse_book(article))

        print(f"Página {page} coletada ({len(articles)} livros).")
        page += 1

        # pausa curta entre requisições, boa prática de scraping educado
        time.sleep(0.5)

    return pd.DataFrame(all_books)


def main():
    df = scrape_all_pages()

    print(f"\nTotal de livros coletados: {len(df)}")
    print(df.head())

    output_path = "data/books.csv"
    df.to_csv(output_path, index=False)
    print(f"\nDados salvos em: {output_path}")


if __name__ == "__main__":
    main()