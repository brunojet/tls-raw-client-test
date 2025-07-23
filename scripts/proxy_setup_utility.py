#!/usr/bin/env python3
"""
Utilitário de configuração e teste para Proxy TLS Client
Facilita setup e diagnóstico em ambientes corporativos
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import argparse
import getpass
from typing import Dict, Any
from tlsraw.proxy_tls_client import create_proxy_client_from_config

def load_config_file(config_path: str = "proxy_config_examples.json") -> Dict[str, Any]:
    """Carrega arquivo de configuração"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo de configuração não encontrado: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return {}

def get_proxy_config_interactive() -> Dict[str, Any]:
    """Coleta configuração de proxy interativamente"""
    
    print("\n🔧 Configuração Interativa de Proxy")
    print("=" * 40)
    
    config = {}
    
    # Informações do proxy
    config["proxy_host"] = input("Endereço do proxy (ex: proxy.empresa.com): ").strip()
    if not config["proxy_host"]:
        print("❌ Endereço do proxy é obrigatório")
        return {}
    
    try:
        config["proxy_port"] = int(input("Porta do proxy (ex: 8080): ").strip())
    except ValueError:
        print("❌ Porta deve ser um número")
        return {}
    
    # Autenticação
    use_auth = input("Usar autenticação? (s/n): ").strip().lower()
    if use_auth in ['s', 'sim', 'y', 'yes']:
        config["proxy_username"] = input("Usuário: ").strip()
        if config["proxy_username"]:
            config["proxy_password"] = getpass.getpass("Senha: ")
    
    # Servidor de destino
    print("\n🎯 Servidor de Destino")
    config["target_host"] = input("Host de destino (ex: www.google.com): ").strip()
    if not config["target_host"]:
        config["target_host"] = "www.google.com"
    
    try:
        port_input = input("Porta de destino (ex: 443): ").strip()
        config["target_port"] = int(port_input) if port_input else 443
    except ValueError:
        config["target_port"] = 443
    
    # Timeout
    try:
        timeout_input = input("Timeout em segundos (ex: 30): ").strip()
        config["timeout"] = int(timeout_input) if timeout_input else 30
    except ValueError:
        config["timeout"] = 30
    
    return config

