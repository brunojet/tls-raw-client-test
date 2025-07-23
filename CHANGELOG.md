# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

## [1.0.0] - 2025-07-23

### Adicionado
- Cliente TLS raw base com implementação manual de handshake TLS 1.2/1.3
- Suporte completo a proxies corporativos com autenticação
- Sistema de configuração via arquivos JSON
- Análise automática de respostas (TLS, HTTP, SSH, FTP, firewall)
- Diagnóstico específico de firewalls corporativos
- Integração com AWS Lambda
- Detecção de SSL inspection
- Utilitário interativo de configuração de proxy
- Comparação com dumps OpenSSL para validação
- Sistema de logging detalhado
- Extração de informações de firewall/proxy
- Suporte a variáveis de ambiente
- Integração com AWS Parameter Store

### Recursos Principais
- **TLS Raw Client** (`tls_raw_client.py`): Cliente base com handshake manual
- **Proxy TLS Client** (`proxy_tls_client.py`): Extensão com suporte a proxy
- **Firewall Diagnostic** (`firewall_diagnostic.py`): Diagnósticos específicos
- **Lambda Integration** (`lambda_integration.py`): Pronto para AWS Lambda
- **Proxy Setup Utility** (`proxy_setup_utility.py`): Configuração interativa
- **OpenSSL Comparison** (`compare_openssl.py`): Validação contra OpenSSL

### Configurações Suportadas
- Proxy básico sem autenticação
- Proxy com autenticação Basic (usuário/senha)
- Configuração específica para AWS Lambda
- Configuração para ambientes com SSL inspection
- Templates para diferentes ambientes (dev, staging, prod)

### Funcionalidades de Diagnóstico
- Detecção automática de tipo de resposta
- Identificação de marcas de firewall (FortiGate, SonicWall, Cisco, etc.)
- Análise de problemas de conectividade
- Recomendações automáticas de solução
- Logs estruturados para troubleshooting

### Compatibilidade
- Python 3.6+
- Apenas bibliotecas padrão (sem dependências externas)
- AWS Lambda (todos os runtimes Python)
- Ambientes corporativos com proxy
- Redes com SSL inspection
