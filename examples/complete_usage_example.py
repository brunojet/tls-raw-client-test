#!/usr/bin/env python3
"""
Exemplo completo de uso do TLS Raw Client
Demonstra diferentes cenários de uso e configurações
"""

import json
import logging
from tls_raw_client import TLSRawClient
from proxy_tls_client import ProxyTLSClient
from firewall_diagnostic import FirewallDiagnosticClient

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def example_basic_tls():
    """Exemplo 1: Cliente TLS básico"""
    print("\n🔹 Exemplo 1: Cliente TLS Básico")
    print("=" * 40)
    
    # Teste básico com Google
    client = TLSRawClient("www.google.com", 443, timeout=10)
    result = client.connect_and_test()
    
    print(f"Host: {result['host']}:{result['port']}")
    print(f"Conexão TCP: {'✅' if result['connection_success'] else '❌'}")
    print(f"Client Hello enviado: {'✅' if result['client_hello_sent'] else '❌'}")
    
    if result.get('response_analysis'):
        analysis = result['response_analysis']
        print(f"Tipo de resposta: {analysis['type']}")
        print(f"Fonte: {analysis['likely_source']}")
    
    if result.get('error'):
        print(f"Erro: {result['error']}")

def example_proxy_basic():
    """Exemplo 2: Proxy sem autenticação"""
    print("\n🔹 Exemplo 2: Proxy Básico (sem autenticação)")
    print("=" * 50)
    
    # Configuração de proxy básico
    try:
        client = ProxyTLSClient(
            host="www.github.com",
            port=443,
            proxy_host="proxy.empresa.com",  # Substitua pelo seu proxy
            proxy_port=8080,
            timeout=15
        )
        
        print("⚠️ Usando configuração de exemplo - ajuste para seu ambiente")
        print("Configuração:")
        print(f"  Target: {client.host}:{client.port}")
        print(f"  Proxy: {client.proxy_host}:{client.proxy_port}")
        print(f"  Auth: Não")
        
        # Teste apenas conectividade (sem enviar dados reais)
        print("\n📝 Para teste real, ajuste as configurações de proxy")
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")

def example_proxy_with_auth():
    """Exemplo 3: Proxy com autenticação"""
    print("\n🔹 Exemplo 3: Proxy com Autenticação")
    print("=" * 42)
    
    # Configuração de proxy com autenticação
    config = {
        "target_host": "api.github.com",
        "target_port": 443,
        "proxy_host": "proxy.corp.com",
        "proxy_port": 3128,
        "proxy_username": "DOMAIN\\usuario",
        "proxy_password": "senha_aqui",
        "timeout": 30
    }
    
    print("Configuração de exemplo:")
    print(json.dumps({**config, "proxy_password": "***"}, indent=2))
    print("\n📝 Substitua pelos valores reais do seu ambiente")

def example_config_file():
    """Exemplo 4: Carregamento via arquivo de configuração"""
    print("\n🔹 Exemplo 4: Configuração via Arquivo")
    print("=" * 43)
    
    try:
        # Tentar carregar configuração de exemplo
        client = ProxyTLSClient.from_config_file("configs/proxy_basic.json")
        
        print("✅ Configuração carregada de: configs/proxy_basic.json")
        print(f"Target: {client.host}:{client.port}")
        print(f"Proxy: {client.proxy_host}:{client.proxy_port}")
        print(f"Auth: {'Sim' if client.proxy_username else 'Não'}")
        
        # Mostrar configurações disponíveis
        configs = client.list_available_configs()
        if configs:
            print(f"\n📁 Configurações disponíveis:")
            for filename, path in configs.items():
                print(f"  • {filename}")
        
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        print("💡 Crie arquivos de configuração em configs/ ou use proxy_setup_utility.py")

def example_firewall_diagnostic():
    """Exemplo 5: Diagnóstico de firewall"""
    print("\n🔹 Exemplo 5: Diagnóstico de Firewall")
    print("=" * 44)
    
    # Diagnóstico específico de firewall
    client = FirewallDiagnosticClient("blocked-site.example.com", 443)
    
    print("🛡️ Cliente de diagnóstico de firewall criado")
    print(f"Target: {client.host}:{client.port}")
    print("\n📝 Este cliente é otimizado para detectar bloqueios de firewall")
    print("   Inclui testes específicos para ambientes corporativos")

