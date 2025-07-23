#!/usr/bin/env python3
"""
Teste do Proxy TLS Client - Demonstra uso em ambiente corporativo
"""

import json
import logging
from proxy_tls_client import create_proxy_client_from_config

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_proxy_configurations():
    """Testa diferentes configurações de proxy"""
    
    print("=== Teste de Configurações de Proxy ===\n")
    
    # Configurações de teste (adaptar conforme necessário)
    test_configs = [
        {
            "name": "Proxy sem autenticação",
            "config": {
                "target_host": "www.google.com",
                "target_port": 443,
                "proxy_host": "proxy.empresa.com",
                "proxy_port": 8080,
                "timeout": 10
            }
        },
        {
            "name": "Proxy com autenticação",
            "config": {
                "target_host": "www.github.com", 
                "target_port": 443,
                "proxy_host": "proxy.empresa.com",
                "proxy_port": 8080,
                "proxy_username": "usuario_corporativo",
                "proxy_password": "senha_corporativa",
                "timeout": 15
            }
        },
        {
            "name": "Proxy alternativo (porta 3128)",
            "config": {
                "target_host": "api.github.com",
                "target_port": 443,
                "proxy_host": "proxy2.empresa.com",
                "proxy_port": 3128,
                "proxy_username": "usuario",
                "proxy_password": "senha",
                "timeout": 20
            }
        }
    ]
    
    for test in test_configs:
        print(f"\n--- {test['name']} ---")
        print(f"Configuração: {json.dumps(test['config'], indent=2)}")
        
        try:
            # Criar cliente
            client = create_proxy_client_from_config(test['config'])
            
            # Testar conectividade básica do proxy
            print("\n1. Testando conectividade com proxy...")
            proxy_test = client.test_proxy_connectivity()
            
            print(f"Conexão proxy: {'✓' if proxy_test['proxy_connection_success'] else '✗'}")
            if proxy_test.get('proxy_connect_time'):
                print(f"Tempo de conexão: {proxy_test['proxy_connect_time']:.3f}s")
            if proxy_test.get('error'):
                print(f"Erro: {proxy_test['error']}")
            
            # Se conectividade básica funcionou, testar TLS
            if proxy_test['proxy_connection_success']:
                print("\n2. Testando TLS através do proxy...")
                tls_result = client.connect_and_test()
                
                print(f"Túnel proxy: {'✓' if tls_result['connect_tunnel_success'] else '✗'}")
                print(f"Client Hello enviado: {'✓' if tls_result['client_hello_sent'] else '✗'}")
                print(f"Resposta recebida: {tls_result.get('response_size', 0)} bytes")
                
                if 'response_analysis' in tls_result:
                    analysis = tls_result['response_analysis']
                    print(f"Tipo de resposta: {analysis['type']}")
                    print(f"Fonte: {analysis['likely_source']}")
                
                if tls_result.get('error'):
                    print(f"Erro TLS: {tls_result['error']}")
            
        except Exception as e:
            print(f"Erro no teste: {e}")
        
        print("-" * 60)

def demonstrate_proxy_diagnosis():
    """Demonstra diagnóstico completo de proxy"""
    
    print("\n\n=== Diagnóstico Completo de Proxy ===\n")
    
    # Configuração para diagnóstico (ajustar conforme necessário)
    config = {
        "target_host": "www.microsoft.com",
        "target_port": 443,
        "proxy_host": "proxy.empresa.com",
        "proxy_port": 8080,
        "proxy_username": "usuario_teste",
        "proxy_password": "senha_teste",
        "timeout": 15
    }
    
    print("Configuração para diagnóstico:")
    print(json.dumps(config, indent=2))
    print()
    
    try:
        # Criar cliente e executar diagnóstico
        client = create_proxy_client_from_config(config)
        diagnosis = client.diagnose_proxy_issues()
        
        print("Resultados do diagnóstico:")
        print(json.dumps(diagnosis, indent=2, default=str))
        
        # Mostrar recomendações de forma amigável
        if diagnosis.get('recommendations'):
            print("\n📋 Recomendações:")
            for i, rec in enumerate(diagnosis['recommendations'], 1):
                print(f"  {i}. {rec}")
        
    except Exception as e:
        print(f"Erro durante diagnóstico: {e}")

