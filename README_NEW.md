# 🚀 TLS Raw Client - Sistema Completo de Diagnóstico TLS

Sistema modular e extensível para diagnóstico de conectividade TLS em ambientes corporativos restritivos, especialmente para AWS Lambda. Implementa handshake TLS manual sem dependências administrativas.

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)

## 🎯 Problema Resolvido

**Cenário**: Conexões TLS em AWS Lambda sendo derrubadas após Client Hello em ambientes corporativos com proxy/firewall.

**Solução**: Cliente TLS raw que:
- ✅ Funciona sem bibliotecas que exigem privilégios administrativos
- ✅ Diagnóstica onde exatamente a conexão TLS falha
- ✅ Suporta proxies corporativos com autenticação
- ✅ Detecta e analisa respostas de firewall/proxy
- ✅ Gera logs detalhados para troubleshooting

## 📁 Estrutura do Projeto

```
tls-raw-client/
├── tls_raw_client.py           # ⭐ Cliente TLS base
├── proxy_tls_client.py         # 🔗 Extensão com suporte a proxy
├── firewall_diagnostic.py      # 🛡️ Diagnósticos específicos de firewall
├── compare_openssl.py          # 🔍 Comparação com OpenSSL
├── lambda_integration.py       # ☁️ Integração AWS Lambda
├── proxy_setup_utility.py      # ⚙️ Utilitário de configuração
├── configs/                    # 📁 Configurações de exemplo
│   ├── proxy_basic.json
│   ├── proxy_auth.json
│   ├── lambda_proxy.json
│   └── security_proxy.json
├── tests/                      # 🧪 Scripts de teste
│   ├── test_response_analysis.py
│   ├── test_proxy_client.py
│   └── demo_config_files.py
├── docs/                       # 📚 Documentação
│   └── PROXY_README.md
└── examples/                   # 💡 Exemplos de uso
    └── example_test.py
```

## 🚀 Início Rápido

### 1. Cliente TLS Básico
```python
from tls_raw_client import TLSRawClient

# Teste básico
client = TLSRawClient("www.google.com", 443)
result = client.connect_and_test()
print(f"Sucesso: {result['connection_success']}")
```

### 2. Cliente com Proxy Corporativo
```python
from proxy_tls_client import ProxyTLSClient

# Proxy com autenticação
client = ProxyTLSClient(
    host="api.externa.com",
    port=443,
    proxy_host="proxy.empresa.com",
    proxy_port=8080,
    proxy_username="usuario",
    proxy_password="senha"
)

result = client.connect_and_test()
```

### 3. Carregamento via Arquivo de Configuração
```python
from proxy_tls_client import ProxyTLSClient

# Carregar configuração de arquivo
client = ProxyTLSClient.from_config_file("configs/proxy_auth.json")
result = client.connect_and_test()
```

### 4. AWS Lambda
```python
# No lambda_integration.py
def lambda_handler(event, context):
    client = create_lambda_client(event)
    return client.connect_and_test()
```

## 🔧 Funcionalidades

### ✅ TLS Raw Client Base
- **Handshake Manual**: Implementação TLS 1.2/1.3 sem bibliotecas externas
- **Compatible OpenSSL**: Client Hello idêntico ao OpenSSL dump
- **Análise de Resposta**: Detecta TLS, HTTP, SSH, FTP, mensagens de firewall
- **Logging Detalhado**: Debug completo de todo o fluxo
- **SNI Support**: Server Name Indication configurável

### ✅ Suporte a Proxy
- **HTTP CONNECT**: Estabelecimento de túnel através de proxy
- **Autenticação Basic**: Usuário/senha para proxies corporativos
- **Configuração Flexível**: Arquivo JSON ou programática
- **Diagnóstico Automático**: Identificação de problemas comuns
- **SSL Inspection**: Detecção de interceptação de certificados

### ✅ Diagnósticos Avançados
- **Firewall Detection**: Identifica marcas de firewall (FortiGate, SonicWall, etc.)
- **Response Analysis**: Análise automática de qualquer resposta
- **Error Classification**: Categorização automática de erros
- **Troubleshooting**: Guias automáticos de resolução

