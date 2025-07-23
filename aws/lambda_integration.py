#!/usr/bin/env python3
"""
Integração AWS Lambda - Exemplo de uso do Proxy TLS Client em ambiente serverless
Demonstra configuração via arquivos e variáveis de ambiente
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import logging
from typing import Dict, Any
from tlsraw.tls_raw_client import TLSRawClient

# Configurar logging para Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Copie todo o código da classe TLSRawClient aqui
# (o código do tls_raw_client.py)


def lambda_handler(event, context):
    """
    Handler do Lambda para diagnóstico TLS

    Event deve conter:
    {
        "host": "servidor.com",
        "port": 443,  // opcional, padrão 443
        "timeout": 30,  // opcional, padrão 30s
        "tests": ["sni", "no_sni", "multiple"]  // opcional
    }
    """

    try:
        # Extrair parâmetros do event
        host = event.get("host")
        if not host:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Host é obrigatório"}),
            }

        port = event.get("port", 443)
        timeout = event.get("timeout", 30.0)
        tests = event.get("tests", ["sni", "no_sni"])

        logger.info(f"Iniciando diagnóstico TLS para {host}:{port}")

        # Executar testes
        results = {
            "host": host,
            "port": port,
            "timeout": timeout,
            "timestamp": context.aws_request_id,
            "tests": {},
        }

        client = TLSRawClient(host, port, timeout)

        # Teste com SNI
        if "sni" in tests:
            logger.info("Executando teste com SNI")
            results["tests"]["with_sni"] = client.connect_and_test(use_sni=True)
            log_test_result("SNI Habilitado", results["tests"]["with_sni"])

        # Teste sem SNI
        if "no_sni" in tests:
            logger.info("Executando teste sem SNI")
            results["tests"]["without_sni"] = client.connect_and_test(use_sni=False)
            log_test_result("SNI Desabilitado", results["tests"]["without_sni"])

        # Múltiplos testes para identificar intermitências
        if "multiple" in tests:
            logger.info("Executando múltiplos testes")
            multiple_results = []
            for i in range(3):
                logger.info(f"Teste múltiplo {i+1}/3")
                result = client.connect_and_test(use_sni=True)
                multiple_results.append(result)
                log_test_result(f"Múltiplo {i+1}", result)

            results["tests"]["multiple"] = multiple_results
            results["analysis"] = analyze_multiple_results(multiple_results)

        # Análise e recomendações
        results["recommendations"] = generate_recommendations(results["tests"])

        logger.info("Diagnóstico TLS concluído com sucesso")

        return {"statusCode": 200, "body": json.dumps(results, default=str, indent=2)}

    except Exception as e:
        logger.error(f"Erro durante diagnóstico: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e), "type": type(e).__name__}),
        }


def log_test_result(test_name: str, result: Dict[str, Any]):
    """Log dos resultados de teste de forma organizada"""

    logger.info(f"=== {test_name} ===")

    # Status da conexão
    if result["connection_success"]:
        connect_time = result.get("connect_time", 0)
        logger.info(f"✅ Conexão TCP: OK ({connect_time:.3f}s)")
    else:
        logger.info("❌ Conexão TCP: FALHOU")

    # Client Hello
    if result["client_hello_sent"]:
        size = result.get("client_hello_size", 0)
        logger.info(f"✅ Client Hello: Enviado ({size} bytes)")
    else:
        logger.info("❌ Client Hello: NÃO ENVIADO")

    # Resposta do servidor
    if result["server_response"]:
        resp = result["server_response"]
        logger.info(f"📥 Resposta: {resp['type']}")

        if "handshake_type" in resp:
            logger.info(f"📋 Handshake: {resp['handshake_type']}")

            if resp["handshake_type"] == "Server Hello":
                logger.info("🎉 SUCESSO: Server Hello recebido!")

        if "alert_level" in resp:
            level = resp["alert_level"]
            desc = resp["alert_description"]
            if level == "Fatal":
                logger.error(f"🚨 ALERT FATAL: {desc}")
            else:
                logger.warning(f"⚠️ Alert: {level} - {desc}")

        logger.info(f"📊 Tamanho: {result.get('response_size', 0)} bytes")
    else:
        logger.warning("❌ Nenhuma resposta do servidor")

    # Erros
    if result["error"]:
        logger.error(f"❌ Erro: {result['error']}")

    logger.info("")


def analyze_multiple_results(results: list) -> Dict[str, Any]:
    """Analisa múltiplos resultados para identificar padrões"""

    analysis = {
        "total_tests": len(results),
        "tcp_success_rate": 0,
        "hello_success_rate": 0,
        "response_rate": 0,
        "consistent_behavior": True,
        "errors": [],
        "alerts": [],
    }

    tcp_successes = sum(1 for r in results if r["connection_success"])
    hello_successes = sum(1 for r in results if r["client_hello_sent"])
    response_successes = sum(1 for r in results if r["server_response"])

    analysis["tcp_success_rate"] = tcp_successes / len(results)
    analysis["hello_success_rate"] = hello_successes / len(results)
    analysis["response_rate"] = response_successes / len(results)

    # Coletar erros e alerts
    for result in results:
        if result.get("error"):
            analysis["errors"].append(result["error"])

        if result.get("server_response", {}).get("alert_description"):
            analysis["alerts"].append(result["server_response"]["alert_description"])

    # Verificar consistência
    if len(set(str(r.get("error")) for r in results)) > 1:
        analysis["consistent_behavior"] = False

    return analysis


def generate_recommendations(tests: Dict[str, Any]) -> list:
    """Gera recomendações baseadas nos resultados dos testes"""

    recommendations = []

    # Analisar teste com SNI
    sni_test = tests.get("with_sni")
    no_sni_test = tests.get("without_sni")

    if sni_test and no_sni_test:
        sni_success = sni_test.get("server_response") is not None
        no_sni_success = no_sni_test.get("server_response") is not None

        if no_sni_success and not sni_success:
            recommendations.append(
                {
                    "type": "SNI_ISSUE",
                    "message": "Servidor responde sem SNI mas falha com SNI",
                    "action": "Verificar configuração SNI do servidor",
                }
            )
        elif sni_success and not no_sni_success:
            recommendations.append(
                {
                    "type": "SNI_REQUIRED",
                    "message": "SNI é obrigatório para este servidor",
                    "action": "Sempre usar SNI nas conexões",
                }
            )

    # Analisar tipos de erro comuns
    all_results = []
    for test_results in tests.values():
        if isinstance(test_results, list):
            all_results.extend(test_results)
        else:
            all_results.append(test_results)

    # Verificar padrões de erro
    connection_failures = [r for r in all_results if not r.get("connection_success")]
    if connection_failures:
        recommendations.append(
            {
                "type": "NETWORK_ISSUE",
                "message": "Falhas de conexão TCP detectadas",
                "action": "Verificar conectividade de rede e firewall",
            }
        )

    # Verificar alerts TLS
    alerts = []
    for r in all_results:
        if r.get("server_response", {}).get("alert_description"):
            alerts.append(r["server_response"]["alert_description"])

    if "handshake_failure" in alerts:
        recommendations.append(
            {
                "type": "TLS_HANDSHAKE",
                "message": "Falha no handshake TLS detectada",
                "action": "Verificar cipher suites e versões TLS suportadas",
            }
        )

    if "protocol_version" in alerts:
        recommendations.append(
            {
                "type": "TLS_VERSION",
                "message": "Incompatibilidade de versão TLS",
                "action": "Ajustar versões TLS suportadas",
            }
        )

    # Verificar timeouts
    timeouts = [
        r for r in all_results if r.get("error", "").lower().find("timeout") != -1
    ]
    if timeouts:
        recommendations.append(
            {
                "type": "TIMEOUT",
                "message": "Timeouts detectados",
                "action": "Aumentar timeout ou verificar latência de rede",
            }
        )

    return recommendations


# Exemplo de event para teste local:
if __name__ == "__main__":
    # Para teste local
    class MockContext:
        aws_request_id = "test-request-123"

    test_event = {
        "host": "google.com",
        "port": 443,
        "timeout": 15,
        "tests": ["sni", "no_sni", "multiple"],
    }

    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
