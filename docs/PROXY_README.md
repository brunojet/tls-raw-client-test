# 🚀 Proxy TLS Client - Sistema Completo para Ambientes Corporativos

Sistema modular e extensível para diagnóstico de conectividade TLS através de proxies corporativos. Baseado no TLS Raw Client, adiciona suporte completo a proxies HTTP CONNECT com autenticação.

## 📋 Funcionalidades

### ✅ Suporte a Proxy
- **Proxy HTTP CONNECT**: Estabelecimento de túnel através de proxy
- **Autenticação Basic**: Suporte a usuário/senha 
- **Configuração Flexível**: Host, porta, credenciais, timeout
- **Herança Completa**: Todas as funcionalidades do TLS Raw Client

### ✅ Diagnóstico Avançado
- **Teste de Conectividade**: Verificação básica do proxy
- **Análise de Resposta**: Detecção de TLS, HTTP, mensagens de firewall
- **Diagnóstico Automático**: Identificação de problemas comuns
- **Logging Detalhado**: Debug completo de todo o fluxo

### ✅ Ambientes Corporativos
- **SSL Inspection**: Detecção de interceptação de certificados
- **Firewall Detection**: Identificação de mensagens de firewall/proxy
- **Múltiplas Configurações**: Suporte a diferentes tipos de proxy
- **Troubleshooting**: Guia automático de resolução de problemas

## 📁 Arquivos do Sistema

```
proxy_tls_client.py          # Cliente principal com suporte a proxy
test_proxy_client.py         # Testes e demonstrações
proxy_setup_utility.py       # Utilitário de configuração interativa
proxy_config_examples.json   # Exemplos e guia de configuração
```

## 🚀 Uso Rápido

### 1. Uso Básico Programático

```python
from proxy_tls_client import ProxyTLSClient

# Proxy sem autenticação
client = ProxyTLSClient(
    host="api.externa.com",
    port=443,
    proxy_host="proxy.empresa.com",
    proxy_port=8080
)

result = client.connect_and_test()
print(f"Sucesso: {result['connection_success']}")
```

### 2. Proxy com Autenticação

```python
# Proxy com autenticação
client = ProxyTLSClient(
    host="secure-api.com",
    port=443,
    proxy_host="proxy.corp.com", 
    proxy_port=3128,
    proxy_username="usuario@empresa.com",
    proxy_password="senha_corporativa"
)

# Diagnóstico completo
diagnosis = client.diagnose_proxy_issues()
```

### 3. Configuração via Dicionário

```python
from proxy_tls_client import create_proxy_client_from_config

config = {
    "target_host": "api.service.com",
    "target_port": 443,
    "proxy_host": "proxy.empresa.com",
    "proxy_port": 8080,
    "proxy_username": "user",
    "proxy_password": "pass",
    "timeout": 30
}

client = create_proxy_client_from_config(config)
result = client.connect_and_test()
```

## 🛠️ Utilitário de Configuração

### Modo Interativo
```bash
python proxy_setup_utility.py --interactive
```

### Teste de Configuração
```bash
python proxy_setup_utility.py --config minha_config.json --test
```

### Diagnóstico Completo
```bash
python proxy_setup_utility.py --config minha_config.json --diagnose
```

### Exemplos e Ajuda
```bash
python proxy_setup_utility.py --examples
python proxy_setup_utility.py --troubleshoot
```

## 📋 Configurações Típicas

### Proxy Corporativo Básico
```json
{
  "target_host": "api.external.com",
  "target_port": 443,
  "proxy_host": "proxy.empresa.com",
  "proxy_port": 8080,
  "timeout": 30
}
```

### Proxy com Autenticação Windows
```json
{
  "target_host": "secure-api.com",
  "target_port": 443,
  "proxy_host": "proxy.corp.local",
  "proxy_port": 3128,
  "proxy_username": "DOMAIN\\username",
  "proxy_password": "password",
  "timeout": 45
}
```

### Proxy com SSL Inspection
```json
{
  "target_host": "external-service.com",
  "target_port": 443,
  "proxy_host": "ssl-proxy.company.com",
  "proxy_port": 8443,
  "proxy_username": "user@company.com", 
  "proxy_password": "complex_password",
  "timeout": 60
}
```

## 🔍 Análise de Resultados

### Resultado Bem-Sucedido
```python
{
  "connection_success": True,
  "proxy_connection_success": True,
  "connect_tunnel_success": True,
  "client_hello_sent": True,
  "response_size": 517,
  "response_analysis": {
    "type": "TLS",
    "likely_source": "TLS Server",
    "likely_tls": True
  }
}
```

### Problema de Autenticação
```python
{
  "connection_success": False,
  "proxy_connection_success": True,
  "connect_tunnel_success": False,
  "error": "407 Proxy Authentication Required"
}
```

### SSL Inspection Detectado
```python
{
  "response_analysis": {
    "type": "HTTP",
    "likely_source": "Proxy/Firewall",
    "details": "SSL inspection detected"
  },
  "firewall_info": {
    "server": "BlueCoat-ProxySG",
    "firewall_brand": "bluecoat"
  }
}
```