def create_corporate_test_scenarios():
    """Cria cenários de teste típicos de ambientes corporativos"""
    
    print("\n\n=== Cenários Corporativos Típicos ===\n")
    
    scenarios = [
        {
            "name": "🏢 Proxy Corporativo Padrão",
            "description": "Proxy HTTP com autenticação NTLM/Basic",
            "config": {
                "target_host": "api.github.com",
                "target_port": 443,
                "proxy_host": "proxy.company.local",
                "proxy_port": 8080,
                "proxy_username": "domain\\username",
                "proxy_password": "password"
            },
            "expected_issues": [
                "Proxy pode interceptar certificados TLS",
                "Firewall pode bloquear CONNECT para certas portas",
                "Autenticação pode exigir domínio Windows"
            ]
        },
        {
            "name": "🔒 Proxy com SSL Inspection",
            "description": "Proxy que inspeciona tráfego SSL/TLS",
            "config": {
                "target_host": "secure-api.service.com",
                "target_port": 443,
                "proxy_host": "ssl-proxy.company.com",
                "proxy_port": 3128,
                "proxy_username": "user@company.com",
                "proxy_password": "complex_password"
            },
            "expected_issues": [
                "Certificado será substituído pelo do proxy",
                "Pode quebrar certificate pinning",
                "Latência adicional devido à inspeção"
            ]
        },
        {
            "name": "🌐 Proxy de Saída Restritivo", 
            "description": "Proxy que bloqueia muitas conexões",
            "config": {
                "target_host": "external-api.vendor.com",
                "target_port": 443,
                "proxy_host": "restrictive-proxy.corp.com",
                "proxy_port": 8080,
                "proxy_username": "service_account",
                "proxy_password": "service_password"
            },
            "expected_issues": [
                "Lista de sites permitidos restrita",
                "Bloqueio baseado em categorias",
                "Timeouts curtos para conexões externas"
            ]
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print(f"Descrição: {scenario['description']}")
        print(f"Configuração sugerida:")
        print(json.dumps(scenario['config'], indent=2))
        print(f"Problemas esperados:")
        for issue in scenario['expected_issues']:
            print(f"  • {issue}")
        print("-" * 50)

def show_usage_examples():
    """Mostra exemplos de uso prático"""
    
    print("\n\n=== Exemplos de Uso Prático ===\n")
    
    print("1. 📝 Uso básico com proxy sem autenticação:")
    print("""
from proxy_tls_client import ProxyTLSClient

client = ProxyTLSClient(
    host="api.externa.com",
    port=443,
    proxy_host="proxy.empresa.com", 
    proxy_port=8080
)

result = client.connect_and_test()
print(f"Sucesso: {result['connection_success']}")
""")
    
    print("2. 🔐 Uso com autenticação:")
    print("""
client = ProxyTLSClient(
    host="secure-api.com",
    port=443,
    proxy_host="proxy.corp.com",
    proxy_port=3128,
    proxy_username="usuario@empresa.com",
    proxy_password="senha_corporativa"
)

# Diagnóstico completo
diagnosis = client.diagnose_proxy_issues()
""")
    
    print("3. ⚙️ Uso com configuração externa:")
    print("""
config = {
    "target_host": "api.service.com",
    "target_port": 443,
    "proxy_host": "proxy.empresa.com",
    "proxy_port": 8080,
    "proxy_username": "user",
    "proxy_password": "pass",
    "timeout": 30
}

client = create_proxy_client_from_config(config)
result = client.connect_and_test()
""")
    
    print("4. 🔍 Análise de problemas:")
    print("""
# Para debugar problemas específicos
result = client.connect_and_test()

if not result['connect_tunnel_success']:
    print("Problema: Túnel proxy não estabelecido")
    print("Verificar: credenciais, conectividade, método CONNECT")

if result['response_analysis']['type'] == 'HTTP':
    print("Problema: Proxy retornou HTTP em vez de TLS")
    print("Verificar: SSL inspection, políticas de proxy")
""")

if __name__ == "__main__":
    print("🚀 Proxy TLS Client - Sistema de Teste e Diagnóstico")
    print("=" * 60)
    
    # Mostrar exemplos de uso
    show_usage_examples()
    
    # Mostrar cenários corporativos
    create_corporate_test_scenarios()
    
    # Executar testes (comentado para evitar conexões reais)
    print("\n\n⚠️  Para executar testes reais, descomente as linhas abaixo")
    print("e ajuste as configurações de proxy conforme seu ambiente:")
    print()
    print("# test_proxy_configurations()")
    print("# demonstrate_proxy_diagnosis()")
    
    print("\n\n✅ Sistema proxy configurado com sucesso!")
    print("\nCapacidades implementadas:")
    print("✓ Suporte a proxy HTTP CONNECT")
    print("✓ Autenticação Basic (usuário/senha)")
    print("✓ Diagnóstico automático de problemas")
    print("✓ Análise de respostas não-TLS")
    print("✓ Herança do TLS Raw Client completo")
    print("✓ Logging detalhado para debug")
    print("✓ Configuração flexível via dicionário")
    print("✓ Tratamento de erros corporativos")
    
    print("\n📚 Arquivos criados:")
    print("  • proxy_tls_client.py - Cliente principal com proxy")
    print("  • Este script de teste e exemplos")
    
    print("\n🎯 Próximos passos:")
    print("  1. Ajustar configurações de proxy para seu ambiente")
    print("  2. Testar conectividade básica")
    print("  3. Executar diagnóstico completo")
    print("  4. Analisar logs para identificar problemas")
