#!/usr/bin/env python3
"""
Script de exemplo simples para teste rápido de TLS
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlsraw.tls_raw_client import TLSRawClient
import json

def test_server(host, port=443):
    """Testa um servidor TLS e imprime resultados detalhados"""
    
    print(f"🔍 Testando {host}:{port}")
    print("=" * 50)
    
    client = TLSRawClient(host, port, timeout=15.0)
    
    # Teste com SNI
    print("📡 Teste com SNI habilitado:")
    results_sni = client.connect_and_test(use_sni=True)
    print_results(results_sni)
    
    print("\n" + "-" * 30 + "\n")
    
    # Teste sem SNI
    print("📡 Teste sem SNI:")
    results_no_sni = client.connect_and_test(use_sni=False)
    print_results(results_no_sni)
    
    return results_sni, results_no_sni

def print_results(results):
    """Imprime resultados de forma organizada"""
    
    # Status da conexão
    if results['connection_success']:
        print(f"✅ Conexão TCP: OK ({results.get('connect_time', 0):.3f}s)")
    else:
        print("❌ Conexão TCP: FALHOU")
        
    # Client Hello
    if results['client_hello_sent']:
        print(f"✅ Client Hello: Enviado ({results.get('client_hello_size', 0)} bytes)")
    else:
        print("❌ Client Hello: NÃO ENVIADO")
    
    # Resposta do servidor
    if results['server_response']:
        resp = results['server_response']
        print(f"📥 Resposta: {resp['type']}")
        
        if 'handshake_type' in resp:
            if resp['handshake_type'] == 'Server Hello':
                print("✅ Server Hello recebido - Handshake iniciado com sucesso!")
            else:
                print(f"📋 Handshake: {resp['handshake_type']}")
                
        if 'alert_level' in resp:
            level = resp['alert_level']
            desc = resp['alert_description']
            if level == 'Fatal':
                print(f"❌ ALERT FATAL: {desc}")
            else:
                print(f"⚠️  Alert: {level} - {desc}")
                
        print(f"📊 Tamanho da resposta: {results.get('response_size', 0)} bytes")
        
    else:
        print("❌ Nenhuma resposta do servidor")
    
    # Erros
    if results['error']:
        print(f"❌ Erro: {results['error']}")
    
    # Dados raw (apenas primeiros bytes para não poluir)
    if results.get('raw_response'):
        raw = results['raw_response']
        preview = raw[:40] + "..." if len(raw) > 40 else raw
        print(f"🔍 Resposta hex: {preview}")

def diagnose_lambda_issue(host, port=443):
    """
    Diagnóstico específico para problemas de Lambda
    """
    print("🏥 DIAGNÓSTICO PARA PROBLEMAS DE LAMBDA")
    print("=" * 50)
    
    client = TLSRawClient(host, port, timeout=30.0)  # Timeout maior para Lambda
    
    # Múltiplos testes para identificar padrões
    print("Executando múltiplos testes para identificar padrões...\n")
    
    results_list = []
    
    for i in range(3):
        print(f"🔄 Teste {i+1}/3:")
        results = client.connect_and_test(use_sni=True)
        results_list.append(results)
        
        # Status resumido
        tcp_ok = "✅" if results['connection_success'] else "❌"
        hello_ok = "✅" if results['client_hello_sent'] else "❌"
        response_ok = "✅" if results['server_response'] else "❌"
        
        print(f"  TCP: {tcp_ok} | Client Hello: {hello_ok} | Resposta: {response_ok}")
        
        if results['error']:
            print(f"  ❌ {results['error']}")
        elif results['server_response']:
            resp = results['server_response']
            if 'alert_level' in resp:
                print(f"  ⚠️  {resp['alert_level']}: {resp['alert_description']}")
            elif 'handshake_type' in resp:
                print(f"  📋 {resp['handshake_type']}")
        
        print()
    
    # Análise dos resultados
    print("📊 ANÁLISE DOS RESULTADOS:")
    print("-" * 30)
    
    tcp_success_rate = sum(1 for r in results_list if r['connection_success']) / len(results_list)
    hello_success_rate = sum(1 for r in results_list if r['client_hello_sent']) / len(results_list)
    response_rate = sum(1 for r in results_list if r['server_response']) / len(results_list)
    
    print(f"Taxa de sucesso TCP: {tcp_success_rate:.1%}")
    print(f"Taxa de envio Client Hello: {hello_success_rate:.1%}")
    print(f"Taxa de resposta do servidor: {response_rate:.1%}")
    
    # Análise de padrões de erro
    errors = [r['error'] for r in results_list if r['error']]
    if errors:
        print(f"\n❌ Erros encontrados:")
        for error in set(errors):
            count = errors.count(error)
            print(f"  • {error} ({count}x)")
    
    # Análise de alerts
    alerts = []
    for r in results_list:
        if r['server_response'] and 'alert_description' in r['server_response']:
            alerts.append(r['server_response']['alert_description'])
    
    if alerts:
        print(f"\n⚠️  Alerts TLS recebidos:")
        for alert in set(alerts):
            count = alerts.count(alert)
            print(f"  • {alert} ({count}x)")
    
    print("\n💡 RECOMENDAÇÕES:")
    print("-" * 20)
    
    if tcp_success_rate < 1.0:
        print("• Problemas de conectividade de rede ou firewall")
        print("• Verificar se o Lambda tem acesso ao destino")
        
    if hello_success_rate < tcp_success_rate:
        print("• Problema no envio do Client Hello")
        print("• Possível problema de MTU ou fragmentação")
        
    if response_rate < hello_success_rate:
        print("• Servidor está recebendo Client Hello mas não respondendo")
        print("• Possível incompatibilidade de cipher suites ou versões TLS")
        print("• Verificar se SNI é obrigatório no servidor")
        
    if 'handshake_failure' in str(alerts):
        print("• Falha no handshake TLS - verificar cipher suites suportados")
        
    if 'protocol_version' in str(alerts):
        print("• Incompatibilidade de versão TLS")
        
    print("\n🔧 Para usar no Lambda:")
    print("• Copie este código para sua função Lambda")
    print("• Execute diagnose_lambda_issue() no handler")
    print("• Analise os logs do CloudWatch")

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso:")
        print(f"  python {sys.argv[0]} <host> [porta]")
        print(f"  python {sys.argv[0]} google.com")
        print(f"  python {sys.argv[0]} exemplo.com 8443")
        print()
        print("Para diagnóstico de Lambda:")
        print(f"  python {sys.argv[0]} --lambda <host> [porta]")
        return
    
    if sys.argv[1] == '--lambda':
        if len(sys.argv) < 3:
            print("Uso: python script.py --lambda <host> [porta]")
            return
        host = sys.argv[2]
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 443
        diagnose_lambda_issue(host, port)
    else:
        host = sys.argv[1]
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 443
        test_server(host, port)

if __name__ == "__main__":
    main()
