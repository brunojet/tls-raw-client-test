#!/usr/bin/env python3
"""
Diagnóstico específico para problemas de Firewall Corporativo
Testa diferentes variações de Client Hello para identificar bloqueios
"""

from .tls_raw_client import TLSRawClient, logger
import struct
import time
import json
from typing import Optional

class FirewallDiagnosticClient(TLSRawClient):
    """Cliente especializado para diagnosticar problemas de firewall"""
    
    def create_minimal_client_hello(self, server_name: Optional[str] = None) -> bytes:
        """
        Cria um Client Hello mínimo reutilizando a estrutura do TLSRawClient
        """
        logger.info("Construindo Client Hello MÍNIMO...")
        
        # Usar cipher suites mais básicos (sem TLS 1.3)
        original_ciphers = self.CIPHER_SUITES
        self.CIPHER_SUITES = [
            0xc02f,  # TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
            0xc030,  # TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
            0x009c,  # TLS_RSA_WITH_AES_128_GCM_SHA256
            0x009d,  # TLS_RSA_WITH_AES_256_GCM_SHA384
            0x002f,  # TLS_RSA_WITH_AES_128_CBC_SHA
            0x0035,  # TLS_RSA_WITH_AES_256_CBC_SHA
        ]
        
        # Sobrescrever o método de extensions temporariamente
        original_extensions = self._create_extensions
        self._create_extensions = self._create_minimal_extensions
        
        try:
            # Usar o método pai com configurações mínimas
            result = self.create_client_hello(server_name)
            logger.info(f"Client Hello MÍNIMO criado: {len(result)} bytes")
            return result
        finally:
            # Restaurar configurações originais
            self.CIPHER_SUITES = original_ciphers
            self._create_extensions = original_extensions
    
    def _create_minimal_extensions(self, server_name: Optional[str] = None) -> bytes:
        """Extensions mínimas para evitar bloqueio de firewall"""
        extensions = b''
        
        # Apenas SNI se necessário
        if server_name:
            sni_data = struct.pack('!BH', 0, len(server_name)) + server_name.encode('utf-8')
            sni_list = struct.pack('!H', len(sni_data)) + sni_data
            sni_ext = struct.pack('!HH', 0x0000, len(sni_list)) + sni_list
            extensions += sni_ext
        
        # Supported Groups básico (apenas curvas clássicas)
        basic_groups = [0x0017, 0x0018, 0x0019]  # secp256r1, secp384r1, secp521r1
        groups_data = b''.join(group.to_bytes(2, 'big') for group in basic_groups)
        groups_ext = struct.pack('!HHH', 0x000a, len(groups_data) + 2, len(groups_data))
        groups_ext += groups_data
        extensions += groups_ext
        
        # EC Point Formats básico
        ec_formats = b'\x01\x00'  # uncompressed apenas
        ec_ext = struct.pack('!HH', 0x000b, len(ec_formats)) + ec_formats
        extensions += ec_ext
        
        # Signature Algorithms básico (apenas RSA/ECDSA clássicos)
        basic_sig_algs = [
            0x0401,  # rsa_pkcs1_sha256
            0x0501,  # rsa_pkcs1_sha384
            0x0403,  # ecdsa_secp256r1_sha256
            0x0503,  # ecdsa_secp384r1_sha384
        ]
        sig_data = b''.join(alg.to_bytes(2, 'big') for alg in basic_sig_algs)
        sig_ext = struct.pack('!HHH', 0x000d, len(sig_data) + 2, len(sig_data))
        sig_ext += sig_data
        extensions += sig_ext
        
        return extensions
    
    def create_legacy_client_hello(self, server_name: Optional[str] = None) -> bytes:
        """
        Cria um Client Hello ainda mais legado (TLS 1.0 style) para firewalls antigos
        """
        logger.info("Construindo Client Hello LEGACY...")
        
        # Cipher suites muito básicos
        original_ciphers = self.CIPHER_SUITES
        self.CIPHER_SUITES = [
            0x002f,  # TLS_RSA_WITH_AES_128_CBC_SHA
            0x0035,  # TLS_RSA_WITH_AES_256_CBC_SHA
            0x000a,  # TLS_RSA_WITH_3DES_EDE_CBC_SHA
        ]
        
        # Session ID com tamanho fixo (como clientes antigos)
        original_random = self.generate_random_bytes
        self.generate_random_bytes = lambda x: b'\x00' * x  # Random zeros para consistência
        
        # Sobrescrever extensions para mínimo absoluto
        original_extensions = self._create_extensions
        self._create_extensions = lambda sn: b'' if not sn else struct.pack('!HH', 0x0000, len(sn) + 5) + struct.pack('!HBH', len(sn) + 3, 0, len(sn)) + sn.encode('utf-8')
        
        try:
            result = self.create_client_hello(server_name)
            logger.info(f"Client Hello LEGACY criado: {len(result)} bytes")
            return result
        finally:
            # Restaurar configurações
            self.CIPHER_SUITES = original_ciphers
            self.generate_random_bytes = original_random
            self._create_extensions = original_extensions

