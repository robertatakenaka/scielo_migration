# scielo_migration

## Instalação

Após clonar o projeto e entrar na pasta, digite:

```
# Crie uma virtualenv
python -m venv .venv

# Ative
source .venv/bin/activate

# Instale os pacotes
pip install -r requirements.txt
```

# Leitura de arquivos `.id` (`ClassicIdFile`)

`ClassicIdFile` é a interface para ler os arquivos `.id` (saída do `i2id`)
das bases `title`, `issue` e `artigo` do site clássico. Ela complementa
`ClassicWebsite`, cujos métodos continuam funcionando como antes.

- Lê o arquivo linha a linha: a memória fica constante (~20 MB),
  independentemente do tamanho do arquivo.
- Para filtrar, lê só o PID e a data. O JSON completo só é montado para
  os itens usados.
- Filtra por data, PID e tipo de item.
- Em `artigo`, junta os registros de cada documento e inclui os registros
  `p` que ficam em arquivos externos.

## Obter o arquivo

Pela `ClassicWebsite` (forma recomendada; aceita base ISIS ou `.id`):

```python
cw = ClassicWebsite(bases_path, bases_work_path, ...)

journals = cw.get_journals_id_file()   # base title
issues = cw.get_issues_id_file()       # base issue
for docs in cw.get_documents_id_files(acron, issue_folder=..., issue_pid=...):
    ...                                # base(s) artigo do fascículo
```

Para `artigo`, a `ClassicWebsite` já configura a busca dos registros `p`
externos em `[bases_work_path, bases_path]`.

Direto, informando o tipo e o caminho do `.id`:

```python
from scielo_classic_website.iid2json.id_file import ClassicIdFile

journals = ClassicIdFile("title", "/bases/title/title.id")    # ou "journal"
issues = ClassicIdFile("issue", "/bases/issue/issue.id")
docs = ClassicIdFile(
    "artigo",                                                 # ou "article"
    "/bases-work/mioc/mioc.id",
    p_records_base_paths=[bases_work_path, bases_path],       # opcional
)
```

Sem `p_records_base_paths`, os registros `p` externos não são incluídos.

## Ler os itens

`items()` retorna um `IdFileItem` por vez, somente os itens bons (os lotes
quebrados ficam em `broken_batches()`):

```python
# title e issue: um registro por item
for item in issues.items(since="20240101"):
    item.pid       # 0074-027620240001
    item.date      # "YYYYMMDD"
    item.data      # o registro em JSON

# artigo: documentos
for item in docs.items(kind="document", since=last_run_date):
    item.pid          # S0074-02762024000100001
    item.issue_pid    # 0074-027620240001
    item.date         # v091 do registro "o"
    item.records      # todos os registros do documento (o, h, f, l, c, p, ...)
    item.p_records    # só os registros "p" (do arquivo principal ou externo)

# artigo: registros "i" (fascículo)
for item in docs.items(kind="issue"):
    item.data
```

Filtros de `items()`, que podem ser combinados:

| Parâmetro | Uso |
|---|---|
| `since`, `until` | Datas `YYYYMMDD` (`"20240315"`), `date` ou `datetime`. `since`: data igual ou maior; `until`: data igual ou menor. |
| `pids` | Lista de PIDs. |
| `kind` | `"document"` ou `"issue"` em artigo; `"journal"` em title; `"issue"` em issue. |
| `date_field` | Campo de data: `"update"` (padrão), `"creation"`, `"publication"` (só artigo) ou uma tag (`"v091"`). |
| `include_undated` | Com filtro de data, inclui itens sem data (padrão `False`). |

Campos de data por base:

| Base | `update` | `creation` | `publication` |
|---|---|---|---|
| title | v941 | v940 | — |
| issue | v091 | v093 | — |
| artigo | v091 | v093 | v065 |

A data de cada item vem do primeiro registro do item que tem o campo. Em
`artigo`, o v091 fica no registro `o`.

Outras formas de leitura:

```python
docs.pids(**filtros)                   # só PIDs
docs.pids_and_dates(**filtros)         # (pid, date)
docs.pids_and_records(**filtros)       # (pid, records), mesmo formato de id2json3
docs.pids_dates_and_records(**filtros) # (pid, date, records)
```

