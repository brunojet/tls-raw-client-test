#!/usr/bin/env python3
"""
Demonstração do sistema de configuração por arquivos do Proxy TLS Client
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import logging
from tlsraw.proxy_tls_client import ProxyTLSClient

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def demo_config_file_usage():
    """Demonstra diferentes formas de usar arquivos de configuração"""
    
    print("🎯 Demonstração: Sistema de Configuração por Arquivos")
    print("=" * 55)
    
    # 1. Listar configurações disponíveis
    print("\n1️⃣ Listando configurações disponíveis...")
    
    # Criar um cliente temporário só para listar configs
    temp_client = ProxyTLSClient("dummy", 443, "dummy", 8080)
    available_configs = temp_client.list_available_configs()
    
    if available_configs:
        print("📁 Configurações encontradas:")
        for filename, path in available_configs.items():
            print(f"   • {filename} -> {path}")
            
            # Mostrar resumo da configuração
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    target = f"{config.get('target_host')}:{config.get('target_port')}"
                    proxy = f"{config.get('proxy_host')}:{config.get('proxy_port')}"
                    auth = "Com auth" if config.get('proxy_username') else "Sem auth"
                    desc = config.get('_metadata', {}).get('description', 'N/A')
                    print(f"     Target: {target} | Proxy: {proxy} | {auth}")
                    print(f"     Desc: {desc}")
            except:
                pass
            print()
    else:
        print("❌ Nenhuma configuração encontrada")
    
    # 2. Demonstrar diferentes métodos de carregamento
    print("\n2️⃣ Métodos de carregamento de configuração...\n")
    
    # Método 1: Construtor com config_file
    print("📝 Método 1: Construtor com config_file")
    print("```python")
    print("client = ProxyTLSClient(")
    print("    host='default.com', port=443,")
    print("    proxy_host='default.proxy', proxy_port=8080,")
    print("    config_file='configs/proxy_basic.json'")
    print(")")
    print("```")
    
    # Método 2: from_config_file
    print("\n📝 Método 2: from_config_file (recomendado)")
    print("```python")
    print("client = ProxyTLSClient.from_config_file('configs/proxy_auth.json')")
    print("```")
    
    # Método 3: from_config_file com overrides
    print("\n📝 Método 3: from_config_file com overrides")
    print("```python")
    print("client = ProxyTLSClient.from_config_file(")
    print("    'configs/lambda_proxy.json',")
    print("    target_host='outro-servidor.com',")
    print("    timeout=60")
    print(")")
    print("```")

def demo_practical_examples():
    """Demonstra exemplos práticos de uso"""
    
    print("\n\n3️⃣ Exemplos Práticos")
    print("=" * 25)
    
    examples = [
        {
            "name": "🏢 Ambiente Corporativo Básico",
            "config": "configs/proxy_basic.json",
            "description": "Proxy sem autenticação para testes básicos"
        },
        {
            "name": "🔐 Ambiente com Autenticação",
            "config": "configs/proxy_auth.json", 
            "description": "Proxy corporativo com credenciais Windows"
        },
        {
            "name": "☁️ AWS Lambda Corporate",
            "config": "configs/lambda_proxy.json",
            "description": "Configuração otimizada para Lambda em ambiente corporativo"
        },
        {
            "name": "🛡️ Ambiente de Segurança",
            "config": "configs/security_proxy.json",
            "description": "Proxy de segurança com SSL inspection"
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}")
        print(f"Config: {example['config']}")
        print(f"Desc: {example['description']}")
        
        config_path = example['config']
        if os.path.exists(config_path):
            try:
                # Mostrar como criar cliente
                print(f"Uso:")
                print(f"```python")
                print(f"client = ProxyTLSClient.from_config_file('{config_path}')")
                print(f"result = client.connect_and_test()")
                print(f"```")
                
                # Mostrar configuração
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                print(f"Configuração:")
                filtered_config = {k: v for k, v in config.items() if not k.startswith('_')}
                # Mascarar senha se presente
                if 'proxy_password' in filtered_config:
                    filtered_config['proxy_password'] = '***'
                print(json.dumps(filtered_config, indent=2))
                
            except Exception as e:
                print(f"❌ Erro ao processar configuração: {e}")
        else:
            print(f"❌ Arquivo não encontrado: {config_path}")
        
        print("-" * 50)

def demo_config_management():
    """Demonstra gerenciamento de configurações"""
    
    print("\n\n4️⃣ Gerenciamento de Configurações")
    print("=" * 35)
    
    print("\n📁 Criando nova configuração...")
    
    # Criar cliente com configurações específicas
    client = ProxyTLSClient(
        host="teste.exemplo.com",
        port=443,
        proxy_host="proxy.teste.com",
        proxy_port=8080,
        proxy_username="usuario_teste",
        proxy_password="senha_teste",
        timeout=45
    )
    
    # Salvar configuração
    new_config_path = "configs/teste_demo.json"
    if client.save_config(new_config_path):
        print(f"✅ Configuração salva em: {new_config_path}")
        
        # Mostrar conteúdo salvo
        with open(new_config_path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
            print(f"Conteúdo salvo:")
            print(json.dumps(saved_config, indent=2))
    else:
        print("❌ Erro ao salvar configuração")
    
    print("\n🔍 Buscas de configuração...")
    print("O sistema busca arquivos de configuração em:")
    print("• Caminho exato fornecido")
    print("• Diretório atual")
    print("• Diretório do script")
    print("• ~/.tlsraw/ (home do usuário)")

def demo_environment_specific():
    """Demonstra configurações específicas por ambiente"""
    
    print("\n\n5️⃣ Configurações por Ambiente")
    print("=" * 32)
    
    environments = {
        "development": {
            "config_file": "configs/dev_proxy.json",
            "description": "Ambiente de desenvolvimento - proxy local",
            "sample_config": {
                "target_host": "dev-api.internal.com",
                "target_port": 443,
                "proxy_host": "dev-proxy.local",
                "proxy_port": 8080,
                "timeout": 15
            }
        },
        "staging": {
            "config_file": "configs/staging_proxy.json", 
            "description": "Ambiente de staging - proxy corporativo",
            "sample_config": {
                "target_host": "staging-api.company.com",
                "target_port": 443,
                "proxy_host": "staging-proxy.corp.com",
                "proxy_port": 3128,
                "proxy_username": "staging_user",
                "proxy_password": "staging_pass",
                "timeout": 30
            }
        },
        "production": {
            "config_file": "configs/prod_proxy.json",
            "description": "Ambiente de produção - proxy seguro",
            "sample_config": {
                "target_host": "api.production.com",
                "target_port": 443,
                "proxy_host": "secure-proxy.company.com",
                "proxy_port": 8443,
                "proxy_username": "prod_service",
                "proxy_password": "secure_password",
                "timeout": 60
            }
        }
    }
    
    for env_name, env_info in environments.items():
        print(f"\n🌍 Ambiente: {env_name.upper()}")
        print(f"Arquivo: {env_info['config_file']}")
        print(f"Descrição: {env_info['description']}")
        
        print("Configuração exemplo:")
        print(json.dumps(env_info['sample_config'], indent=2))
        
        print("Uso:")
        print(f"```python")
        print(f"client = ProxyTLSClient.from_config_file('{env_info['config_file']}')")
        print(f"```")
        print("-" * 40)

def show_best_practices():
    """Mostra melhores práticas para uso de configurações"""
    
    print("\n\n6️⃣ Melhores Práticas")
    print("=" * 22)
    
    practices = [
        {
            "title": "📁 Organização de Arquivos",
            "tips": [
                "Use diretório 'configs/' para arquivos de configuração",
                "Nomeie arquivos claramente: env_tipo.json (ex: prod_proxy.json)",
                "Use metadados (_metadata) para documentação",
                "Versione arquivos de configuração no git (sem senhas)"
            ]
        },
        {
            "title": "🔐 Segurança",
            "tips": [
                "NUNCA commite senhas em arquivos de configuração",
                "Use variáveis de ambiente para credenciais sensíveis",
                "Considere encriptação para configurações sensíveis",
                "Permissões restritivas nos arquivos (600 no Linux)"
            ]
        },
        {
            "title": "🔄 Flexibilidade",
            "tips": [
                "Use from_config_file() com overrides para customização",
                "Mantenha configurações base e especialize por ambiente",
                "Use metadados para documentar propósito e limitações",
                "Teste configurações antes de usar em produção"
            ]
        },
        {
            "title": "🐛 Debug e Troubleshooting",
            "tips": [
                "Ative logging DEBUG para ver carregamento de configs",
                "Use list_available_configs() para verificar arquivos",
                "Salve configurações funcionais com save_config()",
                "Documente problemas conhecidos nos metadados"
            ]
        }
    ]
    
    for practice in practices:
        print(f"\n{practice['title']}")
        for tip in practice['tips']:
            print(f"  • {tip}")

if __name__ == "__main__":
    print("🚀 Sistema de Configuração por Arquivos - Proxy TLS Client")
    print("=" * 60)
    
    # Executar demonstrações
    demo_config_file_usage()
    demo_practical_examples()
    demo_config_management()
    demo_environment_specific()
    show_best_practices()
    
    print("\n\n✅ Demonstração Completa!")
    print("\n🎯 Próximos passos:")
    print("1. Crie suas configurações específicas em configs/")
    print("2. Use ProxyTLSClient.from_config_file() para carregar")
    print("3. Customize com overrides conforme necessário")
    print("4. Documente configurações com metadados")
    print("5. Mantenha senhas fora dos arquivos de configuração")
    
    print("\n📚 Arquivos de exemplo criados:")
    print("• configs/proxy_basic.json - Proxy básico sem auth")
    print("• configs/proxy_auth.json - Proxy com autenticação")
    print("• configs/lambda_proxy.json - Configuração para Lambda")
    print("• configs/security_proxy.json - Proxy de segurança")