### ✅ AWS Lambda Ready
- **Environment Variables**: Configuração via env vars
- **Parameter Store**: Integração com AWS SSM
- **CloudWatch Logs**: Logging otimizado para CloudWatch
- **VPC Support**: Funciona em Lambda com VPC

## 📊 Casos de Uso

### 🏢 Ambiente Corporativo
```bash
# Teste interativo de proxy
python proxy_setup_utility.py --interactive

# Diagnóstico completo
python proxy_setup_utility.py --config configs/proxy_auth.json --diagnose
```

### ☁️ AWS Lambda
```python
# Event para Lambda
{
  "test_type": "full",
  "proxy_config": {
    "target_host": "api.externa.com",
    "target_port": 443,
    "proxy_host": "proxy.empresa.com",
    "proxy_port": 8080,
    "proxy_username": "user",
    "proxy_password": "pass"
  }
}
```

### 🔍 Troubleshooting
```python
from firewall_diagnostic import FirewallDiagnosticClient

# Diagnóstico específico de firewall
client = FirewallDiagnosticClient("blocked-site.com", 443)
diagnosis = client.diagnose_corporate_firewall()
```

## 📋 Análise de Resultados

### ✅ Sucesso TLS
```json
{
  "connection_success": true,
  "client_hello_sent": true,
  "response_analysis": {
    "type": "TLS",
    "likely_source": "TLS Server"
  },
  "server_response": {
    "type": "Handshake",
    "handshake_type": "Server Hello"
  }
}
```

### ❌ Bloqueio de Firewall
```json
{
  "response_analysis": {
    "type": "HTTP",
    "likely_source": "Firewall/Content Filter"
  },
  "server_response": {
    "firewall_info": {
      "server": "FortiGate-100D",
      "firewall_brand": "fortigate",
      "firewall_keywords": "blocked, denied"
    }
  }
}
```

### ⚠️ SSL Inspection
```json
{
  "response_analysis": {
    "type": "TLS",
    "likely_source": "TLS Server"
  },
  "recommendations": [
    "Proxy retornou resposta HTTP - pode estar interceptando TLS",
    "Verificar configurações de SSL/TLS inspection no proxy"
  ]
}
```

## 🛠️ Configuração

### Arquivo de Configuração
```json
{
  "target_host": "api.externa.com",
  "target_port": 443,
  "proxy_host": "proxy.empresa.com",
  "proxy_port": 8080,
  "proxy_username": "DOMAIN\\usuario",
  "proxy_password": "senha",
  "timeout": 30
}
```

### Variáveis de Ambiente (Lambda)
```bash
TARGET_HOST=api.externa.com
TARGET_PORT=443
PROXY_HOST=proxy.empresa.com
PROXY_PORT=8080
PROXY_USERNAME=usuario
PROXY_PASSWORD=senha
PROXY_TIMEOUT=30
```

## 🧪 Testes

### Executar Todos os Testes
```bash
# Análise de resposta
python test_response_analysis.py

# Teste de proxy
python test_proxy_client.py

# Demonstração de configurações
python demo_config_files.py
```

### Teste com OpenSSL
```bash
# Comparar com dump OpenSSL
python compare_openssl.py --host www.google.com --compare
```

## 📚 Documentação

- **[PROXY_README.md](PROXY_README.md)** - Documentação completa do sistema de proxy
- **[Configurações de Exemplo](configs/)** - Templates para diferentes ambientes
- **[Exemplos de Uso](examples/)** - Scripts de demonstração

## 🔧 Requisitos

- **Python 3.6+**
- **Bibliotecas**: Apenas standard library (socket, struct, time, logging, typing)
- **AWS Lambda**: Compatível com qualquer runtime Python
- **Rede**: Funciona através de proxies corporativos

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- Inspirado na necessidade real de diagnosticar problemas TLS em ambientes corporativos
- Baseado em análise de dumps OpenSSL para máxima compatibilidade
- Testado em ambientes AWS Lambda corporativos

---

**Desenvolvido para resolver problemas reais de conectividade TLS em ambientes corporativos restritivos** 🚀