## Buscar um documento

```python
item = docs.get(pid)       # uma busca: lê o arquivo até o fim

docs.build_index()         # várias buscas: monta o índice uma vez
for pid in pids:
    item = docs.get(pid)   # acesso direto, menos de 1 ms por busca
```

Se um PID aparece mais de uma vez no arquivo, `get()` e o índice retornam a
última ocorrência. `items()` retorna todas. Lotes quebrados são ignorados por
`items()`, `get()` e o índice: um `o` solto depois do documento completo não
o substitui.

## Formato de `records`

O mesmo de `id2json3.pids_and_their_records`: uma lista de registros, cada
um um dicionário `tag -> lista de ocorrências`, com os subcampos como chaves
e o conteúdo sem subcampo em `"_"`:

```python
[
    {"v706": [{"_": "o"}], "v880": [{"_": "S0074-02762024000100001"}], "v091": [{"_": "20240115"}]},
    {"v706": [{"_": "h"}], "v012": [{"_": "Título", "l": "pt"}, {"_": "Title", "l": "en"}]},
    ...
]
```

## Regras de leitura da base `artigo`

- Os registros de um documento formam um lote que segue a ordem
  `o`, `h`, `f`, `l`, `p`, `c`, `r`. Tipos podem faltar, mas a ordem não se
  inverte (`o` nunca vem depois de `h`), e só `p`, `c` e `r` se repetem.
  Um novo lote começa quando a ordem se inverte, quando um tipo que não se
  repete aparece de novo ou quando o PID muda.
- O registro `i` (fascículo) não faz parte de nenhum documento. Ele é
  retornado como item próprio (`kind="issue"`), mesmo quando está no meio
  dos registros de um documento.
- Registros sem v706 (por exemplo, só `v880=S` e `v936`) são ignorados.
- Registros `p`: se o documento tem `p` no arquivo principal, eles são
  usados e o arquivo externo não é consultado. Se não tem, `records` inclui
  os `p` de `{base}/artigo/p/{pid[1:10]}/{pid[10:14]}/{pid[14:18]}/{pid[-5:]}.id`,
  quando o arquivo existe. Se não existe, o documento fica sem `p`.
- `kind="document"`: lote que começa com `o`, tem `h` e PID de 23
  caracteres. Qualquer outro lote é `kind="broken"`.

### Lotes quebrados

Lotes quebrados não são documentos e não devem ser processados como
tais. Por isso `items()` (e `pids()`, `pids_and_records()`, `get()`...) não
os retorna: eles ficam separados, para auditoria. A biblioteca não os avalia
nem gera erro, e eles não são filtrados (os filtros de data, PID e `kind` são
de `items()`):

```python
for batch in docs.broken_batches():   # todos os lotes; sem filtros
    batch.pid
    batch.record_types   # ("h", "f", "l", "c", ...)
    batch.mfn, batch.last_mfn, batch.offset
    batch.records
```

Exemplos encontrados num arquivo real: um `o` solto (o documento completo
aparece mais adiante) e um lote `h`, `f`, `l`, `c`... sem `o`.

Para ler os itens bons e os lotes quebrados sem ler o arquivo duas vezes,
chame `broken_batches()` depois de uma leitura completa:

```python
for item in docs.items():             # leitura completa: registra a posição
    ...                               # (offset) de cada lote quebrado
for batch in docs.broken_batches():   # lê só os lotes, a partir das posições
    ...
```

- O custo é um inteiro por lote quebrado.
- Contam como leitura completa `items()`, `pids()`, `build_index()`,
  `get()` sem índice etc., com qualquer filtro, desde que o consumidor
  não interrompa a leitura.
- Se não houve leitura completa, ou se o arquivo mudou desde então (tamanho
  ou data de modificação), `broken_batches()` lê o arquivo inteiro.

Em todas as bases, quebras de linha dentro do conteúdo de um campo viram um
espaço simples. Só é campo novo uma linha `!v<tag>!` e só é registro novo
uma linha `!ID <número>`.

## Recomendações de uso

