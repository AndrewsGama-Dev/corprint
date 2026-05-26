# Informações necessárias do cliente para nova integração (Folha → Ponto)

Este projeto gera CSVs a partir da **API JSON da Folha ** e envia à **API REST Ponto (iFractal)**


## 1. Dados disponíveis Folha (o que esperamos encontrar na API)


- Empresa(s) cadastrada(s) e **ativas**.
- Departamentos (centros de custo) **vinculados ao que aparece nos funcionários**.
- Funcionários com **cargo/função** no padrão que a API envia (ex.: `000108 - DESCRIÇÃO`).
- Para demissões: funcionários **demitidos** com **data de demissão** preenchida no DP.
- Para afastamentos: registros que a API marca com tipo/descrição (ex.: **não é férias** no módulo de afastamentos, pois o fluxo atual de afastamentos exclui férias quando filtra pela descrição).


--

## 2. Arquivos CSV gerados e colunas esperadas pelo integrador

Separador: **`;`** — codificação típica: **UTF-8 com BOM** (`utf-8-sig`).

### 2.1 `empresas_api.csv` (Ponto: `configuracao_empresa`)

| Coluna | Origem / observação |
|--------|---------------------|
| `codigo_legado` | ID da empresa na API. |
| `campo_chave` | Fixo: `codigo_legado`. |
| `nro` | Idem ID empresa. |
| `nome` | Nome da empresa. |
| `cnpj` | `cpfcnpj` na API. |
| `inscricao_estadual`, `cep`, `bairro`, `telefone`, `email`, `site` | Hoje muitas vezes **vazios** se a API não expõe; **cidade/UF podem estar fixos no código** (ex.: Manaus/AM) — validar com o cliente se precisam de endereço real na Ponto. |
| `endereco` | Quando disponível na API. |
| `nome_relatorio` | Pode ser nulo. |


### 2.2 `departamentos_api.csv` (Ponto: `configuracao_depto`)

| Coluna | Origem |
|--------|--------|
| `campo_chave` | Fixo: `codigo_legado`. |
| `codigo_legado` | ID do departamento (centro de custo) na API. |
| `nome` | Nome do departamento. |
| `conta` | Idem `codigo_legado`. |
| `id-empresa` | ID da empresa vinculada (extraído do vínculo funcionário/empresa). |

**Solicitar ao cliente:** departamentos corretos e **empresa** coerente para cada centro de custo no DP.

### 2.3 `cargos_api.csv` (Ponto: `configuracao_cargo`)

| Coluna | Origem |
|--------|--------|
| `campo_chave` | Fixo: `codigo_legado`. |
| `codigo_legado` | Código extraído do campo `nomefuncao` (antes de ` - `). |
| `nome` | Texto após ` - ` em `nomefuncao`. |
| `id-empresa` | Primeira empresa ativa retornada pela API (padrão do script). |
| `nome_cbo`, `nro_cbo` | Vazios no mapeamento atual. |



### 2.4 `funcionarios_api.csv` (Ponto: `funcionario_cadastrar`)

Principais grupos de colunas (alistar para o cliente alinhar cadastro DP + expectativa Ponto):

- **Identificação:** `nome`, `cpf`, `matricula` (código funcionário), `rg`, `pis`, `login`, `cracha` (uso de CPF/senha padrão conforme código).
- **Datas:** `dtadmissao`, `dtnascimento`.
- **Contato/endereço:** `email`, `endereco`, `bairro`, `cidade`, `uf`, `cep`, `complemento`.
- **Dados pessoais complementares:** `nome_mae`, `nome_pai`, `sexo`, `escolaridade`, `estado_civil`, `qtd_filho`, `nacionalidade`, `naturalidade`, **`orgao_emissor_rg`** (RG).
- **Vínculo:** `cod_empresa`, `codigo_legado_empresa`, `empresa`; `codigo_unidade`, `nome_unidade`, `nro_centro_custo`, `codigo_legado_centro_custo`, `nome_centro_custo`; `codigo_cargo`, `nome_cargo`, `nome_funcao`, etc.
- **Outros:** `salario`, `senha`, `timezone` (fixo atual no projeto: America/Manaus), campos opcionais vazios (CNH, sindicato, escala).

### 2.5 `afastamentos_api.csv` (Ponto: `importar_cad` em endpoint de afastamentos)

| Coluna | Descrição |
|--------|-----------|
| `ID-AFASTAMENTO` | Classificação pelo tipo/descrição do afastamento na API (mapeamento interno por descrição). |
| `DTINICIO` | Data início (`afastamento` na API quando disponível). |
| `DTFIM` | Data fim (`retorno` quando disponível). |
| `OBS` | Texto/descrição do afastamento. |
| `CAMPO_CHAVE` | Fixo: `matricula`. |
| `MATRICULA` | Código do funcionário (matricula). |

**Solicitar ao cliente:** afastamentos com **datas e descrições** claras na API; regra atual **exclui** linhas cuja OBS contém “férias” (flavor do código).

### 2.6 `demissoes_api.csv`

| Coluna | Observação |
|--------|-------------|
| `matricula` | Código zerado à esquerda. |
| `DATA_DEMISSAO` | Derivada da data de demissão na API (`demissao`). |
| `obs`, `motivo`, `tipo_aviso`, `devolveu_cracha`, `dias_indenizados` | Podem estar com **valores fixos/default** no integrador (`demissoes.py`). |
| `data_aviso`, `data_ultimo_dia_trabalhado`, `data_acerto` | **Calculadas no script** em torno da data demissão (regras de negócio do código; podem divergir do contrato trabalhista real). |

---


