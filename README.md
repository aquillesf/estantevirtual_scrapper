Scraper de sebos e livreiros da Estante Virtual

Este script faz scraping da pagina de sebos e livreiros do site Estante Virtual
(https://www.estantevirtual.com.br/garimpepor/sebos-e-livreiros) e salva os dados
coletados em um arquivo JSON dentro da pasta "files".

O script extrai os dados diretamente do estado interno da pagina (window.__INITIAL_STATE__),
evitando a necessidade de parsear HTML complexo.

============================================================================
NECESSARIO TER PARA EXECUTAR O CODIGO
============================================================================

Python 3.x
pip
requests
beautifulsoup4
os

Para instalar as dependencias:

    pip install requests beautifulsoup4

============================================================================
COMO USAR
============================================================================

Execute o script diretamente pelo terminal, dentro da pasta onde o arquivo esta:

    python estante_virtual_scraper.py

Por padrao, o script coleta ate 5 paginas. Para alterar esse limite, edite a
ultima linha do arquivo:

    main(max_pages=5)

Substitua o numero pelo total de paginas que deseja coletar, ou passe None
para coletar todas as paginas disponiveis:

    main(max_pages=None)

============================================================================
SAIDA
============================================================================

O script cria uma pasta chamada "files" no mesmo diretorio e salva um arquivo
JSON nomeado com a data de execucao no seguinte formato:

    files/EV_DD_MES_AAAA.json


============================================================================
ESTRUTURA DOS DADOS
============================================================================

Cada entrada no JSON representa um sebo e contem os seguintes campos:

    id              numero identificador do sebo na plataforma
    name            nome do sebo
    link            URL completa para a pagina do sebo na Estante Virtual
    location        objeto com os campos:
                        city    cidade do sebo
                        state   estado do sebo
    freeShipping    booleano indicando se o sebo oferece frete gratis
    memberSince     data de cadastro do sebo na plataforma

============================================================================
ESTRUTURA DO CODIGO
============================================================================

extract_initial_state(html)
    Recebe o HTML de uma pagina e extrai o objeto window.__INITIAL_STATE__
    embutido nos scripts inline. Retorna um dicionario Python ou None em
    caso de falha no parse do JSON.

fetch_page(page)
    Faz a requisicao HTTP para a pagina indicada pelo numero passado como
    argumento. Retorna o estado extraido pela funcao acima ou None em caso
    de erro na requisicao.

parse_sellers(state)
    Recebe o dicionario de estado e extrai a lista de sebos, montando para
    cada um o dicionario com os campos decritos na secao de estrutura de dados.

save_json(filename, data)
    Cria a pasta "files" se ela nao existir e salva a lista de sebos no arquivo
    JSON com o nome recebido como argumento.

main(max_pages)
    Funcao principal. Faz a primeira requisicao para obter o total de paginas
    disponivel, itera sobre as demais paginas respeitando o limite definido,
    agrega todos os sebos coletados e chama save_json ao final.


projeto/
├── estante_virtual_scraper.py     script principal
└── files/                         criada automaticamente
    └── EV_DD_MES_AAAA.json        saida com data