- Não use `list(docs.items())`: isso carrega tudo na memória. Processe item
  a item.
- Só acesse `item.records` quando for usar os registros. Para decidir o que
  processar, use `pid`, `date` e `kind`.
- Para ler só o que mudou, guarde a data da última execução e passe-a em
  `since`. O arquivo é lido inteiro, mas só os itens no intervalo são
  convertidos.
- A posição no arquivo não indica a data: o arquivo está em ordem de
  processamento, e o v091 de cada artigo pode ser anterior à data de
  processamento do fascículo. Não interrompa a leitura com base na data.
- O v091 de um artigo pode se manter quando o fascículo é reprocessado. Se
  for preciso detectar reprocessamentos, compare por fascículo (por exemplo,
  pelo v091 do registro `i`) ou pelo conteúdo.

## Desempenho

Comparação com `id2json3.pids_and_their_records` (usado pelos métodos
antigos de `ClassicWebsite`) em um `.id` real de artigos (153 MB, 214 mil
registros):

| Operação | `id2json3` | `ClassicIdFile` |
|---|---|---|
| Converter tudo para JSON | 6,9 s / 540 MB | 7,7 s / 24 MB |
| Filtro por data + JSON dos itens filtrados | 6,9 s / 540 MB | 3,1 s / 22 MB |
| Só PIDs e datas | 6,9 s / 540 MB | 3,1 s / 19 MB |
| Buscar um PID | 6,8 s / 540 MB | 3,0 s / 19 MB |
| 100 buscas (com `build_index()`) | ~680 s | 3,0 s (índice) + 0,08 s |
| Lotes quebrados depois de `items()` | — | 0,006 s (138 lotes) |

A memória do `id2json3` cresce com o tamanho do arquivo (cerca de 1 GB para
um arquivo de 400 MB). A do `ClassicIdFile` fica constante.

## Migrar dos métodos antigos

| `ClassicWebsite` (antigo) | Nova interface |
|---|---|
| `get_journals_pids_and_records()` | `cw.get_journals_id_file().pids_and_records()` |
| `get_issues_pids_and_records()` | `cw.get_issues_id_file().pids_and_records()` |
| `get_document_records(source_paths)` | `cw.get_documents_id_files(...)` e `.items(kind="document")` |
| `get_issue_doc_records(...)` | `items()`, separando por `item.kind` e `item.issue_pid` |
| `get_p_records(pid)` | `item.p_records` |

Em relação ao `id2json3`, `ClassicIdFile` se comporta de forma diferente em
alguns casos:

- registros `i` repetidos ou no meio de um documento não separam o documento;
- registros sem v706 não são anexados ao documento seguinte;
- lotes sem registro `o` ou `h` são `kind="broken"`, não documentos;
- campos com o byte `\x85` não são cortados;
- linhas vazias são ignoradas;
- arquivo inexistente gera `FileNotFoundError`, em vez de retornar uma lista
  vazia.

# Models Builder

## CSV input format
```
record,tag,subfield,subfield_name,multi_val,composite,field_name,name,description
Issue,31,,,,,volume,volume,Volume
Issue,32,,,,,number,number,Number
Issue,43,,,,,_start_end_months, start end months, Start End Months
Issue,,,,,,start_month,start month,Start Month
Issue,,,,,,end_month,end month,End Month
Issue,131,,,,,supplement_volume,supplement volume,Supplement Volume
Issue,132,,,,,supplement_number,supplement number,Supplement Number
Issue,,,,,,is_ahead_of_print,is ahead of print,Is Ahead Of Print

```


## Commands

Create a JSON version of `tests/fixtures/models_builder/issue_record.csv` (`/path/output/issue.json`)

```console
python scielo_classic_website/cli/models_builder.py generate_json_data_dictionary tests/fixtures/models_builder/issue_record.csv /path/output/issue.json
```

Create the python modules `/path/output/base_issue.py` and `/path/output/issue.py` given a CSV file (`issue_record.csv`)

```console
python scielo_classic_website/cli/models_builder.py generate_model tests/fixtures/models_builder/issue_record.csv Issue Issue /path/output/issue.py
```