## 🛠️ Resolução de Problemas

### 1. Connection Refused
**Problema**: `Connection refused to proxy`
**Soluções**:
- Verificar proxy_host e proxy_port
- Confirmar conectividade de rede
- Testar: `telnet proxy_host proxy_port`

### 2. Authentication Failed  
**Problema**: `407 Proxy Authentication Required`
**Soluções**:
- Verificar username/password
- Testar formato DOMAIN\\user se necessário
- Confirmar se conta não está bloqueada

### 3. Method Not Allowed
**Problema**: `405 Method Not Allowed`  
**Soluções**:
- Proxy não suporta CONNECT method
- Verificar configurações de HTTPS no proxy
- Contatar administrador de rede

### 4. SSL Interception
**Problema**: Certificate verification failed
**Soluções**:
- Proxy está fazendo SSL inspection
- Certificado substituído pelo do proxy
- Normal em ambientes corporativos

## 🔧 Funcionalidades Avançadas

### Diagnóstico Automático
```python
client = ProxyTLSClient(host, port, proxy_host, proxy_port, user, pass)
diagnosis = client.diagnose_proxy_issues()

# Análise automática com recomendações
if diagnosis['recommendations']:
    for rec in diagnosis['recommendations']:
        print(f"💡 {rec}")
```

### Análise de Firewall
```python
result = client.connect_and_test()

if result['server_response']['type'] == 'Non-TLS Response':
    firewall_info = result['server_response']['firewall_info']
    
    if 'firewall_brand' in firewall_info:
        print(f"🔥 Firewall detectado: {firewall_info['firewall_brand']}")
    
    if 'server' in firewall_info:
        print(f"🖥️ Servidor: {firewall_info['server']}")
```

### Logging Detalhado
```python
import logging

# Configurar logging para debug detalhado
logging.basicConfig(level=logging.DEBUG)

client = ProxyTLSClient(...)
result = client.connect_and_test()

# Logs incluem:
# - Conectividade proxy
# - Requisição CONNECT  
# - Resposta do proxy
# - Handshake TLS
# - Análise de resposta
```

## 🎯 Casos de Uso

### 1. **Desenvolvimento em Ambiente Corporativo**
- Testar APIs externas através de proxy corporativo
- Verificar se SSL inspection está ativo
- Debug de problemas de conectividade

### 2. **Deploy em AWS Lambda**
- Configurar Lambda para usar proxy corporativo
- Diagnosticar conexões que falham após Client Hello
- Identificar bloqueios de firewall

### 3. **Troubleshooting de Rede**
- Identificar onde conexões TLS estão falhando
- Distinguir entre problemas de proxy vs destino
- Coletar evidências para equipes de rede

### 4. **Testes de Integração**
- Validar conectividade antes de deploy
- Testar diferentes configurações de proxy
- Automatizar verificações de rede

## 🏗️ Arquitetura

```
TLSRawClient (base)
    ↓ herda
ProxyTLSClient (extensão)
    ↓ usa
proxy_setup_utility (ferramenta)
    ↓ configura
proxy_config_examples (templates)
```

### Extensibilidade
- **Herança Limpa**: ProxyTLSClient herda todo TLSRawClient
- **Modular**: Cada funcionalidade em arquivo separado
- **Configurável**: JSON para diferentes ambientes
- **Testável**: Scripts de teste independentes

## 📊 Saída de Exemplo

```
🧪 Testando configuração:
   Proxy: proxy.empresa.com:8080
   Destino: api.github.com:443
   Auth: Sim

1️⃣ Testando conectividade com proxy...
   ✅ Conexão com proxy: OK (0.045s)
   ✅ Método CONNECT: OK

2️⃣ Testando handshake TLS através do proxy...
   ✅ Túnel proxy: OK
   ✅ Client Hello enviado: OK
   ✅ Resposta recebida: 517 bytes
   📊 Tipo: TLS
   📊 Fonte: TLS Server
   ✅ Handshake TLS bem-sucedido!

✅ Teste completo bem-sucedido!
```

## 🚀 Próximos Passos

1. **Configurar seu ambiente**:
   ```bash
   python proxy_setup_utility.py --interactive
   ```

2. **Testar conectividade**:
   ```bash
   python proxy_setup_utility.py --config minha_config.json --test
   ```

3. **Executar diagnóstico**:
   ```bash
   python proxy_setup_utility.py --config minha_config.json --diagnose
   ```

4. **Integrar em seu código**:
   ```python
   from proxy_tls_client import ProxyTLSClient
   # ... usar conforme exemplos acima
   ```

## 💡 Dicas Importantes

- **Sempre teste conectividade básica primeiro**
- **Use logging DEBUG para troubleshooting detalhado**
- **SSL inspection é comum em ambientes corporativos**
- **Salve configurações funcionais para reutilização**
- **Verifique timeouts em redes lentas**
- **Documente configurações específicas do seu ambiente**

---

**Sistema desenvolvido para máxima compatibilidade com ambientes corporativos restritivos, mantendo todas as capacidades de diagnóstico TLS do cliente base.**
