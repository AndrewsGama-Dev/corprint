import configparser
import os

def ler_config():
    """
    Lê o arquivo .config e retorna um dicionário com todas as seções
    """
    try:
        if not os.path.exists('.config'):
            print("❌ Arquivo .config não encontrado")
            return None
        
        config = configparser.ConfigParser()
        config.read('.config', encoding='utf-8')
        
        # Converter para dicionário para facilitar o uso
        config_dict = {}
        for secao in config.sections():
            config_dict[secao] = dict(config[secao])
        
        return config_dict
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo .config: {e}")
        return None

def ler_token_config():
    """
    Lê especificamente o token da seção APISOURCE
    """
    try:
        config = ler_config()
        if config and 'APISOURCE' in config:
            token = config['APISOURCE'].get('token')
            if token:
                print("✅ Token carregado do arquivo .config")
                return token.strip('"')  # Remove aspas se houver
        
        print("❌ Token não encontrado na seção [APISOURCE]")
        return None
        
    except Exception as e:
        print(f"❌ Erro ao ler token: {e}")
        return None

def obter_headers_api():
    """
    Obtém os headers necessários para chamadas à API da Alterdata
    """
    token = ler_token_config()
    if not token:
        return None
    
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': f'Bearer {token}'
    }
    
    return headers


def ler_codigo_empresa_filtro():
    """
    Lê o ID da empresa a filtrar na seção [FILTROS] do .config.

    Returns:
        str | None: ID da empresa (ex.: "129") ou None se não configurado
                    (integração traz funcionários de todas as empresas).
    """
    try:
        config = ler_config()
        if not config or 'FILTROS' not in config:
            return None

        codigo = (config['FILTROS'].get('codigo_empresa') or '').strip().strip('"')
        if not codigo:
            return None

        return codigo
    except Exception as e:
        print(f"❌ Erro ao ler codigo_empresa do .config: {e}")
        return None


def _parse_bool_config(valor, default=True):
    """Interpreta true/false, 1/0, sim/nao, yes/no (case insensitive)."""
    if valor is None:
        return default
    texto = str(valor).strip().strip('"').lower()
    if texto in ('true', '1', 'yes', 'y', 'sim', 's', 'on'):
        return True
    if texto in ('false', '0', 'no', 'n', 'nao', 'não', 'off'):
        return False
    return default


MODULOS_PADRAO = (
    'empresas',
    'departamentos',
    'cargos',
    'funcionarios',
    'afastamentos',
    'demissoes',
)


def ler_modulos_habilitados():
    """
    Lê a seção [MODULOS] do .config (true/false por módulo).

    Se a seção não existir, todos os módulos ficam habilitados (compatibilidade).
    """
    habilitados = {nome: True for nome in MODULOS_PADRAO}
    try:
        config = ler_config()
        if not config or 'MODULOS' not in config:
            return habilitados

        secao = config['MODULOS']
        for nome in MODULOS_PADRAO:
            if nome in secao:
                habilitados[nome] = _parse_bool_config(secao.get(nome), default=True)
        return habilitados
    except Exception as e:
        print(f"❌ Erro ao ler [MODULOS] do .config: {e}")
        return habilitados


def modulo_habilitado(nome_modulo):
    """Retorna True se o módulo deve ser executado conforme [MODULOS]."""
    return bool(ler_modulos_habilitados().get(nome_modulo, True))