def diagnose_corporate_firewall(host: str, port: int = 443):
    """
    Diagnóstico específico para firewall corporativo
    """
    print("🔥 DIAGNÓSTICO DE FIREWALL CORPORATIVO")
    print("=" * 60)
    print(f"Testando: {host}:{port}")
    print("Cenário: Firewall centralizado interceptando tráfego TLS")
    print()
    
    # Diferentes clientes para testar
    standard_client = TLSRawClient(host, port, timeout=15.0)
    firewall_client = FirewallDiagnosticClient(host, port, timeout=15.0)
    
    tests = [
        {
            "name": "1. Client Hello Padrão (OpenSSL-like)",
            "description": "Client Hello completo baseado no dump OpenSSL",
            "client": standard_client,
            "method": "create_client_hello",
            "sni": True
        },
        {
            "name": "2. Client Hello Mínimo",
            "description": "Client Hello simplificado (sem TLS 1.3, extensions básicas)",
            "client": firewall_client,
            "method": "create_minimal_client_hello", 
            "sni": True
        },
        {
            "name": "3. Client Hello Legacy",
            "description": "Client Hello muito básico (como browsers antigos)",
            "client": firewall_client,
            "method": "create_legacy_client_hello",
            "sni": True
        },
        {
            "name": "4. Sem SNI",
            "description": "Teste sem Server Name Indication",
            "client": firewall_client,
            "method": "create_minimal_client_hello",
            "sni": False
        },
        {
            "name": "5. Múltiplas Tentativas",
            "description": "Detectar intermitências e padrões temporais",
            "client": standard_client,
            "method": "create_client_hello",
            "sni": True,
            "repeat": 5
        },
        {
            "name": "6. Conexões Consecutivas",
            "description": "Testar se firewall bloqueia após múltiplas conexões",
            "client": firewall_client,
            "method": "create_minimal_client_hello",
            "sni": True,
            "repeat": 3,
            "no_delay": True
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"🧪 TESTE {i}: {test['name']}")
        print(f"📋 {test['description']}")
        print("-" * 40)
        
        repeat_count = test.get('repeat', 1)
        test_results = []
        
        for attempt in range(repeat_count):
            if repeat_count > 1:
                print(f"  Tentativa {attempt + 1}/{repeat_count}:")
            
            try:
                # Criar Client Hello
                if test['sni']:
                    hello_data = getattr(test['client'], test['method'])(host)
                else:
                    hello_data = getattr(test['client'], test['method'])(None)
                
                # Testar conectividade
                result = test['client'].connect_and_test(use_sni=test['sni'])
                result['hello_size'] = len(hello_data)
                result['test_name'] = test['name']
                
                test_results.append(result)
                
                # Status resumido
                tcp_ok = "✅" if result['connection_success'] else "❌"
                hello_ok = "✅" if result['client_hello_sent'] else "❌" 
                resp_ok = "✅" if result['server_response'] else "❌"
                
                status_line = f"  TCP: {tcp_ok} | Hello: {hello_ok} | Resp: {resp_ok}"
                
                if result['server_response']:
                    if 'handshake_type' in result['server_response']:
                        status_line += f" | {result['server_response']['handshake_type']}"
                    elif 'alert_description' in result['server_response']:
                        status_line += f" | Alert: {result['server_response']['alert_description']}"
                
                if result['error']:
                    status_line += f" | ❌ {result['error']}"
                
                print(status_line)
                
                # Timing para detectar timeouts vs. resets
                if 'connect_time' in result:
                    timing = f"  ⏱️  TCP: {result['connect_time']:.3f}s"
                    if result['error'] and 'timeout' in result['error'].lower():
                        timing += " | TLS: TIMEOUT"
                    elif result['error'] and 'reset' in result['error'].lower():
                        timing += " | TLS: RESET (firewall?)"
                    print(timing)
                
            except Exception as e:
                error_result = {
                    'test_name': test['name'],
                    'error': str(e),
                    'connection_success': False,
                    'client_hello_sent': False,
                    'server_response': None
                }
                test_results.append(error_result)
                print(f"  ❌ Exceção: {e}")
            
            if repeat_count > 1 and attempt < repeat_count - 1:
                # Delay configurable entre tentativas
                delay = 0.5 if test.get('no_delay') else 2.0
                time.sleep(delay)
        
        results.extend(test_results)
        print("\n")
    
    # Análise dos resultados
    print("📊 ANÁLISE DE FIREWALL:")
    print("=" * 40)
    
    # Análise por tipo de teste
    tcp_success_by_test = {}
    hello_success_by_test = {}
    response_by_test = {}
    
    for result in results:
        test_name = result['test_name']
        
        if test_name not in tcp_success_by_test:
            tcp_success_by_test[test_name] = []
            hello_success_by_test[test_name] = []
            response_by_test[test_name] = []
        
        tcp_success_by_test[test_name].append(result['connection_success'])
        hello_success_by_test[test_name].append(result['client_hello_sent'])
        response_by_test[test_name].append(bool(result['server_response']))
    
    for test_name in tcp_success_by_test:
        tcp_rate = sum(tcp_success_by_test[test_name]) / len(tcp_success_by_test[test_name])
        hello_rate = sum(hello_success_by_test[test_name]) / len(hello_success_by_test[test_name])
        resp_rate = sum(response_by_test[test_name]) / len(response_by_test[test_name])
        
        print(f"{test_name}:")
        print(f"  TCP: {tcp_rate:.1%} | Hello: {hello_rate:.1%} | Resposta: {resp_rate:.1%}")
    
    print("\n🔍 INDICADORES DE FIREWALL:")
    print("-" * 30)
    
    # Análise mais detalhada dos padrões
    all_tcp_success = all(r['connection_success'] for r in results)
    tcp_success_rate = sum(r['connection_success'] for r in results) / len(results)
    hello_sent_rate = sum(r['client_hello_sent'] for r in results if r['connection_success']) / max(1, sum(r['connection_success'] for r in results))
    response_rate = sum(bool(r['server_response']) for r in results) / len(results)
    
    reset_errors = [r for r in results if r.get('error') and 'reset' in r['error'].lower()]
    timeout_errors = [r for r in results if r.get('error') and 'timeout' in r['error'].lower()]
    
    # Padrões específicos de firewall corporativo
    if tcp_success_rate > 0.8 and response_rate < 0.2:
        print("🔴 FIREWALL CORPORATIVO DETECTADO:")
        print("  • TCP conecta consistentemente")
        print("  • Client Hello enviado com sucesso")
        print("  • Servidor nunca responde (silent drop)")
        print("  • DIAGNÓSTICO: Firewall bloqueando TLS baseado em conteúdo")
    
    if reset_errors:
        print("🔴 FIREWALL COM INSPEÇÃO ATIVA:")
        print(f"  • {len(reset_errors)} conexões resetadas ativamente")
        print("  • Deep Packet Inspection (DPI) detectou padrões suspeitos")
        print("  • Possível bloqueio de cipher suites ou extensions específicas")
        
        # Verificar se reset acontece com tipos específicos
        reset_by_type = {}
        for r in reset_errors:
            test_type = r['test_name']
            reset_by_type[test_type] = reset_by_type.get(test_type, 0) + 1
        
        if reset_by_type:
            print("  • Padrão de reset por tipo de teste:")
            for test_type, count in reset_by_type.items():
                print(f"    - {test_type}: {count} resets")
    
    if timeout_errors and len(timeout_errors) > len(reset_errors):
        print("🟡 FIREWALL COM ANÁLISE LENTA:")
        print(f"  • {len(timeout_errors)} timeouts vs {len(reset_errors)} resets")
        print("  • DPI está analisando mas não decidindo rapidamente")
        print("  • Pode estar consultando listas de bloqueio externas")
    
    # Análise de padrões temporais
    consecutive_tests = [r for r in results if 'Consecutivas' in r['test_name']]
    if consecutive_tests:
        consecutive_success = sum(bool(r['server_response']) for r in consecutive_tests)
        if consecutive_success < len(consecutive_tests) * 0.5:
            print("🟠 RATE LIMITING DETECTADO:")
            print("  • Conexões consecutivas têm menor taxa de sucesso")
            print("  • Firewall pode ter rate limiting por IP/destino")
    
    # Análise de tipos de Client Hello
    minimal_results = [r for r in results if 'Mínimo' in r['test_name']]
    standard_results = [r for r in results if 'Padrão' in r['test_name']]
    legacy_results = [r for r in results if 'Legacy' in r['test_name']]
    
    minimal_success = sum(bool(r['server_response']) for r in minimal_results) if minimal_results else 0
    standard_success = sum(bool(r['server_response']) for r in standard_results) if standard_results else 0
    legacy_success = sum(bool(r['server_response']) for r in legacy_results) if legacy_results else 0
    
    if legacy_success > minimal_success > standard_success:
        print("🟢 FIREWALL PREFERE TLS LEGACY:")
        print("  • Client Hello mais antigo tem melhor taxa de sucesso")
        print("  • Firewall pode estar bloqueando features TLS modernas")
        print("  • Recomendação: Use TLS 1.2 com cipher suites básicos")
    
    elif minimal_success > standard_success:
        print("🟡 FIREWALL SENSÍVEL A COMPLEXIDADE:")
        print("  • Client Hello simplificado funciona melhor")
        print("  • Extensions ou cipher suites específicos podem estar sendo bloqueados")
        print("  • Recomendação: Minimize extensions TLS")
    
    # Análise de tamanho
    hello_sizes = [r.get('hello_size', 0) for r in results if r.get('hello_size')]
    if hello_sizes:
        min_size = min(hello_sizes)
        max_size = max(hello_sizes)
        print(f"\n📏 TAMANHOS DE CLIENT HELLO:")
        print(f"  • Mínimo: {min_size} bytes")
        print(f"  • Máximo: {max_size} bytes")
        if max_size - min_size > 200:
            print("  • Diferença significativa - pode afetar firewall")
    
    print("\n💡 RECOMENDAÇÕES:")
    print("-" * 20)
    
    # Recomendações baseadas nos resultados
    any_response = any(r['server_response'] for r in results)
    minimal_works = any(r['server_response'] for r in results if 'Mínimo' in r['test_name'])
    standard_fails = not any(r['server_response'] for r in results if 'Padrão' in r['test_name'])
    
    if minimal_works and standard_fails:
        print("✅ SOLUÇÃO ENCONTRADA:")
        print("  → Use Client Hello simplificado")
        print("  → Evite extensions TLS 1.3 modernas")
        print("  → Configure bibliotecas para TLS 1.2 básico")
        print("  → Exemplo: requests com ssl_context customizado")
    
    elif legacy_success > 0 and not minimal_works:
        print("✅ SOLUÇÃO LEGACY:")
        print("  → Use configurações TLS muito básicas")
        print("  → Cipher suites RSA clássicos apenas")
        print("  → Evite ECDHE e algoritmos modernos")
    
    if not any_response:
        print("❌ BLOQUEIO TOTAL DETECTADO:")
        print("  → Destino pode estar em blacklist corporativa")
        print("  → Solicite liberação formal ao time de segurança")
        print("  → Forneça justificativa de negócio para acesso")
        print("  → Considere usar proxy corporativo se disponível")
    
    if reset_errors and not timeout_errors:
        print("⚠️  FIREWALL AGRESSIVO:")
        print("  → Regras ativas bloqueando TLS específico")
        print("  → Teste com ferramentas padrão (curl, openssl)")
        print("  → Compare com acesso de outras aplicações")
        print("  → Documente comportamento para time de rede")
    
    # Recomendações específicas para Lambda
    print("\n🔧 PARA AWS LAMBDA:")
    print("  • Aumente timeout para 30s+ (firewalls corporativos são lentos)")
    print("  • Use retry com backoff exponencial")
    print("  • Considere VPC Endpoint se aplicável")
    print("  • Monitore via CloudWatch para padrões temporais")
    
    if minimal_works:
        print("  • Implemente TLSRawClient com configurações mínimas")
        print("  • Use como fallback quando requests/urllib3 falhar")
    
    return results

def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso:")
        print(f"  python {sys.argv[0]} <host> [porta]")
        print()
        print("Exemplos:")
        print(f"  python {sys.argv[0]} redestorehml.service-now.com")
        print(f"  python {sys.argv[0]} api.exemplo.com 8443")
        return
    
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443
    
    results = diagnose_corporate_firewall(host, port)
    
    # Salvar resultados para análise posterior
    timestamp = int(time.time())
    filename = f"firewall_diagnostic_{host.replace('.', '_')}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, default=str, indent=2)
    
    print(f"\n💾 Resultados salvos em: {filename}")
    print("📤 Envie este arquivo para o time de rede/segurança")

if __name__ == "__main__":
    main()
