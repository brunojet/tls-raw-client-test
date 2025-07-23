#!/usr/bin/env python3
"""
Script de upload do projeto TLS Raw Client para GitHub
Automatiza o processo de inicialização do Git e upload
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Executa comando e mostra resultado"""
    print(f"🔄 {description}...")
    print(f"   Executando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} - Erro")
            if result.stderr.strip():
                print(f"   Erro: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ {description} - Exceção: {e}")
        return False

def check_git_installed():
    """Verifica se Git está instalado"""
    return run_command("git --version", "Verificando instalação do Git")

def initialize_git_repo():
    """Inicializa repositório Git"""
    if os.path.exists('.git'):
        print("⚠️ Repositório Git já existe")
        return True
    
    return run_command("git init", "Inicializando repositório Git")

def add_all_files():
    """Adiciona todos os arquivos"""
    return run_command("git add .", "Adicionando arquivos ao Git")

def create_initial_commit():
    """Cria commit inicial"""
    commit_message = "Initial commit: TLS Raw Client v1.0.0"
    return run_command(f'git commit -m "{commit_message}"', "Criando commit inicial")

def add_remote_origin():
    """Adiciona remote origin"""
    repo_url = "https://github.com/brunojet/tls-raw-client-test.git"
    
    # Primeiro verificar se remote já existe
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "origin" in result.stdout:
        print("⚠️ Remote origin já existe")
        return True
    
    return run_command(f'git remote add origin {repo_url}', "Adicionando remote origin")

def push_to_github():
    """Faz push para GitHub"""
    return run_command("git push -u origin main", "Fazendo push para GitHub")

def show_project_info():
    """Mostra informações do projeto"""
    print("\n📊 Informações do Projeto")
    print("=" * 30)
    print("Nome: TLS Raw Client")
    print("Versão: 1.0.0")
    print("Repositório: https://github.com/brunojet/tls-raw-client-test.git")
    print("Licença: MIT")
    
    # Mostrar estatísticas
    python_files = len([f for f in os.listdir('.') if f.endswith('.py')])
    print(f"Arquivos Python: {python_files}")
    
    if os.path.exists('configs'):
        config_files = len([f for f in os.listdir('configs') if f.endswith('.json')])
        print(f"Configurações: {config_files}")

def main():
    """Função principal"""
    print("🚀 TLS Raw Client - Upload para GitHub")
    print("=" * 40)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists('tls_raw_client.py'):
        print("❌ Execute este script no diretório raiz do projeto")
        sys.exit(1)
    
    show_project_info()
    
    print("\n🔧 Iniciando processo de upload...")
    
    steps = [
        (check_git_installed, "Git instalado"),
        (initialize_git_repo, "Repositório inicializado"),
        (add_all_files, "Arquivos adicionados"),
        (create_initial_commit, "Commit criado"),
        (add_remote_origin, "Remote configurado"),
        (push_to_github, "Upload concluído")
    ]
    
    for step_func, step_name in steps:
        if not step_func():
            print(f"\n❌ Falha na etapa: {step_name}")
            print("Verifique os erros acima e tente novamente")
            sys.exit(1)
    
    print("\n" + "=" * 40)
    print("✅ UPLOAD CONCLUÍDO COM SUCESSO!")
    print("\n🎉 Seu projeto está agora disponível em:")
    print("https://github.com/brunojet/tls-raw-client-test")
    print("\n📋 Próximos passos recomendados:")
    print("1. Acesse o repositório no GitHub")
    print("2. Configure GitHub Pages (se desejar)")
    print("3. Adicione badges ao README")
    print("4. Configure Actions para CI/CD")

if __name__ == "__main__":
    main()
