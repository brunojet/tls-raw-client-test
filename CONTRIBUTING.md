# Contributing to TLS Raw Client

Obrigado por considerar contribuir para o TLS Raw Client! Este documento fornece diretrizes para contribuições.

## 🎯 Como Contribuir

### Reportando Bugs
1. Verifique se o bug já foi reportado nas [Issues](https://github.com/brunojet/tls-raw-client-test/issues)
2. Se não existir, crie uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Resultado esperado vs atual
   - Versão do Python e sistema operacional
   - Logs relevantes (com dados sensíveis removidos)

### Sugerindo Melhorias
1. Abra uma issue com tag "enhancement"
2. Descreva a funcionalidade desejada
3. Explique por que seria útil
4. Considere fornecer exemplos de uso

### Desenvolvendo

#### Setup do Ambiente
```bash
git clone https://github.com/brunojet/tls-raw-client-test.git
cd tls-raw-client-test
```

#### Executando Testes
```bash
# Testes básicos
python tests/test_response_analysis.py
python tests/test_proxy_client.py

# Teste com OpenSSL
python compare_openssl.py --host www.google.com

# Configuração interativa
python proxy_setup_utility.py --interactive
```

#### Processo de Desenvolvimento
1. Fork o repositório
2. Crie uma branch para sua feature:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
3. Implemente suas mudanças
4. Teste thoroughly
5. Commit com mensagens descritivas:
   ```bash
   git commit -m "feat: adiciona suporte a novo tipo de proxy"
   ```
6. Push para seu fork:
   ```bash
   git push origin feature/nova-funcionalidade
   ```
7. Abra um Pull Request

## 📝 Padrões de Código

### Style Guidelines
- Siga PEP 8 para estilo Python
- Use type hints quando possível
- Documente funções públicas com docstrings
- Mantenha linhas com máximo 100 caracteres
- Use nomes descritivos para variáveis e funções

### Exemplo de Função Bem Documentada
```python
def analyze_response(self, data: bytes) -> Dict[str, Any]:
    """
    Analisa qualquer resposta recebida para identificar o tipo
    
    Args:
        data: Dados brutos recebidos do servidor
        
    Returns:
        Dict com análise da resposta contendo:
        - likely_tls: bool indicando se é TLS válido
        - detected_type: string com tipo detectado
        - likely_source: string com fonte provável
        - preview: string com preview dos dados (se texto)
    
    Raises:
        ValueError: Se data estiver vazio
    """
```

### Estrutura de Arquivos
- **Core modules**: Arquivos principais na raiz
- **Tests**: Todos os testes em `tests/`
- **Examples**: Exemplos de uso em `examples/`
- **Configs**: Configurações de exemplo em `configs/`
- **Docs**: Documentação em `docs/`

## 🧪 Testes

### Tipos de Teste
1. **Unit Tests**: Testam funções individuais
2. **Integration Tests**: Testam fluxos completos
3. **Real Network Tests**: Testam conectividade real (opcional)

### Adicionando Novos Testes
- Coloque testes em `tests/`
- Use nomes descritivos como `test_new_feature.py`
- Inclua casos de sucesso e falha
- Teste edge cases

### Exemplo de Teste
```python
def test_tls_response_analysis():
    """Testa análise de resposta TLS válida"""
    client = TLSRawClient("example.com", 443)
    
    # TLS Server Hello simulado
    tls_data = bytes.fromhex("160303003502000031030364ce8c...")
    
    analysis = client.analyze_response(tls_data)
    
    assert analysis["likely_tls"] == True
    assert analysis["detected_type"] == "TLS Record"
    assert "TLS Server" in analysis["likely_source"]
```

## 🔐 Segurança

### Dados Sensíveis
- **NUNCA** commite credenciais reais
- Use placeholders em configurações de exemplo
- Mascare senhas em logs
- Remove dados sensíveis de issues/PRs

### Exemplo de Configuração Segura
```json
{
  "proxy_username": "SEU_USUARIO_AQUI",
  "proxy_password": "SUA_SENHA_AQUI",
  "_notes": "Substitua os valores acima pelos reais"
}
```

## 📚 Documentação

### Atualizando README
- Mantenha exemplos funcionais
- Atualize lista de funcionalidades
- Inclua novos casos de uso

### Documentando Novos Recursos
- Adicione exemplos práticos
- Explique quando usar
- Documente configurações necessárias
- Inclua troubleshooting comum

## 🏷️ Versionamento

Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Nova funcionalidade (compatível)
- **PATCH**: Bug fixes (compatível)

### Formato de Commits
- `feat:` Nova funcionalidade
- `fix:` Bug fix
- `docs:` Mudanças na documentação
- `test:` Adiciona/modifica testes
- `refactor:` Refatoração de código
- `chore:` Mudanças de build/configuração

## ❓ Dúvidas

### Canais de Comunicação
- **Issues**: Para bugs e feature requests
- **Discussions**: Para perguntas gerais
- **Pull Requests**: Para revisão de código

### FAQ

**Q: Posso adicionar dependências externas?**
A: Preferimos manter apenas stdlib. Se necessário, discuta primeiro em uma issue.

**Q: Como testar em ambiente corporativo?**
A: Use configurações de exemplo e ajuste para seu ambiente. Compartilhe casos de uso interessantes.

**Q: Posso contribuir com novos tipos de proxy?**
A: Sim! Especialmente protocolos corporativos como NTLM, Kerberos, etc.

## 🙏 Reconhecimento

Contribuições são reconhecidas no README e CHANGELOG. Grandes contribuições podem ser mencionadas especialmente.

---

**Obrigado por contribuir! Sua ajuda torna este projeto melhor para toda a comunidade.** 🚀
