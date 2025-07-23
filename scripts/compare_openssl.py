#!/usr/bin/env python3
"""
Script para testar e comparar o Client Hello gerado com o dump do OpenSSL
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tlsraw.tls_raw_client import TLSRawClient
import binascii

def parse_openssl_dump():
    """Parse do dump do OpenSSL para comparação"""
    
    # Client Hello do dump OpenSSL (redestorehml.service-now.com)
    openssl_hex = """
    01 00 01 41 03 03 6e 0a 72 01 af b9 09 df 1b 8b
    27 ae 26 0b 0a 53 be 96 52 51 f2 d4 d0 f4 8f 15
    e0 e1 43 77 b7 e0 20 01 94 35 6a ce 37 69 87 54
    19 4e 72 0d 0a 49 67 20 08 ae 61 72 8b 4d f3 c3
    e8 8a f7 ce a8 94 d8 00 3e 13 02 13 03 13 01 c0
    2c c0 30 00 9f cc a9 cc a8 cc aa c0 2b c0 2f 00
    9e c0 24 c0 28 00 6b c0 23 c0 27 00 67 c0 0a c0
    14 00 39 c0 09 c0 13 00 33 00 9d 00 9c 00 3d 00
    3c 00 35 00 2f 00 ff 01 00 00 ba 00 00 00 21 00
    1f 00 00 1c 72 65 64 65 73 74 6f 72 65 68 6d 6c
    2e 73 65 72 76 69 63 65 2d 6e 6f 77 2e 63 6f 6d
    00 0b 00 04 03 00 01 02 00 0a 00 16 00 14 00 1d
    00 17 00 1e 00 19 00 18 01 00 01 01 01 02 01 03
    01 04 00 23 00 00 00 16 00 00 00 17 00 00 00 0d
    00 2a 00 28 04 03 05 03 06 03 08 07 08 08 08 09
    08 0a 08 0b 08 04 08 05 08 06 04 01 05 01 06 01
    03 03 03 01 03 02 04 02 05 02 06 02 00 2b 00 05
    04 03 04 03 03 00 2d 00 02 01 01 00 33 00 26 00
    24 00 1d 00 20 8b 0a 78 3d e2 72 4f 2e b4 a8 86
    a5 af 60 68 fb 9c b0 2f 32 58 9e 83 3b e6 87 94
    75 79 b7 ec 1e
    """.replace('\n', '').replace(' ', '')
    
    return bytes.fromhex(openssl_hex)

def analyze_client_hello(data):
    """Analisa a estrutura do Client Hello"""
    
    print("=== ANÁLISE DO CLIENT HELLO ===")
    print(f"Tamanho total: {len(data)} bytes")
    print(f"Hex: {data.hex()}")
    print()
    
    if len(data) < 6:
        print("Dados insuficientes")
        return
    
    # Parse da estrutura
    pos = 0
    
    # Handshake Type
    handshake_type = data[pos]
    print(f"Handshake Type: 0x{handshake_type:02x} ({'Client Hello' if handshake_type == 1 else 'Unknown'})")
    pos += 1
    
    # Length (3 bytes)
    length = int.from_bytes(data[pos:pos+3], 'big')
    print(f"Length: {length} bytes")
    pos += 3
    
    # TLS Version
    version = int.from_bytes(data[pos:pos+2], 'big')
    print(f"TLS Version: 0x{version:04x} (TLS {version>>8}.{version&0xFF})")
    pos += 2
    
    # Client Random (32 bytes)
    client_random = data[pos:pos+32]
    print(f"Client Random: {client_random.hex()}")
    pos += 32
    
    # Session ID Length
    session_id_len = data[pos]
    print(f"Session ID Length: {session_id_len}")
    pos += 1
    
    if session_id_len > 0:
        session_id = data[pos:pos+session_id_len]
        print(f"Session ID: {session_id.hex()}")
        pos += session_id_len
    
    # Cipher Suites Length
    if pos + 2 <= len(data):
        cipher_suites_len = int.from_bytes(data[pos:pos+2], 'big')
        print(f"Cipher Suites Length: {cipher_suites_len}")
        pos += 2
        
        # Cipher Suites
        cipher_suites = data[pos:pos+cipher_suites_len]
        print(f"Cipher Suites ({cipher_suites_len//2} suites):")
        for i in range(0, cipher_suites_len, 2):
            suite = int.from_bytes(cipher_suites[i:i+2], 'big')
            print(f"  0x{suite:04x}")
        pos += cipher_suites_len
    
    # Compression Methods
    if pos < len(data):
        comp_len = data[pos]
        print(f"Compression Methods Length: {comp_len}")
        pos += 1
        
        if comp_len > 0:
            comp_methods = data[pos:pos+comp_len]
            print(f"Compression Methods: {comp_methods.hex()}")
            pos += comp_len
    
    # Extensions
    if pos + 2 <= len(data):
        ext_len = int.from_bytes(data[pos:pos+2], 'big')
        print(f"Extensions Length: {ext_len}")
        pos += 2
        
        print("Extensions:")
        ext_pos = pos
        while ext_pos < pos + ext_len:
            ext_type = int.from_bytes(data[ext_pos:ext_pos+2], 'big')
            ext_pos += 2
            ext_data_len = int.from_bytes(data[ext_pos:ext_pos+2], 'big')
            ext_pos += 2
            
            ext_names = {
                0x0000: "Server Name",
                0x000a: "Supported Groups", 
                0x000b: "EC Point Formats",
                0x000d: "Signature Algorithms",
                0x0016: "Encrypt-then-MAC",
                0x0017: "Extended Master Secret",
                0x0023: "Session Ticket",
                0x002b: "Supported Versions",
                0x002d: "PSK Key Exchange Modes",
                0x0033: "Key Share"
            }
            
            ext_name = ext_names.get(ext_type, f"Unknown (0x{ext_type:04x})")
            print(f"  {ext_name}: {ext_data_len} bytes")
            
            ext_pos += ext_data_len

def test_against_openssl():
    """Testa nosso cliente contra o dump do OpenSSL"""
    
    print("🔍 COMPARANDO NOSSO CLIENT HELLO COM OPENSSL")
    print("=" * 60)
    
    # Client Hello do OpenSSL
    openssl_data = parse_openssl_dump()
    print("📥 CLIENT HELLO DO OPENSSL:")
    analyze_client_hello(openssl_data)
    
    print("\n" + "=" * 60 + "\n")
    
    # Nosso Client Hello
    client = TLSRawClient("redestorehml.service-now.com", 443)
    our_record = client.create_client_hello("redestorehml.service-now.com")
    
    # Extrair apenas o handshake (sem TLS record header)
    our_handshake = our_record[5:]  # Skip 5 bytes do TLS record header
    
    print("📤 NOSSO CLIENT HELLO:")
    analyze_client_hello(our_handshake)
    
    print("\n" + "=" * 60 + "\n")
    
    # Comparação de tamanhos
    print("📊 COMPARAÇÃO DE TAMANHOS:")
    print(f"OpenSSL:  {len(openssl_data)} bytes")
    print(f"Nosso:    {len(our_handshake)} bytes")
    print(f"Diferença: {len(our_handshake) - len(openssl_data)} bytes")
    
    # Teste de conectividade
    print("\n🌐 TESTE DE CONECTIVIDADE:")
    print("-" * 30)
    
    results = client.connect_and_test(use_sni=True)
    
    tcp_status = "✅" if results['connection_success'] else "❌"
    hello_status = "✅" if results['client_hello_sent'] else "❌"
    response_status = "✅" if results['server_response'] else "❌"
    
    print(f"TCP Connection: {tcp_status}")
    print(f"Client Hello Sent: {hello_status}")
    print(f"Server Response: {response_status}")
    
    if results['error']:
        print(f"❌ Erro: {results['error']}")
    
    if results['server_response']:
        resp = results['server_response']
        print(f"📥 Resposta: {resp['type']}")
        
        if 'handshake_type' in resp:
            if resp['handshake_type'] == 'Server Hello':
                print("🎉 SUCESSO! Server Hello recebido!")
            else:
                print(f"📋 Handshake: {resp['handshake_type']}")
        
        if 'alert_level' in resp:
            print(f"⚠️ Alert: {resp['alert_level']} - {resp['alert_description']}")

if __name__ == "__main__":
    test_against_openssl()
