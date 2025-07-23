#!/usr/bin/env python3
"""
Teste das capacidades de análise de resposta do TLS Raw Client
Demonstra como o cliente pode detectar e analisar diferentes tipos de resposta
"""

from tls_raw_client import TLSRawClient
import json

def test_response_analysis():
    """Testa a análise de diferentes tipos de resposta"""
    
    print("=== Teste de Análise de Resposta TLS Raw Client ===\n")
    
    # Criar cliente para teste
    client = TLSRawClient("www.google.com", 443)
    
    # Testar diferentes tipos de resposta simulados
    test_responses = [
        {
            "name": "TLS Server Hello Válido",
            "data": bytes.fromhex("160303003502000031030364ce8c09e0a0e8e4d77d1b51e9b2b8c1a1f8e2d3c4b5a69788b1a2c3d4e5f600130000090000000014000000")
        },
        {
            "name": "Resposta HTTP de Firewall",
            "data": b"HTTP/1.1 403 Forbidden\r\nServer: FortiGate-100D\r\nX-Blocked-By: Corporate Firewall\r\nContent-Type: text/html\r\n\r\n<html><body>Access Denied by Firewall</body></html>"
        },
        {
            "name": "Mensagem de Proxy",
            "data": b"HTTP/1.1 407 Proxy Authentication Required\r\nProxy-Authenticate: Basic realm=\"Corporate Proxy\"\r\nVia: 1.1 proxy.company.com\r\n\r\n"
        },
        {
            "name": "Banner SSH (porta errada)",
            "data": b"SSH-2.0-OpenSSH_7.4\r\n"
        },
        {
            "name": "Dados Binários Desconhecidos",
            "data": bytes([0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0] * 10)
        },
        {
            "name": "Mensagem de Firewall SonicWall",
            "data": b"HTTP/1.0 403 Forbidden\r\nServer: SonicWall\r\nContent-Type: text/html\r\n\r\n<html><head><title>Access Denied</title></head><body>This site has been blocked by your network administrator.</body></html>"
        }
    ]
    
    for test in test_responses:
        print(f"\n--- Testando: {test['name']} ---")
        print(f"Dados (primeiros 50 bytes): {test['data'][:50]}")
        print(f"Tamanho total: {len(test['data'])} bytes")
        
        # Analisar tipo de resposta
        analysis = client.analyze_response(test['data'])
        print(f"\nAnálise de Resposta:")
        print(f"  Tipo detectado: {analysis['type']}")
        print(f"  Fonte provável: {analysis['likely_source']}")
        print(f"  É TLS: {analysis['likely_tls']}")
        if analysis.get('details'):
            print(f"  Detalhes: {analysis['details']}")
        
        # Se não for TLS, extrair informações de firewall
        if not analysis['likely_tls']:
            firewall_info = client.extract_firewall_info(test['data'])
            if firewall_info:
                print(f"\nInformações de Firewall/Proxy:")
                for key, value in firewall_info.items():
                    print(f"  {key}: {value}")
        
        print("-" * 60)

def test_real_connection():
    """Testa conexão real para demonstrar funcionalidade"""
    
    print("\n\n=== Teste de Conexão Real ===\n")
    
    # Teste com servidor TLS normal
    print("1. Testando conexão TLS normal (www.google.com:443)...")
    client = TLSRawClient("www.google.com", 443, timeout=10)
    
    try:
        result = client.connect_and_test()
        print(f"Resultado da conexão:")
        print(f"  Sucesso da conexão: {result['connection_success']}")
        print(f"  Client Hello enviado: {result['client_hello_sent']}")
        print(f"  Tamanho da resposta: {result.get('response_size', 0)} bytes")
        
        if 'response_analysis' in result:
            analysis = result['response_analysis']
            print(f"  Tipo de resposta: {analysis['type']}")
            print(f"  Fonte: {analysis['likely_source']}")
        
        if 'server_response' in result and result['server_response']:
            response = result['server_response']
            if response.get('type') == 'Non-TLS Response':
                print(f"  Resposta não-TLS detectada!")
                if 'firewall_info' in response and response['firewall_info']:
                    print(f"  Informações de firewall:")
                    for key, value in response['firewall_info'].items():
                        print(f"    {key}: {value}")
            else:
                print(f"  TLS detectado - Tipo: {response.get('type', 'Unknown')}")
        
    except Exception as e:
        print(f"Erro na conexão: {e}")
    finally:
        client.close()
    
    # Teste com porta que provavelmente retornará erro
    print("\n2. Testando porta não-TLS (www.google.com:80)...")
    client_http = TLSRawClient("www.google.com", 80, timeout=5)
    
    try:
        result = client_http.connect_and_test()
        print(f"Resultado da conexão HTTP:")
        print(f"  Sucesso da conexão: {result['connection_success']}")
        print(f"  Client Hello enviado: {result['client_hello_sent']}")
        
        if 'response_analysis' in result:
            analysis = result['response_analysis']
            print(f"  Tipo de resposta: {analysis['type']}")
            print(f"  Fonte: {analysis['likely_source']}")
            
        if 'error' in result and result['error']:
            print(f"  Erro: {result['error']}")
            
    except Exception as e:
        print(f"Erro na conexão HTTP: {e}")
    finally:
        client_http.close()

if __name__ == "__main__":
    print("TLS Raw Client - Teste de Análise de Resposta")
    print("=" * 50)
    
    # Testar análise de diferentes tipos de resposta
    test_response_analysis()
    
    # Testar conexões reais
    test_real_connection()
    
    print("\n=== Teste Concluído ===")
    print("\nEste cliente agora pode:")
    print("✓ Detectar respostas TLS válidas")
    print("✓ Identificar mensagens de firewall HTTP")
    print("✓ Reconhecer respostas de proxy")
    print("✓ Extrair informações de marcas de firewall")
    print("✓ Analisar dados binários desconhecidos")
    print("✓ Capturar qualquer tipo de resposta para diagnóstico")
