#!/usr/bin/env python3
"""
Script de validação do projeto TLS Raw Client
Verifica se todos os arquivos estão presentes e funcionais
"""

import os
import sys
import json
import importlib.util
from pathlib import Path

def check_file_exists(filepath, description=""):
    """Verifica se arquivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {filepath} - {description}")
        return True
    else:
        print(f"❌ {filepath} - {description} (AUSENTE)")
        return False

def check_directory_structure():
    """Verifica estrutura de diretórios"""
    print("📁 Verificando estrutura de diretórios...")
    
    directories = [
        ("configs", "Arquivos de configuração"),
        ("tests", "Scripts de teste"),
        ("examples", "Exemplos de uso"),
        ("docs", "Documentação")
    ]
    
    all_good = True
    for dir_name, description in directories:
        if os.path.isdir(dir_name):
            print(f"✅ {dir_name}/ - {description}")
        else:
            print(f"❌ {dir_name}/ - {description} (AUSENTE)")
            all_good = False
    
    return all_good

def check_core_files():
    """Verifica arquivos principais"""
    print("\n📄 Verificando arquivos principais...")
    
    core_files = [
        ("tls_raw_client.py", "Cliente TLS base"),
        ("proxy_tls_client.py", "Cliente com suporte a proxy"),
        ("firewall_diagnostic.py", "Diagnósticos de firewall"),
        ("compare_openssl.py", "Comparação com OpenSSL"),
        ("lambda_integration.py", "Integração AWS Lambda"),
        ("proxy_setup_utility.py", "Utilitário de configuração"),
        ("README.md", "Documentação principal"),
        ("LICENSE", "Licença MIT"),
        ("CHANGELOG.md", "Histórico de mudanças"),
        ("CONTRIBUTING.md", "Guia de contribuição"),
        (".gitignore", "Arquivo gitignore"),
        ("requirements.txt", "Dependências Python")
    ]
    
    all_good = True
    for filename, description in core_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    return all_good

def check_config_files():
    """Verifica arquivos de configuração"""
    print("\n⚙️ Verificando configurações...")
    
    config_files = [
        ("configs/proxy_basic.json", "Proxy básico"),
        ("configs/proxy_auth.json", "Proxy com autenticação"),
        ("configs/lambda_proxy.json", "Configuração Lambda"),
        ("configs/security_proxy.json", "Proxy de segurança"),
        ("configs/dev_local.json", "Desenvolvimento local")
    ]
    
    all_good = True
    for filename, description in config_files:
        exists = check_file_exists(filename, description)
        if exists:
            # Validar JSON
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    required_fields = ["target_host", "target_port", "proxy_host", "proxy_port"]
                    missing = [field for field in required_fields if field not in config]
                    if missing:
                        print(f"   ⚠️ Campos ausentes: {missing}")
                    else:
                        print(f"   ✅ JSON válido")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON inválido: {e}")
                all_good = False
        else:
            all_good = False
    
    return all_good

def check_test_files():
    """Verifica arquivos de teste"""
    print("\n🧪 Verificando testes...")
    
    test_files = [
        ("tests/test_response_analysis.py", "Teste de análise de resposta"),
        ("tests/test_proxy_client.py", "Teste de cliente proxy"),
        ("tests/demo_config_files.py", "Demonstração de configurações")
    ]
    
    all_good = True
    for filename, description in test_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    return all_good

def check_example_files():
    """Verifica arquivos de exemplo"""
    print("\n💡 Verificando exemplos...")
    
    example_files = [
        ("examples/example_test.py", "Exemplo básico"),
        ("examples/complete_usage_example.py", "Exemplo completo")
    ]
    
    all_good = True
    for filename, description in example_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    return all_good

def check_documentation():
    """Verifica documentação"""
    print("\n📚 Verificando documentação...")
    
    doc_files = [
        ("docs/PROXY_README.md", "Documentação de proxy")
    ]
    
    all_good = True
    for filename, description in doc_files:
        if not check_file_exists(filename, description):
            all_good = False
    
    return all_good

def check_imports():
    """Verifica se módulos podem ser importados"""
    print("\n🐍 Verificando imports...")
    
    modules = [
        ("tls_raw_client", "TLSRawClient"),
        ("proxy_tls_client", "ProxyTLSClient"),
        ("firewall_diagnostic", "FirewallDiagnosticClient")
    ]
    
    all_good = True
    for module_name, class_name in modules:
        try:
            spec = importlib.util.spec_from_file_location(module_name, f"{module_name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name} - Importa corretamente")
            else:
                print(f"❌ {module_name}.{class_name} - Classe não encontrada")
                all_good = False
                
        except Exception as e:
            print(f"❌ {module_name} - Erro de import: {e}")
            all_good = False
    
    return all_good

def check_git_readiness():
    """Verifica se projeto está pronto para Git"""
    print("\n🔧 Verificando preparação para Git...")
    
    # Verificar .gitignore
    if os.path.exists('.gitignore'):
        print("✅ .gitignore presente")
        
        # Verificar se contém regras importantes
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            
        important_rules = ['__pycache__/', '*.pyc', '.env', '*.log']
        missing_rules = []
        
        for rule in important_rules:
            if rule not in gitignore_content:
                missing_rules.append(rule)
        
        if missing_rules:
            print(f"   ⚠️ Regras ausentes no .gitignore: {missing_rules}")
        else:
            print("   ✅ .gitignore com regras importantes")
    else:
        print("❌ .gitignore ausente")
        return False
    
    # Verificar se __pycache__ não está commitado
    if os.path.exists('__pycache__'):
        print("   ⚠️ __pycache__ presente (será ignorado pelo .gitignore)")
    else:
        print("   ✅ Sem __pycache__ para commitar")
    
    return True

def generate_project_summary():
    """Gera resumo do projeto"""
    print("\n📊 Resumo do Projeto")
    print("=" * 30)
    
    # Contar arquivos
    file_counts = {
        "Arquivos Python": len([f for f in os.listdir('.') if f.endswith('.py')]),
        "Configurações": len([f for f in os.listdir('configs') if f.endswith('.json')]) if os.path.exists('configs') else 0,
        "Testes": len([f for f in os.listdir('tests') if f.endswith('.py')]) if os.path.exists('tests') else 0,
        "Exemplos": len([f for f in os.listdir('examples') if f.endswith('.py')]) if os.path.exists('examples') else 0,
        "Documentação": len([f for f in os.listdir('docs') if f.endswith('.md')]) if os.path.exists('docs') else 0
    }
    
    for category, count in file_counts.items():
        print(f"{category}: {count}")
    
    # Calcular tamanho total
    total_size = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if not file.startswith('.') and not '__pycache__' in root:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
    
    print(f"Tamanho total: {total_size / 1024:.1f} KB")

def main():
    """Função principal"""
    print("🔍 TLS Raw Client - Validação do Projeto")
    print("=" * 45)
    
    checks = [
        check_directory_structure(),
        check_core_files(),
        check_config_files(),
        check_test_files(),
        check_example_files(),
        check_documentation(),
        check_imports(),
        check_git_readiness()
    ]
    
    all_passed = all(checks)
    
    generate_project_summary()
    
    print("\n" + "=" * 45)
    if all_passed:
        print("✅ PROJETO VALIDADO COM SUCESSO!")
        print("\n🚀 Pronto para upload no GitHub:")
        print("1. git init")
        print("2. git add .")
        print("3. git commit -m 'Initial commit: TLS Raw Client v1.0'")
        print("4. git remote add origin https://github.com/brunojet/tls-raw-client-test.git")
        print("5. git push -u origin main")
    else:
        print("❌ PROJETO COM PROBLEMAS - Corrija os erros acima")
        sys.exit(1)

if __name__ == "__main__":
    main()
