#!/usr/bin/env python3
"""
TLS Raw Socket Client para diagnóstico de problemas de conectividade
Implementa Client Hello TLS 1.2/1.3 manualmente sem bibliotecas administrativas
"""

import socket
import struct
import time
import random
from typing import Optional, Dict, Any
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TLSRawClient:
    """Cliente TLS raw para diagnóstico de conectividade"""
    
    # Constantes TLS
    TLS_RECORD_TYPE_HANDSHAKE = 0x16
    TLS_HANDSHAKE_CLIENT_HELLO = 0x01
    TLS_VERSION_1_0 = 0x0301
    TLS_VERSION_1_2 = 0x0303
    TLS_VERSION_1_3 = 0x0304
    
    # Cipher Suites baseados no dump OpenSSL (ordem exata)
    CIPHER_SUITES = [
        0x1302,  # TLS_AES_256_GCM_SHA384 (TLS 1.3)
        0x1303,  # TLS_CHACHA20_POLY1305_SHA256 (TLS 1.3)  
        0x1301,  # TLS_AES_128_GCM_SHA256 (TLS 1.3)
        0xc02c,  # TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
        0xc030,  # TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
        0x009f,  # TLS_DHE_RSA_WITH_AES_256_GCM_SHA384
        0xcca9,  # TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
        0xcca8,  # TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
        0xccaa,  # TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256
        0xc02b,  # TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
        0xc02f,  # TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
        0x009e,  # TLS_DHE_RSA_WITH_AES_128_GCM_SHA256
        0xc024,  # TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384
        0xc028,  # TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384
        0x006b,  # TLS_DHE_RSA_WITH_AES_256_CBC_SHA256
        0xc023,  # TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256
        0xc027,  # TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256
        0x0067,  # TLS_DHE_RSA_WITH_AES_128_CBC_SHA256
        0xc00a,  # TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA
        0xc014,  # TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
        0x0039,  # TLS_DHE_RSA_WITH_AES_256_CBC_SHA
        0xc009,  # TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA
        0xc013,  # TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
        0x0033,  # TLS_DHE_RSA_WITH_AES_128_CBC_SHA
        0x009d,  # TLS_RSA_WITH_AES_256_GCM_SHA384
        0x009c,  # TLS_RSA_WITH_AES_128_GCM_SHA256
        0x003d,  # TLS_RSA_WITH_AES_256_CBC_SHA256
        0x003c,  # TLS_RSA_WITH_AES_128_CBC_SHA256
        0x0035,  # TLS_RSA_WITH_AES_256_CBC_SHA
        0x002f,  # TLS_RSA_WITH_AES_128_CBC_SHA
        0x00ff,  # TLS_EMPTY_RENEGOTIATION_INFO_SCSV
    ]
    
    def __init__(self, host: str, port: int = 443, timeout: float = 10.0):
        """
        Inicializa o cliente TLS raw
        
        Args:
            host: Hostname ou IP do servidor
            port: Porta do servidor (padrão 443)
            timeout: Timeout para conexões em segundos
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        
    def generate_random_bytes(self, length: int) -> bytes:
        """Gera bytes aleatórios"""
        return bytes(random.getrandbits(8) for _ in range(length))
    
    def create_client_hello(self, server_name: Optional[str] = None) -> bytes:
        """
        Cria um Client Hello TLS manual baseado no formato OpenSSL
        
        Args:
            server_name: Nome do servidor para SNI (Server Name Indication)
            
        Returns:
            bytes: Client Hello completo como bytes
        """
        logger.info("Construindo Client Hello TLS...")
        
        # Random de 32 bytes (como no dump do OpenSSL)
        client_random = self.generate_random_bytes(32)
        
        # Session ID com 32 bytes (como no dump OpenSSL)
        session_id = self.generate_random_bytes(32)
        
        # Cipher Suites baseados no dump OpenSSL
        cipher_suites_data = b''.join(
            suite.to_bytes(2, 'big') for suite in self.CIPHER_SUITES
        )
        
        # Compression Methods (null compression)
        compression_methods = b'\x00'
        
        # Extensions baseadas no dump
        extensions = self._create_extensions(server_name)
        
        # Construir Client Hello (formato correto)
        client_hello = b''
        
        # TLS Version (0x0303 para TLS 1.2)
        client_hello += struct.pack('!H', self.TLS_VERSION_1_2)
        
        # Client Random (32 bytes)
        client_hello += client_random
        
        # Session ID Length + Session ID
        client_hello += struct.pack('!B', len(session_id))
        client_hello += session_id
        
        # Cipher Suites Length + Cipher Suites
        client_hello += struct.pack('!H', len(cipher_suites_data))
        client_hello += cipher_suites_data
        
        # Compression Methods Length + Compression Methods
        client_hello += struct.pack('!B', len(compression_methods))
        client_hello += compression_methods
        
        # Extensions Length + Extensions
        if extensions:
            client_hello += struct.pack('!H', len(extensions))
            client_hello += extensions
        
        # Wrap em TLS Handshake (3 bytes para length)
        handshake_length = len(client_hello)
        handshake = struct.pack('!B', self.TLS_HANDSHAKE_CLIENT_HELLO)
        handshake += struct.pack('!L', handshake_length)[1:]  # 3 bytes de length
        handshake += client_hello
        
        # Wrap em TLS Record
        record = struct.pack(
            '!BHH',
            self.TLS_RECORD_TYPE_HANDSHAKE,
            0x0301,  # TLS 1.0 no record header como no OpenSSL
            len(handshake)
        )
        record += handshake
        
        logger.info(f"Client Hello criado: {len(record)} bytes")
        return record
    
    def _create_extensions(self, server_name: Optional[str] = None) -> bytes:
        """Cria extensions para o Client Hello baseadas no dump OpenSSL"""
        extensions = b''
        
        # Server Name Indication (SNI) - Extension 0x0000
        if server_name:
            sni_data = struct.pack('!BH', 0, len(server_name)) + server_name.encode('utf-8')
            sni_list = struct.pack('!H', len(sni_data)) + sni_data
            sni_ext = struct.pack('!HH', 0x0000, len(sni_list)) + sni_list
            extensions += sni_ext
        
        # EC Point Formats - Extension 0x000b
        ec_formats = b'\x03\x00\x01\x02'  # uncompressed, ansiX962_compressed_prime, ansiX962_compressed_char2
        ec_ext = struct.pack('!HH', 0x000b, len(ec_formats)) + ec_formats
        extensions += ec_ext
        
        # Supported Groups (Elliptic Curves) - Extension 0x000a  
        supported_groups = [
            0x001d,  # x25519
            0x0017,  # secp256r1
            0x001e,  # x448
            0x0019,  # secp521r1
            0x0018,  # secp384r1
            0x0100,  # ffdhe2048
            0x0101,  # ffdhe3072
            0x0102,  # ffdhe4096
            0x0103,  # ffdhe6144
            0x0104,  # ffdhe8192
        ]
        groups_data = b''.join(group.to_bytes(2, 'big') for group in supported_groups)
        groups_ext = struct.pack('!HHH', 0x000a, len(groups_data) + 2, len(groups_data))
        groups_ext += groups_data
        extensions += groups_ext
        
        # Session Ticket - Extension 0x0023 (empty)
        extensions += struct.pack('!HH', 0x0023, 0)
        
        # Encrypt-then-MAC - Extension 0x0016 (empty)
        extensions += struct.pack('!HH', 0x0016, 0)
        
        # Extended Master Secret - Extension 0x0017 (empty)
        extensions += struct.pack('!HH', 0x0017, 0)
        
        # Signature Algorithms - Extension 0x000d
        sig_algs = [
            0x0403,  # ecdsa_secp256r1_sha256
            0x0503,  # ecdsa_secp384r1_sha384
            0x0603,  # ecdsa_secp521r1_sha512
            0x0807,  # ed25519
            0x0808,  # ed448
            0x0809,  # rsa_pss_pss_sha256
            0x080a,  # rsa_pss_pss_sha384
            0x080b,  # rsa_pss_pss_sha512
            0x0804,  # rsa_pss_rsae_sha256
            0x0805,  # rsa_pss_rsae_sha384
            0x0806,  # rsa_pss_rsae_sha512
            0x0401,  # rsa_pkcs1_sha256
            0x0501,  # rsa_pkcs1_sha384
            0x0601,  # rsa_pkcs1_sha512
            0x0303,  # ecdsa_sha224
            0x0301,  # ecdsa_sha1
            0x0302,  # rsa_pkcs1_sha224
            0x0402,  # rsa_pkcs1_sha256 (duplicate?)
            0x0502,  # rsa_pkcs1_sha384 (duplicate?)
            0x0602,  # rsa_pkcs1_sha512 (duplicate?)
        ]
        sig_data = b''.join(alg.to_bytes(2, 'big') for alg in sig_algs)
        sig_ext = struct.pack('!HHH', 0x000d, len(sig_data) + 2, len(sig_data))
        sig_ext += sig_data
        extensions += sig_ext
        
        # Supported Versions - Extension 0x002b (TLS 1.3, 1.2)
        versions = [0x0304, 0x0303]  # TLS 1.3, TLS 1.2
        versions_data = struct.pack('!B', len(versions) * 2)
        versions_data += b''.join(v.to_bytes(2, 'big') for v in versions)
        versions_ext = struct.pack('!HH', 0x002b, len(versions_data)) + versions_data
        extensions += versions_ext
        
        # PSK Key Exchange Modes - Extension 0x002d
        psk_modes = b'\x01\x01'  # psk_dhe_ke
        psk_ext = struct.pack('!HH', 0x002d, len(psk_modes)) + psk_modes
        extensions += psk_ext
        
        # Key Share - Extension 0x0033
        # x25519 key share (32 bytes)
        key_share_data = struct.pack('!HH', 0x001d, 32)  # x25519, 32 bytes
        key_share_data += self.generate_random_bytes(32)  # random key
        key_shares = struct.pack('!H', len(key_share_data)) + key_share_data
        key_share_ext = struct.pack('!HH', 0x0033, len(key_shares)) + key_shares
        extensions += key_share_ext
        
        return extensions
    
    def analyze_response(self, data: bytes) -> Dict[str, Any]:
        """
        Analisa qualquer resposta recebida para identificar o tipo
        
        Args:
            data: Dados brutos recebidos
            
        Returns:
            Dict com análise da resposta
        """
        analysis = {
            "likely_tls": False,
            "detected_type": "Unknown",
            "likely_source": "Unknown",
            "preview": "",
            "raw_hex": data.hex()[:100] + "..." if len(data) > 50 else data.hex()
        }
        
        if len(data) == 0:
            analysis["detected_type"] = "Empty Response"
            analysis["likely_source"] = "Connection closed immediately"
            return analysis
        
        # Verificar se é TLS válido
        if len(data) >= 5:
            record_type = data[0]
            version = struct.unpack('!H', data[1:3])[0]
            length = struct.unpack('!H', data[3:5])[0]
            
            # TLS record types válidos
            valid_tls_types = [0x14, 0x15, 0x16, 0x17, 0x18]
            valid_tls_versions = [0x0301, 0x0302, 0x0303, 0x0304]  # TLS 1.0-1.3
            
            if (record_type in valid_tls_types and 
                version in valid_tls_versions and 
                length > 0 and length < 65536):
                analysis["likely_tls"] = True
                analysis["detected_type"] = "TLS Record"
                analysis["likely_source"] = "TLS Server"
                return analysis
        
        # Verificar se é HTTP
        try:
            text = data.decode('utf-8', errors='ignore')[:200]
            analysis["preview"] = text
            
            if text.startswith(('HTTP/', 'html', '<!DOCTYPE', '<html')):
                analysis["detected_type"] = "HTTP Response"
                analysis["likely_source"] = "HTTP Server/Proxy"
                
                # Detectar tipos específicos de HTTP
                if 'blocked' in text.lower() or 'forbidden' in text.lower():
                    analysis["likely_source"] = "Firewall/Content Filter (HTTP)"
                elif 'proxy' in text.lower():
                    analysis["likely_source"] = "Proxy Server"
                elif '407' in text or 'Proxy Authentication' in text:
                    analysis["likely_source"] = "Proxy Authentication Required"
                    
            elif text.startswith('SSH-'):
                analysis["detected_type"] = "SSH Banner"
                analysis["likely_source"] = "SSH Server"
                
            elif 'FTP' in text and ('220' in text or '421' in text):
                analysis["detected_type"] = "FTP Response" 
                analysis["likely_source"] = "FTP Server"
                
            elif any(word in text.lower() for word in ['firewall', 'blocked', 'denied', 'unauthorized']):
                analysis["detected_type"] = "Firewall Message"
                analysis["likely_source"] = "Corporate Firewall"
                
            else:
                analysis["detected_type"] = "Text Response"
                analysis["likely_source"] = "Unknown Text Server"
                
        except UnicodeDecodeError:
            # Dados binários não-texto
            pass
        
        # Verificar padrões binários específicos
        if not analysis["detected_type"] or analysis["detected_type"] == "Unknown":
            
            # Verificar se é uma resposta de proxy CONNECT
            if data.startswith(b'HTTP/1.1 200') or data.startswith(b'HTTP/1.0 200'):
                analysis["detected_type"] = "HTTP CONNECT Success"
                analysis["likely_source"] = "Proxy Server"
                
            elif data.startswith(b'HTTP/1.1 407') or data.startswith(b'HTTP/1.0 407'):
                analysis["detected_type"] = "Proxy Authentication Required"
                analysis["likely_source"] = "Proxy Server"
                
            # Padrões específicos de firewall
            elif len(data) < 10 and all(b == 0 for b in data):
                analysis["detected_type"] = "Null Response"
                analysis["likely_source"] = "Firewall (Silent Drop with Null)"
                
            elif data == b'\x00' * len(data):
                analysis["detected_type"] = "Zero-filled Response"
                analysis["likely_source"] = "Firewall/IDS (Padding Response)"
                
            # Verificar se é SOCKS response
            elif len(data) >= 2 and data[0] == 0x05:
                analysis["detected_type"] = "SOCKS5 Response"
                analysis["likely_source"] = "SOCKS Proxy"
                
            else:
                analysis["detected_type"] = "Binary Data"
                analysis["likely_source"] = "Unknown Binary Protocol"
                
                # Análise de entropia para detectar dados suspeitos
                if len(data) > 10:
                    unique_bytes = len(set(data))
                    entropy_ratio = unique_bytes / len(data)
                    
                    if entropy_ratio < 0.1:  # Dados muito repetitivos
                        analysis["likely_source"] = "Firewall (Low Entropy Response)"
                    elif entropy_ratio > 0.9:  # Dados muito aleatórios
                        analysis["likely_source"] = "Possible Encrypted/Random Data"
        
        return analysis
    
    def extract_firewall_info(self, data: bytes) -> Dict[str, str]:
        """
        Extrai informações úteis de respostas de firewall/proxy
        
        Args:
            data: Dados brutos da resposta
            
        Returns:
            Dict com informações extraídas
        """
        info = {}
        
        try:
            # Tentar decodificar como texto
            text = data.decode('utf-8', errors='ignore')
            
            # Procurar por headers HTTP úteis
            if 'HTTP/' in text:
                lines = text.split('\n')
                for line in lines[:10]:  # Primeiras 10 linhas
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        # Headers interessantes
                        if key in ['server', 'x-forwarded-by', 'via', 'x-firewall', 
                                 'x-blocked-by', 'x-proxy', 'location']:
                            info[key] = value
            
            # Procurar por palavras-chave de firewall
            firewall_keywords = [
                'firewall', 'blocked', 'denied', 'forbidden', 'unauthorized',
                'filtered', 'proxy', 'gateway', 'security', 'violation'
            ]
            
            found_keywords = []
            for keyword in firewall_keywords:
                if keyword in text.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                info['firewall_keywords'] = ', '.join(found_keywords)
            
            # Extrair possível nome/marca do firewall
            firewall_brands = [
                'fortigate', 'palo alto', 'checkpoint', 'cisco', 'juniper',
                'sonicwall', 'watchguard', 'barracuda', 'f5', 'bluecoat',
                'websense', 'symantec', 'mcafee', 'trend micro'
            ]
            
            for brand in firewall_brands:
                if brand in text.lower():
                    info['firewall_brand'] = brand
                    break
                    
        except Exception as e:
            info['extraction_error'] = str(e)
        
        return info
    
    def parse_tls_record(self, data: bytes) -> Dict[str, Any]:
        """
        Parse de um record TLS
        
        Args:
            data: Dados do record TLS
            
        Returns:
            Dict com informações parseadas
        """
        if len(data) < 5:
            return {"error": "Dados insuficientes para TLS record"}
        
        record_type = data[0]
        version = struct.unpack('!H', data[1:3])[0]
        length = struct.unpack('!H', data[3:5])[0]
        
        record_types = {
            0x14: "Change Cipher Spec",
            0x15: "Alert",
            0x16: "Handshake", 
            0x17: "Application Data"
        }
        
        result = {
            "type": record_types.get(record_type, f"Unknown ({record_type})"),
            "version": f"{version >> 8}.{version & 0xFF}",
            "length": length,
            "payload": data[5:5+length] if len(data) >= 5+length else data[5:]
        }
        
        # Parse específico para handshake
        if record_type == 0x16 and len(result["payload"]) >= 4:
            handshake_type = result["payload"][0]
            handshake_length = struct.unpack('!L', b'\x00' + result["payload"][1:4])[0]
            
            handshake_types = {
                0x00: "Hello Request",
                0x01: "Client Hello",
                0x02: "Server Hello",
                0x0b: "Certificate",
                0x0c: "Server Key Exchange",
                0x0d: "Certificate Request",
                0x0e: "Server Hello Done",
                0x0f: "Certificate Verify",
                0x10: "Client Key Exchange",
                0x14: "Finished"
            }
            
            result["handshake_type"] = handshake_types.get(
                handshake_type, f"Unknown ({handshake_type})"
            )
            result["handshake_length"] = handshake_length
        
        # Parse específico para alert
        elif record_type == 0x15 and len(result["payload"]) >= 2:
            alert_level = result["payload"][0]
            alert_desc = result["payload"][1]
            
            alert_levels = {1: "Warning", 2: "Fatal"}
            alert_descriptions = {
                0: "close_notify",
                10: "unexpected_message",
                20: "bad_record_mac",
                21: "decryption_failed",
                22: "record_overflow",
                30: "decompression_failure",
                40: "handshake_failure",
                41: "no_certificate",
                42: "bad_certificate",
                43: "unsupported_certificate",
                44: "certificate_revoked",
                45: "certificate_expired",
                46: "certificate_unknown",
                47: "illegal_parameter",
                48: "unknown_ca",
                49: "access_denied",
                50: "decode_error",
                51: "decrypt_error",
                70: "protocol_version",
                71: "insufficient_security",
                80: "internal_error",
                90: "user_canceled",
                100: "no_renegotiation"
            }
            
            result["alert_level"] = alert_levels.get(alert_level, f"Unknown ({alert_level})")
            result["alert_description"] = alert_descriptions.get(
                alert_desc, f"Unknown ({alert_desc})"
            )
        
        return result
    
    def connect_and_test(self, use_sni: bool = True) -> Dict[str, Any]:
        """
        Conecta ao servidor e testa o handshake TLS
        
        Args:
            use_sni: Se deve usar SNI (Server Name Indication)
            
        Returns:
            Dict com resultados do teste
        """
        results = {
            "timestamp": time.time(),
            "host": self.host,
            "port": self.port,
            "connection_success": False,
            "client_hello_sent": False,
            "server_response": None,
            "error": None,
            "raw_response": None
        }
        
        try:
            logger.info(f"Tentando conectar em {self.host}:{self.port}")
            
            # Criar socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            
            # Conectar
            start_time = time.time()
            self.socket.connect((self.host, self.port))
            connect_time = time.time() - start_time
            
            logger.info(f"Conexão TCP estabelecida em {connect_time:.3f}s")
            results["connection_success"] = True
            results["connect_time"] = connect_time
            
            # Criar e enviar Client Hello
            server_name = self.host if use_sni else None
            client_hello = self.create_client_hello(server_name)
            
            logger.info(f"Enviando Client Hello ({len(client_hello)} bytes)...")
            logger.debug(f"Client Hello hex: {client_hello.hex()}")
            
            self.socket.send(client_hello)
            results["client_hello_sent"] = True
            results["client_hello_size"] = len(client_hello)
            
            # Tentar receber resposta
            logger.info("Aguardando resposta do servidor...")
            
            try:
                response = self.socket.recv(4096)
                if response:
                    logger.info(f"Resposta recebida: {len(response)} bytes")
                    logger.debug(f"Resposta hex: {response.hex()}")
                    
                    results["raw_response"] = response.hex()
                    results["response_size"] = len(response)
                    results["raw_response_bytes"] = response  # Buffer bruto para análise
                    
                    # Tentar identificar o tipo de resposta
                    response_analysis = self.analyze_response(response)
                    results["response_analysis"] = response_analysis
                    
                    # Se parecer TLS, fazer parse TLS
                    if response_analysis["likely_tls"]:
                        parsed = self.parse_tls_record(response)
                        results["server_response"] = parsed
                        
                        logger.info(f"Tipo de resposta TLS: {parsed.get('type', 'Unknown')}")
                        
                        if "handshake_type" in parsed:
                            logger.info(f"Handshake type: {parsed['handshake_type']}")
                        
                        if "alert_level" in parsed:
                            logger.warning(f"Alert recebido: {parsed['alert_level']} - {parsed['alert_description']}")
                    else:
                        # Resposta não-TLS (possível firewall/proxy)
                        logger.warning(f"Resposta não-TLS detectada: {response_analysis['detected_type']}")
                        logger.warning(f"Possível origem: {response_analysis['likely_source']}")
                        
                        # Extrair informações detalhadas de firewall/proxy
                        firewall_info = self.extract_firewall_info(response)
                        
                        results["server_response"] = {
                            "type": "Non-TLS Response",
                            "detected_type": response_analysis["detected_type"],
                            "likely_source": response_analysis["likely_source"],
                            "preview": response_analysis["preview"],
                            "firewall_info": firewall_info
                        }
                        
                        # Log informações de firewall se encontradas
                        if firewall_info:
                            logger.info("Informações de firewall/proxy detectadas:")
                            for key, value in firewall_info.items():
                                logger.info(f"  {key}: {value}")
                
                else:
                    logger.warning("Conexão fechada pelo servidor sem resposta")
                    results["error"] = "Conexão fechada sem resposta"
                    
            except socket.timeout:
                logger.error("Timeout aguardando resposta do servidor")
                results["error"] = "Timeout na resposta"
                
            except ConnectionResetError:
                logger.error("Conexão resetada pelo servidor")
                results["error"] = "Conexão resetada"
                
        except socket.gaierror as e:
            logger.error(f"Erro de resolução DNS: {e}")
            results["error"] = f"DNS Error: {e}"
            
        except ConnectionRefusedError:
            logger.error("Conexão recusada pelo servidor")
            results["error"] = "Conexão recusada"
            
        except socket.timeout:
            logger.error("Timeout na conexão")
            results["error"] = "Timeout na conexão"
            
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            results["error"] = f"Erro inesperado: {e}"
            
        finally:
            if self.socket:
                self.socket.close()

        log_response(results)

        return results


def log_response(results: Dict[str, Any]):
    print(f"Conexão TCP: {'✓' if results['connection_success'] else '✗'}")
    if results.get('connect_time'):
        print(f"Tempo de conexão: {results['connect_time']:.3f}s")
        
    print(f"Client Hello enviado: {'✓' if results['client_hello_sent'] else '✗'}")
    if results.get('client_hello_size'):
        print(f"Tamanho Client Hello: {results['client_hello_size']} bytes")
    
    if results['server_response']:
        resp = results['server_response']
        print(f"Resposta do servidor: {resp['type']}")
        if 'handshake_type' in resp:
            print(f"Handshake Type: {resp['handshake_type']}")
        if 'alert_level' in resp:
            print(f"Alert: {resp['alert_level']} - {resp['alert_description']}")
            
    if results['error']:
        print(f"Erro: {results['error']}")
        
    if results.get('raw_response_bytes'):
        print("Resposta raw (hex+ascii):")
        print(hexdump(results['raw_response_bytes'], 32))
    elif results.get('raw_response'):
        print(f"Resposta raw (hex): {results['raw_response']}")

def hexdump(data: bytes, width: int = 16) -> str:
    """
    Gera um dump hex+ascii similar ao hexdump clássico.
    """
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_bytes = ' '.join(f"{b:02x}" for b in chunk)
        ascii_bytes = ''.join((chr(b) if 32 <= b < 127 else '.') for b in chunk)
        lines.append(f"{i:08x}  {hex_bytes:<{width*3}}  {ascii_bytes}")
    return '\n'.join(lines)


def main():
    """Função principal para testes"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cliente TLS Raw para diagnóstico")
    parser.add_argument("host", help="Hostname ou IP do servidor")
    parser.add_argument("-p", "--port", type=int, default=443, help="Porta (padrão: 443)")
    parser.add_argument("-t", "--timeout", type=float, default=10.0, help="Timeout em segundos")
    parser.add_argument("--no-sni", action="store_true", help="Desabilitar SNI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Logging verboso")
    parser.add_argument("--repeat", type=int, default=1, help="Número de tentativas")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    client = TLSRawClient(args.host, args.port, args.timeout)
    
    print(f"=== Teste TLS Raw para {args.host}:{args.port} ===")
    print(f"SNI: {'Desabilitado' if args.no_sni else 'Habilitado'}")
    print(f"Timeout: {args.timeout}s")
    print(f"Tentativas: {args.repeat}")
    print()
    
    for i in range(args.repeat):
        if args.repeat > 1:
            print(f"--- Tentativa {i+1}/{args.repeat} ---")
        
        client.connect_and_test(use_sni=not args.no_sni)
        
        if i < args.repeat - 1:
            time.sleep(1)  # Pausa entre tentativas
    
    print("=== Fim do teste ===")


if __name__ == "__main__":
    main()