def example_response_analysis():
    """Exemplo 6: Análise de diferentes tipos de resposta"""
    print("\n🔹 Exemplo 6: Análise de Tipos de Resposta")
    print("=" * 47)
    
    client = TLSRawClient("example.com", 443)
    
    # Simular diferentes tipos de resposta
    test_responses = [
        {
            "name": "TLS Server Hello",
            "data": bytes.fromhex("160303003502000031030364ce8c09e0"),
            "expected": "TLS Record"
        },
        {
            "name": "HTTP Firewall Block",
            "data": b"HTTP/1.1 403 Forbidden\r\nServer: FortiGate\r\n\r\n",
            "expected": "HTTP Response"
        },
        {
            "name": "Proxy Auth Required",
            "data": b"HTTP/1.1 407 Proxy Authentication Required\r\n\r\n",
            "expected": "Proxy Authentication Required"
        }
    ]
    
    for test in test_responses:
        print(f"\n🔍 Analisando: {test['name']}")
        analysis = client.analyze_response(test['data'])
        print(f"   Tipo detectado: {analysis['type']}")
        print(f"   Fonte: {analysis['likely_source']}")
        print(f"   É TLS: {analysis['likely_tls']}")
        
        # Extrair informações de firewall se não for TLS
        if not analysis['likely_tls']:
            firewall_info = client.extract_firewall_info(test['data'])
            if firewall_info:
                print(f"   Firewall info: {firewall_info}")

def example_lambda_config():
    """Exemplo 7: Configuração para AWS Lambda"""
    print("\n🔹 Exemplo 7: Configuração AWS Lambda")
    print("=" * 42)
    
    # Exemplo de event para Lambda
    lambda_event = {
        "test_type": "full",
        "proxy_config": {
            "target_host": "api.externa.com",
            "target_port": 443,
            "proxy_host": "proxy.empresa.com",
            "proxy_port": 8080,
            "proxy_username": "lambda_service",
            "proxy_password": "service_password",
            "timeout": 45
        }
    }
    
    print("📦 Exemplo de event para AWS Lambda:")
    print(json.dumps({
        **lambda_event,
        "proxy_config": {
            **lambda_event["proxy_config"],
            "proxy_password": "***"
        }
    }, indent=2))
    
    print("\n🔧 Variáveis de ambiente suportadas:")
    env_vars = [
        "TARGET_HOST", "TARGET_PORT", "PROXY_HOST", "PROXY_PORT",
        "PROXY_USERNAME", "PROXY_PASSWORD", "PROXY_TIMEOUT"
    ]
    for var in env_vars:
        print(f"   • {var}")

def show_troubleshooting_tips():
    """Dicas de troubleshooting"""
    print("\n🔹 Dicas de Troubleshooting")
    print("=" * 32)
    
    tips = [
        {
            "problema": "Connection refused",
            "solução": "Verificar host/porta, conectividade de rede"
        },
        {
            "problema": "Timeout na conexão",
            "solução": "Aumentar timeout, verificar firewall/proxy"
        },
        {
            "problema": "407 Proxy Authentication",
            "solução": "Verificar credenciais, formato domain\\user"
        },
        {
            "problema": "Resposta HTTP em vez de TLS",
            "solução": "Proxy com SSL inspection ativo"
        },
        {
            "problema": "Conexão fecha após Client Hello",
            "solução": "Firewall bloqueando, cipher suites incompatíveis"
        }
    ]
    
    for tip in tips:
        print(f"\n❌ {tip['problema']}")
        print(f"   💡 {tip['solução']}")

def main():
    """Função principal - executa todos os exemplos"""
    print("🚀 TLS Raw Client - Exemplos de Uso Completos")
    print("=" * 50)
    print("Este script demonstra diferentes formas de usar o sistema")
    print("Ajuste as configurações conforme seu ambiente\n")
    
    # Executar exemplos
    example_basic_tls()
    example_proxy_basic()
    example_proxy_with_auth()
    example_config_file()
    example_firewall_diagnostic()
    example_response_analysis()
    example_lambda_config()
    show_troubleshooting_tips()
    
    print("\n" + "=" * 50)
    print("✅ Exemplos concluídos!")
    print("\n📚 Próximos passos:")
    print("1. Ajuste configurações para seu ambiente")
    print("2. Use proxy_setup_utility.py para configuração interativa")
    print("3. Teste com seus servidores/proxies reais")
    print("4. Veja docs/PROXY_README.md para documentação completa")
    print("\n🔧 Utilitários disponíveis:")
    print("• python proxy_setup_utility.py --interactive")
    print("• python tests/test_response_analysis.py")
    print("• python compare_openssl.py --host exemplo.com")

if __name__ == "__main__":
    main()
