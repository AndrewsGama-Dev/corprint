# Atualizar integração no servidor

Projeto em Python: **corprint** — copiar código, manter `.config` e dependências alinhadas ao `requirements.txt`.

**Caminho no servidor:** `/home/gogotech/integracao/corprint`  
**Repositório:** https://github.com/AndrewsGama-Dev/corprint.git

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
cd /home/gogotech/integracao/corprint
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
# Só funcionários CSV (sem envio ao destino), se já usarem esse fluxo:
python3 funcionarios.py csv

# Integração completa (cuidado: envia dados ao destino / SOAP onde aplicável):
python3 main.py
```

Ajustar o comando ao interpretador correto (`python` vs `python3` vs `.venv/bin/python`).

## 5. Agendamento

- **Windows:** Agendador de Tarefas — apontar “Programa” para o `python.exe` do venv e “Argumentos” para o caminho completo de `main.py`; “Iniciar em” = pasta do projeto (onde está o `.config`).
- **Linux:** `crontab -e`:

```cron
# Exemplo: todo dia às 02:15
15 2 * * * cd /home/gogotech/integracao/corprint && . .venv/bin/activate && python main.py >> logs/cron.log 2>&1
```

## 6. Transporte dos arquivos

Formas usuais: **Git** (pull no VPS), **rsync** ou **scp** por SSH, **SFTP** (WinSCP/FileZilla).  

**Nunca** publique o `.config` em repositório **público**. Use repositório **privado** ou envie o `.config` só por canal seguro (scp separado, secret do painel, etc.).

---

## 6.1 VPS Linux — subir ou atualizar o código (SSH)

Caminho fixo desta integração: `/home/gogotech/integracao/corprint`

### Primeira vez no VPS (preparar pasta e venv)

Conecte: `ssh gogotech@IP_DO_VPS`

```bash
mkdir -p /home/gogotech/integracao/corprint
cd /home/gogotech/integracao/corprint
git clone https://github.com/AndrewsGama-Dev/corprint.git .
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
# Se requirements.txt falhar no Linux (pacotes Windows), use:
pip install requests pandas pytz
```

Crie o **`.config`** direto no VPS (nano/vi) ou copie **uma vez** do seu PC (incluir `[FILTROS] codigo_empresa = 129`):

```bash
# No seu computador (exemplo scp do Windows PowerShell ou Linux):
scp .config gogotech@IP_DO_VPS:/home/gogotech/integracao/corprint/.config
```

### Opção A — Atualizar com **Git** (recomendado)

**No PC:** commit + push para branch (ex.: `main`), **sem** commitar `.config` (`git status` deve mostrar `.config` ignorado ou fora do repo).

**No VPS:**

```bash
cd /home/gogotech/integracao/corprint
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
  ./corprint/ gogotech@IP_DO_VPS:/home/gogotech/integracao/corprint/
```

**Depois no VPS:** `ssh` + `source .venv/bin/activate` + `pip install ...` como acima.

### Opção C — **scp** ou **ZIP** (Windows PowerShell)

Compacte a pasta **sem** incluir `.config` de desenvolvimento se for substituir tudo, ou envie só os `.py` + `requirements.txt`.

```powershell
# Exemplo: enviar pasta inteira (atenção: pode sobrescrever .config — faça backup no VPS antes)
scp -r C:\caminho\corprint\* gogotech@IP_DO_VPS:/home/gogotech/integracao/corprint/
```

### Checklist pós-deploy no VPS

```bash
cd /home/gogotech/integracao/corprint
test -f .config && echo "OK .config existe" || echo "FALTA .config"
source .venv/bin/activate
python3 funcionarios.py csv
# ou: python3 main.py   (integração completa — cuidado em produção)
```

### Agendamento no VPS (cron) — `integrador.sh`

Preferir **`integrador.sh`** (executa `python main.py` com código do Git).

```bash
cd /home/gogotech/integracao/corprint
chmod +x integrador.sh
crontab -e
```

Exemplo de linha no cron:

```cron
*/30 * * * * cd /home/gogotech/integracao/corprint && flock -n /tmp/integrador_corprint.lock ./integrador.sh >> /home/gogotech/integracao/corprint/integrador.log 2>&1
```

Rotação de log (se existir `rotaciona_log.sh`):

```cron
0 3 * * * /home/gogotech/integracao/corprint/rotaciona_log.sh
```

Teste manual antes do cron:

```bash
cd /home/gogotech/integracao/corprint
./integrador.sh
```

### Firewall

Garantir saída **HTTPS (443)** para APIs Alterdata/destino e URL do SOAP. Nada a abrir na entrada se o script só inicia conexões de saída.

---

## 7. Rollback

Se algo falhar, restaurar a pasta inteira do **backup** do passo 1 e só então revisar erro (versão Python, permissões, token expirado no `.config`, etc.).

---

*Integração corprint — caminho padrão: `/home/gogotech/integracao/corprint`*