def save_config_file(config: Dict[str, Any], filename: str = "my_proxy_config.json") -> bool:
    """Salva configuração em arquivo"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuração salva em: {filename}")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar configuração: {e}")
        return False

def test_proxy_config(config: Dict[str, Any]) -> bool:
    """Testa configuração de proxy"""
    
    print(f"\n🧪 Testando configuração:")
    print(f"   Proxy: {config.get('proxy_host')}:{config.get('proxy_port')}")
    print(f"   Destino: {config.get('target_host')}:{config.get('target_port')}")
    print(f"   Auth: {'Sim' if config.get('proxy_username') else 'Não'}")
    
    try:
        # Criar cliente
        client = create_proxy_client_from_config(config)
        
        # Teste básico de conectividade
        print("\n1️⃣ Testando conectividade com proxy...")
        proxy_test = client.test_proxy_connectivity()
        
        if proxy_test["proxy_connection_success"]:
            print(f"   ✅ Conexão com proxy: OK ({proxy_test.get('proxy_connect_time', 0):.3f}s)")
            
            if proxy_test.get("connect_success"):
                print("   ✅ Método CONNECT: OK")
            else:
                print("   ❌ Método CONNECT: Falhou")
                if proxy_test.get("error"):
                    print(f"      Erro: {proxy_test['error']}")
                return False
        else:
            print("   ❌ Conexão com proxy: Falhou")
            if proxy_test.get("error"):
                print(f"      Erro: {proxy_test['error']}")
            return False
        
        # Teste TLS completo
        print("\n2️⃣ Testando handshake TLS através do proxy...")
        tls_result = client.connect_and_test()
        
        if tls_result["connect_tunnel_success"]:
            print("   ✅ Túnel proxy: OK")
        else:
            print("   ❌ Túnel proxy: Falhou")
            return False
        
        if tls_result["client_hello_sent"]:
            print("   ✅ Client Hello enviado: OK")
        else:
            print("   ❌ Client Hello: Falhou")
            return False
        
        response_size = tls_result.get("response_size", 0)
        if response_size > 0:
            print(f"   ✅ Resposta recebida: {response_size} bytes")
            
            # Analisar tipo de resposta
            if "response_analysis" in tls_result:
                analysis = tls_result["response_analysis"]
                print(f"   📊 Tipo: {analysis['type']}")
                print(f"   📊 Fonte: {analysis['likely_source']}")
                
                if analysis["type"] == "TLS":
                    print("   ✅ Handshake TLS bem-sucedido!")
                elif analysis["type"] == "HTTP":
                    print("   ⚠️ Resposta HTTP detectada (possível SSL inspection)")
                else:
                    print(f"   ⚠️ Resposta inesperada: {analysis['type']}")
        else:
            print("   ❌ Nenhuma resposta recebida")
            return False
        
        print("\n✅ Teste completo bem-sucedido!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante teste: {e}")
        return False

def run_diagnostics(config: Dict[str, Any]) -> None:
    """Executa diagnóstico completo"""
    
    print(f"\n🔍 Diagnóstico Completo de Proxy")
    print("=" * 40)
    
    try:
        client = create_proxy_client_from_config(config)
        diagnosis = client.diagnose_proxy_issues()
        
        # Mostrar resultados organizados
        print(f"\n📋 Resultados:")
        
        # Teste de conectividade
        connectivity = diagnosis["tests"].get("proxy_connectivity", {})
        print(f"   Conexão proxy: {'✅' if connectivity.get('proxy_connection_success') else '❌'}")
        print(f"   CONNECT method: {'✅' if connectivity.get('connect_success') else '❌'}")
        
        # Teste TLS
        tls_test = diagnosis["tests"].get("tls_through_proxy", {})
        print(f"   Túnel proxy: {'✅' if tls_test.get('connect_tunnel_success') else '❌'}")
        print(f"   Client Hello: {'✅' if tls_test.get('client_hello_sent') else '❌'}")
        print(f"   Resposta: {tls_test.get('response_size', 0)} bytes")
        
        # Recomendações
        if diagnosis.get("recommendations"):
            print(f"\n💡 Recomendações:")
            for i, rec in enumerate(diagnosis["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        # Salvar diagnóstico detalhado
        with open("diagnostico_proxy.json", "w", encoding="utf-8") as f:
            json.dump(diagnosis, f, indent=2, default=str, ensure_ascii=False)
        print(f"\n📄 Diagnóstico detalhado salvo em: diagnostico_proxy.json")
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")

def show_examples() -> None:
    """Mostra exemplos de configuração"""
    
    config_data = load_config_file()
    
    print("\n📚 Exemplos de Configuração")
    print("=" * 30)
    
    if "proxy_configurations" in config_data:
        for name, config in config_data["proxy_configurations"].items():
            print(f"\n🔧 {name}:")
            print(f"   Descrição: {config.get('description', 'N/A')}")
            print(f"   Host: {config.get('proxy_host', 'N/A')}")
            print(f"   Porta: {config.get('proxy_port', 'N/A')}")
            print(f"   Auth: {'Sim' if config.get('proxy_username') else 'Não'}")
    
    if "test_targets" in config_data:
        print(f"\n🎯 Alvos de Teste Sugeridos:")
        for name, target in config_data["test_targets"].items():
            print(f"   {name}: {target['host']}:{target['port']} - {target['description']}")

def show_troubleshooting() -> None:
    """Mostra guia de resolução de problemas"""
    
    config_data = load_config_file()
    
    print("\n🛠️ Guia de Resolução de Problemas")
    print("=" * 35)
    
    if "troubleshooting" in config_data:
        for issue, info in config_data["troubleshooting"].items():
            print(f"\n❌ {info['error']}")
            print("   Soluções:")
            for solution in info['solutions']:
                print(f"   • {solution}")

def main():
    """Função principal do utilitário"""
    
    parser = argparse.ArgumentParser(description="Utilitário de Proxy TLS Client")
    parser.add_argument("--config", "-c", help="Arquivo de configuração JSON")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Modo interativo para configuração")
    parser.add_argument("--test", "-t", action="store_true",
                       help="Executar teste de conectividade")
    parser.add_argument("--diagnose", "-d", action="store_true",
                       help="Executar diagnóstico completo")
    parser.add_argument("--examples", "-e", action="store_true",
                       help="Mostrar exemplos de configuração")
    parser.add_argument("--troubleshoot", "-s", action="store_true",
                       help="Mostrar guia de resolução de problemas")
    
    args = parser.parse_args()
    
    print("🚀 Proxy TLS Client - Utilitário de Configuração")
    print("=" * 50)
    
    # Mostrar exemplos
    if args.examples:
        show_examples()
        return
    
    # Mostrar troubleshooting
    if args.troubleshoot:
        show_troubleshooting()
        return
    
    # Configuração interativa
    if args.interactive:
        config = get_proxy_config_interactive()
        if not config:
            return
        
        # Salvar configuração
        save_config_file(config)
        
        # Testar se solicitado
        if input("\nTestar configuração agora? (s/n): ").strip().lower() in ['s', 'sim', 'y', 'yes']:
            test_proxy_config(config)
        
        return
    
    # Carregar configuração de arquivo
    config = {}
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar configuração: {e}")
            return
    
    # Se não tem configuração, mostrar help
    if not config:
        print("\n⚠️ Nenhuma configuração fornecida")
        print("Use --interactive para configuração interativa")
        print("ou --config arquivo.json para carregar configuração")
        print("ou --examples para ver exemplos")
        print("\nUse --help para ver todas as opções")
        return
    
    # Executar testes
    if args.test:
        test_proxy_config(config)
    
    if args.diagnose:
        run_diagnostics(config)

if __name__ == "__main__":
    main()
