# Atualizar integração no servidor

Projeto em Python: copiar código, manter `.config` e dependências alinhadas ao `requirements.txt`.

## 1. Antes de atualizar

- Fazer **backup** da pasta atual no servidor (principalmente `.config` e eventuais CSVs/relatórios importantes).
- Anotar como a integração é **disparada** hoje (Agendador de Tarefas no Windows, **cron** no Linux, serviço manual, etc.).

## 2. O que enviar para o servidor

**Incluir (código):**

- `main.py`, todos os `.py` dos módulos (`empresas`, `departamentos`, `cargos`, `funcionarios`, `afastamentos`, `demissoes`, `ferias`, etc.)
- `config_reader.py`
- `requirements.txt`
- Scripts opcionais que usarem: `consulta_funcionarios_ativos.py`, `relatorio_funcionarios_demitidos.py`, `gerar_pdf_requisitos.py`, documentação (`REQUISITOS_*.md`/`.pdf`)

**Não versionar em repositório público (tratar com cuidado):**

- **`.config`** — contém token e senhas. No servidor, **não substituir** o `.config` de produção pelo de desenvolvimento, a menos que seja intencional. Após copiar o código novo, **reaplique** o `.config` de produção se tiver sido sobrescrito por engano.

**Não obrigatório copiar:**

- `__pycache__`, `*.pyc`, CSVs gerados (`*_api.csv`), `logs_demissao/`, relatórios antigos (opcional manter histórico).

## 3. Ambiente Python no servidor

Na pasta da integração:

```bash
# Exemplo Linux
cd /caminho/hevi-integracao
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

No **Windows Server**, equivalente:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

**Nota Linux:** algumas entradas do `requirements.txt` são típicas de Windows (`pyinstaller`, `pywin32-ctypes`). Se `pip install -r requirements.txt` falhar, instale apenas o necessário à execução:

```bash
pip install requests pandas pytz
```

(+ `pip install markdown xhtml2pdf` só se forem usar `gerar_pdf_requisitos.py`.)

Confirme se `configparser` está disponível (vem na biblioteca padrão do Python 3).

## 4. Teste rápido após deploy

Na pasta onde está o `.config`:

```bash
# Só funcionários CSV (sem Hevi), se já usarem esse fluxo:
python funcionarios.py csv

# Integração completa (cuidado: envia dados à Hevi / SOAP onde aplicável):
python main.py
```

Ajustar o comando ao interpretador correto (`python` vs `python3` vs `.venv/scripts/python`).

## 5. Agendamento

- **Windows:** Agendador de Tarefas — apontar “Programa” para o `python.exe` do venv e “Argumentos” para o caminho completo de `main.py`; “Iniciar em” = pasta do projeto (onde está o `.config`).
- **Linux:** `crontab -e`:

```cron
# Exemplo: todo dia às 02:15
15 2 * * * cd /opt/hevi-integracao && . .venv/bin/activate && python main.py >> logs/cron.log 2>&1
```

## 6. Transporte dos arquivos

Formas usuais: **Git** (pull no VPS), **rsync** ou **scp** por SSH, **SFTP** (WinSCP/FileZilla).  

**Nunca** publique o `.config` em repositório **público**. Use repositório **privado** ou envie o `.config` só por canal seguro (scp separado, secret do painel, etc.).

---

## 6.1 VPS Linux — subir ou atualizar o código (SSH)

Substitua `USUARIO`, `IP_DO_VPS` e `/opt/hevi-integracao` pelos valores reais.

### Primeira vez no VPS (preparar pasta e venv)

Conecte: `ssh USUARIO@IP_DO_VPS`

```bash
sudo mkdir -p /opt/hevi-integracao
sudo chown "$USER:$USER" /opt/hevi-integracao
cd /opt/hevi-integracao
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
# Se requirements.txt falhar no Linux (pacotes Windows), use:
pip install requests pandas pytz
```

Crie o **`.config`** direto no VPS (nano/vi) ou copie **uma vez** do seu PC:

```bash
# No seu computador (exemplo scp do Windows PowerShell ou Linux):
scp .config USUARIO@IP_DO_VPS:/opt/hevi-integracao/.config
```

### Opção A — Atualizar com **Git** (recomendado)

**No PC:** commit + push para branch (ex.: `main`), **sem** commitar `.config` (`git status` deve mostrar `.config` ignorado ou fora do repo).

**No VPS:**

```bash
cd /opt/hevi-integracao
# Se ainda não for um clone:
# git clone https://github.com/SUA_ORG/hevi-integracao.git .
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt || pip install -U requests pandas pytz
python3 funcionarios.py csv   # teste opcional
```

### Opção B — **rsync** (do seu PC para o VPS)

Exclui `.config` no envio para **não sobrescrever** produção (o `.config` continua só no servidor).

**Linux / macOS / WSL:**

```bash
cd /caminho/para/pasta/pai
rsync -avz --delete \
  --exclude '.config' \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude 'logs_demissao' \
  --exclude '*.csv' \
  ./hevi-integracao/ USUARIO@IP_DO_VPS:/opt/hevi-integracao/
```

**Depois no VPS:** `ssh` + `source .venv/bin/activate` + `pip install ...` como acima.

### Opção C — **scp** ou **ZIP** (Windows PowerShell)

Compacte a pasta **sem** incluir `.config` de desenvolvimento se for substituir tudo, ou envie só os `.py` + `requirements.txt`.

```powershell
# Exemplo: enviar pasta inteira (atenção: pode sobrescrever .config — faça backup no VPS antes)
scp -r C:\caminho\hevi-integracao\* USUARIO@IP_DO_VPS:/opt/hevi-integracao/
```

### Checklist pós-deploy no VPS

```bash
cd /opt/hevi-integracao
test -f .config && echo "OK .config existe" || echo "FALTA .config"
source .venv/bin/activate
python3 funcionarios.py csv
# ou: python3 main.py   (integração completa — cuidado em produção)
```

### Agendamento no VPS (cron)

```bash
mkdir -p /opt/hevi-integracao/logs
crontab -e
```

Exemplo (diário 02:15):

```cron
15 2 * * * cd /opt/hevi-integracao && . .venv/bin/activate && /usr/bin/python3 main.py >> /opt/hevi-integracao/logs/cron.log 2>&1
```

Use caminho absoluto do `python` do venv se preferir: `/opt/hevi-integracao/.venv/bin/python`.

### Firewall

Garantir saída **HTTPS (443)** para APIs Alterdata/Hevi e URL do SOAP. Nada a abrir na entrada se o script só inicia conexões de saída.

---

## 7. Rollback

Se algo falhar, restaurar a pasta inteira do **backup** do passo 1 e só então revisar erro (versão Python, permissões na pasta OneDrive no servidor, token expirado no `.config`, etc.).

---

*Documento genérico: adapte caminhos, usuário e política de credenciais da sua infraestrutura.*
