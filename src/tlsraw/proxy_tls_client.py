#!/usr/bin/env python3
"""
Proxy TLS Client - Extensão do TLS Raw Client para suporte a proxy corporativo
Suporta HTTP CONNECT proxy com autenticação para ambientes corporativos
"""

import base64
import socket
import struct
import time
import logging
import json
import os
from typing import Dict, Any, Optional
from .tls_raw_client import TLSRawClient

logger = logging.getLogger(__name__)

class ProxyTLSClient(TLSRawClient):
    """
    Cliente TLS com suporte a proxy HTTP CONNECT
    Extende TLSRawClient para funcionar através de proxies corporativos
    """
    
    def __init__(self, 
                 host: str, 
                 port: int,
                 proxy_host: str,
                 proxy_port: int,
                 proxy_username: Optional[str] = None,
                 proxy_password: Optional[str] = None,
                 timeout: int = 30,
                 config_file: Optional[str] = None):
        """
        Inicializa cliente TLS com proxy
        
        Args:
            host: Servidor de destino
            port: Porta do servidor de destino
            proxy_host: Endereço do proxy
            proxy_port: Porta do proxy
            proxy_username: Usuário para autenticação no proxy (opcional)
            proxy_password: Senha para autenticação no proxy (opcional)
            timeout: Timeout para conexões
            config_file: Arquivo de configuração para sobrescrever parâmetros (opcional)
        """
        # Se config_file foi fornecido, carregar configurações
        if config_file:
            config = self._load_config_file(config_file)
            if config:
                # Sobrescrever parâmetros com valores do arquivo
                host = config.get("target_host", host)
                port = config.get("target_port", port)
                proxy_host = config.get("proxy_host", proxy_host)
                proxy_port = config.get("proxy_port", proxy_port)
                proxy_username = config.get("proxy_username", proxy_username)
                proxy_password = config.get("proxy_password", proxy_password)
                timeout = config.get("timeout", timeout)
                
                logger.info(f"Configuração carregada de: {config_file}")
        
        # Inicializar classe pai
        super().__init__(host, port, timeout)
        
        # Configurações do proxy
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.config_file = config_file
        
        logger.info(f"Proxy configurado: {proxy_host}:{proxy_port}")
        if proxy_username:
            logger.info(f"Autenticação proxy: {proxy_username}")
    
    def _load_config_file(self, config_path: str) -> Optional[Dict[str, Any]]:
        """
        Carrega configuração de arquivo JSON
        
        Args:
            config_path: Caminho para arquivo de configuração
            
        Returns:
            Dicionário com configuração ou None se erro
        """
        try:
            # Verificar caminhos relativos e absolutos
            search_paths = [
                config_path,  # Caminho exato fornecido
                os.path.join(os.getcwd(), config_path),  # Relativo ao diretório atual
                os.path.join(os.path.dirname(__file__), config_path),  # Relativo ao script
                os.path.join(os.path.expanduser("~"), ".tlsraw", config_path),  # Home do usuário
            ]
            
            config_found = None
            for path in search_paths:
                if os.path.isfile(path):
                    config_found = path
                    break
            
            if not config_found:
                logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
                logger.info(f"Caminhos pesquisados: {search_paths}")
                return None
            
            with open(config_found, 'r', encoding='utf-8') as f:
                config = json.load(f)
                logger.info(f"Configuração carregada de: {config_found}")
                return config
                
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao interpretar JSON em {config_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar configuração de {config_path}: {e}")
            return None
    
    @classmethod
    def from_config_file(cls, config_file: str, **overrides) -> 'ProxyTLSClient':
        """
        Cria instância a partir de arquivo de configuração
        
        Args:
            config_file: Caminho para arquivo de configuração
            **overrides: Parâmetros para sobrescrever configuração do arquivo
            
        Returns:
            Instância de ProxyTLSClient configurada
            
        Example:
            client = ProxyTLSClient.from_config_file("proxy_config.json")
            client = ProxyTLSClient.from_config_file("proxy_config.json", target_host="outro.com")
        """
        # Carregar configuração base
        instance = cls.__new__(cls)
        config = instance._load_config_file(config_file)
        
        if not config:
            raise ValueError(f"Não foi possível carregar configuração de: {config_file}")
        
        # Aplicar overrides
        final_config = {**config, **overrides}
        
        # Verificar campos obrigatórios
        required_fields = ["target_host", "target_port", "proxy_host", "proxy_port"]
        missing_fields = [field for field in required_fields if field not in final_config]
        
        if missing_fields:
            raise ValueError(f"Campos obrigatórios ausentes na configuração: {missing_fields}")
        
        # Inicializar com configuração completa
        return cls(
            host=final_config["target_host"],
            port=final_config["target_port"],
            proxy_host=final_config["proxy_host"],
            proxy_port=final_config["proxy_port"],
            proxy_username=final_config.get("proxy_username"),
            proxy_password=final_config.get("proxy_password"),
            timeout=final_config.get("timeout", 30),
            config_file=config_file
        )
    
    def save_config(self, config_file: str) -> bool:
        """
        Salva configuração atual em arquivo
        
        Args:
            config_file: Caminho para salvar configuração
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        config = {
            "target_host": self.host,
            "target_port": self.port,
            "proxy_host": self.proxy_host,
            "proxy_port": self.proxy_port,
            "proxy_username": self.proxy_username,
            "proxy_password": self.proxy_password,
            "timeout": self.timeout,
            "_metadata": {
                "created_by": "ProxyTLSClient",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "description": f"Configuração para {self.host}:{self.port} via {self.proxy_host}:{self.proxy_port}"
            }
        }
        
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuração salva em: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração em {config_file}: {e}")
            return False
    
    def list_available_configs(self, config_dir: str = None) -> Dict[str, str]:
        """
        Lista arquivos de configuração disponíveis
        
        Args:
            config_dir: Diretório para pesquisar (opcional)
            
        Returns:
            Dict com nome_arquivo: caminho_completo
        """
        if not config_dir:
            search_dirs = [
                os.getcwd(),  # Diretório atual
                os.path.dirname(__file__),  # Diretório do script
                os.path.join(os.path.expanduser("~"), ".tlsraw"),  # Home do usuário
            ]
        else:
            search_dirs = [config_dir]
        
        configs = {}
        
        for directory in search_dirs:
            if not os.path.isdir(directory):
                continue
                
            try:
                for filename in os.listdir(directory):
                    if filename.endswith(('.json', '.config')):
                        full_path = os.path.join(directory, filename)
                        if os.path.isfile(full_path):
                            # Verificar se é um arquivo de configuração válido
                            try:
                                with open(full_path, 'r', encoding='utf-8') as f:
                                    config = json.load(f)
                                    if "proxy_host" in config and "target_host" in config:
                                        configs[filename] = full_path
                            except:
                                continue  # Ignorar arquivos JSON inválidos
                                
            except Exception as e:
                logger.debug(f"Erro ao listar diretório {directory}: {e}")
        
        return configs
    
    def _create_proxy_auth_header(self) -> str:
        """
        Cria header de autenticação Basic para proxy
        
        Returns:
            Header Proxy-Authorization ou string vazia
        """
        if not self.proxy_username or not self.proxy_password:
            return ""
        
        # Codificar credenciais em Base64
        credentials = f"{self.proxy_username}:{self.proxy_password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('ascii')
        
        return f"Proxy-Authorization: Basic {encoded_credentials}\r\n"
    
    def _send_connect_request(self) -> bool:
        """
        Envia requisição HTTP CONNECT através do proxy
        
        Returns:
            True se CONNECT foi bem-sucedido, False caso contrário
        """
        # Criar requisição CONNECT
        connect_request = f"CONNECT {self.host}:{self.port} HTTP/1.1\r\n"
        connect_request += f"Host: {self.host}:{self.port}\r\n"
        connect_request += "User-Agent: TLS-Raw-Client/1.0\r\n"
        
        # Adicionar autenticação se configurada
        auth_header = self._create_proxy_auth_header()
        if auth_header:
            connect_request += auth_header
        
        connect_request += "\r\n"
        
        logger.debug(f"Enviando CONNECT: {connect_request.strip()}")
        
        try:
            # Enviar requisição CONNECT
            self.socket.send(connect_request.encode('utf-8'))
            
            # Receber resposta do proxy
            response = self.socket.recv(4096).decode('utf-8')
            logger.debug(f"Resposta CONNECT: {response.strip()}")
            
            # Verificar se CONNECT foi bem-sucedido
            if "200 Connection established" in response or "200 OK" in response:
                logger.info("CONNECT estabelecido com sucesso")
                return True
            else:
                logger.error(f"CONNECT falhou: {response.strip()}")
                return False
                
        except Exception as e:
            logger.error(f"Erro durante CONNECT: {e}")
            return False
    
    def _establish_proxy_connection(self) -> bool:
        """
        Estabelece conexão através do proxy usando HTTP CONNECT
        
        Returns:
            True se conexão foi estabelecida, False caso contrário
        """
        try:
            # Conectar ao proxy primeiro
            logger.info(f"Conectando ao proxy {self.proxy_host}:{self.proxy_port}")
            self.socket.connect((self.proxy_host, self.proxy_port))
            
            # Enviar CONNECT para estabelecer túnel
            if not self._send_connect_request():
                return False
            
            logger.info(f"Túnel proxy estabelecido para {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao estabelecer conexão proxy: {e}")
            return False
    
    def test_proxy_connectivity(self) -> Dict[str, Any]:
        """
        Testa conectividade básica com o proxy
        
        Returns:
            Dict com resultados do teste
        """
        results = {
            "timestamp": time.time(),
            "proxy_host": self.proxy_host,
            "proxy_port": self.proxy_port,
            "proxy_connection_success": False,
            "proxy_auth_configured": bool(self.proxy_username),
            "connect_success": False,
            "error": None
        }
        
        try:
            # Criar socket para teste
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(self.timeout)
            
            # Testar conexão básica com proxy
            start_time = time.time()
            test_socket.connect((self.proxy_host, self.proxy_port))
            connect_time = time.time() - start_time
            
            results["proxy_connection_success"] = True
            results["proxy_connect_time"] = connect_time
            
            logger.info(f"Conexão com proxy bem-sucedida em {connect_time:.3f}s")
            
            # Testar CONNECT básico
            self.socket = test_socket
            if self._send_connect_request():
                results["connect_success"] = True
                logger.info("Teste CONNECT bem-sucedido")
            else:
                results["error"] = "CONNECT falhou"
            
            test_socket.close()
            
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"Erro no teste de proxy: {e}")
        
        return results
    
    def connect_and_test(self, use_sni: bool = True) -> Dict[str, Any]:
        """
        Conecta através do proxy e testa handshake TLS
        Sobrescreve o método da classe pai para usar proxy
        
        Args:
            use_sni: Se deve usar SNI (Server Name Indication)
            
        Returns:
            Dict com resultados do teste
        """
        results = {
            "timestamp": time.time(),
            "host": self.host,
            "port": self.port,
            "proxy_host": self.proxy_host,
            "proxy_port": self.proxy_port,
            "proxy_auth_used": bool(self.proxy_username),
            "proxy_connection_success": False,
            "connect_tunnel_success": False,
            "connection_success": False,
            "client_hello_sent": False,
            "server_response": None,
            "error": None,
            "raw_response": None
        }
        
        try:
            logger.info(f"Conectando através do proxy para {self.host}:{self.port}")
            
            # Criar socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            
            # Estabelecer conexão através do proxy
            if not self._establish_proxy_connection():
                results["error"] = "Falha ao estabelecer túnel proxy"
                return results
            
            results["proxy_connection_success"] = True
            results["connect_tunnel_success"] = True
            results["connection_success"] = True
            
            # A partir daqui, usar lógica normal do TLS client
            # (o socket agora está tunelado através do proxy)
            
            # Criar e enviar Client Hello
            server_name = self.host if use_sni else None
            client_hello = self.create_client_hello(server_name)
            
            logger.info(f"Enviando Client Hello através do proxy ({len(client_hello)} bytes)...")
            logger.debug(f"Client Hello hex: {client_hello.hex()}")
            
            self.socket.send(client_hello)
            results["client_hello_sent"] = True
            results["client_hello_size"] = len(client_hello)
            
            # Tentar receber resposta
            logger.info("Aguardando resposta do servidor através do proxy...")
            
            try:
                response = self.socket.recv(4096)
                if response:
                    logger.info(f"Resposta recebida através do proxy: {len(response)} bytes")
                    logger.debug(f"Resposta hex: {response.hex()}")
                    
                    results["raw_response"] = response.hex()
                    results["response_size"] = len(response)
                    results["raw_response_bytes"] = response
                    
                    # Usar análise de resposta da classe pai
                    response_analysis = self.analyze_response(response)
                    results["response_analysis"] = response_analysis
                    
                    # Processar resposta usando lógica da classe pai
                    if response_analysis["likely_tls"]:
                        parsed = self.parse_tls_record(response)
                        results["server_response"] = parsed
                        logger.info(f"Resposta TLS através do proxy: {parsed.get('type', 'Unknown')}")
                    else:
                        # Resposta não-TLS
                        firewall_info = self.extract_firewall_info(response)
                        results["server_response"] = {
                            "type": "Non-TLS Response",
                            "detected_type": response_analysis["detected_type"],
                            "likely_source": response_analysis["likely_source"],
                            "preview": response_analysis["preview"],
                            "firewall_info": firewall_info
                        }
                        logger.warning(f"Resposta não-TLS através do proxy: {response_analysis['detected_type']}")
                
                else:
                    logger.warning("Conexão fechada pelo servidor sem resposta")
                    results["error"] = "Conexão fechada sem resposta"
                    
            except socket.timeout:
                logger.warning("Timeout aguardando resposta do servidor")
                results["error"] = "Timeout na resposta do servidor"
                
        except Exception as e:
            logger.error(f"Erro durante teste com proxy: {e}")
            results["error"] = str(e)
            
        finally:
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
        
        return results
    
    def diagnose_proxy_issues(self) -> Dict[str, Any]:
        """
        Executa diagnóstico completo de problemas relacionados ao proxy
        
        Returns:
            Dict com diagnóstico detalhado
        """
        diagnosis = {
            "timestamp": time.time(),
            "proxy_config": {
                "host": self.proxy_host,
                "port": self.proxy_port,
                "auth_configured": bool(self.proxy_username)
            },
            "tests": {}
        }
        
        logger.info("Iniciando diagnóstico de proxy...")
        
        # Teste 1: Conectividade básica com proxy
        logger.info("1. Testando conectividade básica com proxy...")
        proxy_test = self.test_proxy_connectivity()
        diagnosis["tests"]["proxy_connectivity"] = proxy_test
        
        if not proxy_test["proxy_connection_success"]:
            diagnosis["recommendation"] = "Verificar se proxy está acessível e porta está correta"
            return diagnosis
        
        # Teste 2: TLS através do proxy
        logger.info("2. Testando handshake TLS através do proxy...")
        tls_test = self.connect_and_test()
        diagnosis["tests"]["tls_through_proxy"] = tls_test
        
        # Análise e recomendações
        recommendations = []
        
        if not tls_test["connect_tunnel_success"]:
            recommendations.append("Verificar credenciais de autenticação do proxy")
            recommendations.append("Confirmar se proxy suporta método CONNECT")
        
        if tls_test["client_hello_sent"] and not tls_test.get("response_size"):
            recommendations.append("Proxy pode estar bloqueando tráfego TLS")
            recommendations.append("Verificar políticas de firewall do proxy")
        
        if tls_test.get("response_analysis", {}).get("type") == "HTTP":
            recommendations.append("Proxy retornou resposta HTTP - pode estar interceptando TLS")
            recommendations.append("Verificar configurações de SSL/TLS inspection no proxy")
        
        diagnosis["recommendations"] = recommendations
        
        return diagnosis


def create_proxy_client_from_config(config: Dict[str, Any]) -> ProxyTLSClient:
    """
    Cria cliente proxy a partir de configuração
    
    Args:
        config: Dicionário com configurações
                {
                    "target_host": "servidor.com",
                    "target_port": 443,
                    "proxy_host": "proxy.empresa.com", 
                    "proxy_port": 8080,
                    "proxy_username": "usuario",  # opcional
                    "proxy_password": "senha",    # opcional
                    "timeout": 30                 # opcional
                }
    
    Returns:
        Instância configurada de ProxyTLSClient
    """
    return ProxyTLSClient(
        host=config["target_host"],
        port=config["target_port"],
        proxy_host=config["proxy_host"],
        proxy_port=config["proxy_port"],
        proxy_username=config.get("proxy_username"),
        proxy_password=config.get("proxy_password"),
        timeout=config.get("timeout", 30)
    )


if __name__ == "__main__":
    # Exemplo de uso
    import json
    
    print("=== Proxy TLS Client - Exemplo de Uso ===\n")
    
    # Configuração de exemplo (ajustar conforme necessário)
    config = {
        "target_host": "www.google.com",
        "target_port": 443,
        "proxy_host": "proxy.empresa.com",  # Ajustar para proxy real
        "proxy_port": 8080,                 # Ajustar para porta real
        "proxy_username": "seu_usuario",    # Opcional
        "proxy_password": "sua_senha",      # Opcional
        "timeout": 15
    }
    
    print("Configuração:")
    print(json.dumps(config, indent=2))
    print()
    
    # Criar cliente
    client = create_proxy_client_from_config(config)
    
    # Executar diagnóstico completo
    print("Executando diagnóstico de proxy...")
    diagnosis = client.diagnose_proxy_issues()
    
    print("\nResultados do diagnóstico:")
    print(json.dumps(diagnosis, indent=2, default=str))
