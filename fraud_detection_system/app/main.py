"""
API FastAPI para Detecção de Fraudes em Tempo Real
===================================================
Este é o módulo principal da API REST que expõe endpoints para
detecção de fraudes em transações financeiras.

Endpoints principais:
- POST /predict: Analisa uma transação
- POST /predict/batch: Analisa múltiplas transações
- GET /user/{user_id}/history: Histórico do usuário
- GET /health: Status de saúde do sistema
- GET /metrics: Métricas Prometheus

Autor: Natália Barros
Data: 2025
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import time
import logging
from typing import List, Optional
from contextlib import asynccontextmanager
import os

from app.models import (
    Transaction, FraudPrediction, SystemHealth,
    BatchPredictionRequest, BatchPredictionResponse,
    UserHistory
)
from app.ml_model import FraudDetectionModel
from app.database import get_redis_client, close_redis_connection, RedisClient
from app.monitoring import (
    get_metrics_collector, get_prometheus_metrics,
    get_content_type, HealthChecker,
    log_prediction_result, log_api_request
)

# Importa endpoints empresariais
try:
    from app.enterprise_endpoints import router as enterprise_router
    ENTERPRISE_ENABLED = True
except ImportError:
    ENTERPRISE_ENABLED = False
    logger.warning("⚠️ Endpoints empresariais não disponíveis")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== CICLO DE VIDA DA APLICAÇÃO ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação (startup e shutdown)
    """
    # STARTUP
    logger.info("🚀 Iniciando API de Detecção de Fraudes...")

    try:
        # Inicializa Redis
        logger.info("📡 Conectando ao Redis...")
        app.state.redis_client = get_redis_client()

        # Inicializa e carrega o modelo ML
        logger.info("🤖 Carregando modelo de Machine Learning...")
        app.state.model = FraudDetectionModel(redis_client=app.state.redis_client)

        # Tenta carregar modelo treinado
        if app.state.model.load_model():
            logger.info("✅ Modelo carregado com sucesso!")

            # Atualiza métricas do modelo
            metrics_collector = get_metrics_collector()
            metrics_collector.set_model_info(
                version=app.state.model.model_version,
                trained_at=str(app.state.model.trained_at) if app.state.model.trained_at else None,
                features_count=len(app.state.model.feature_names) if app.state.model.feature_names else None
            )

            if app.state.model.metrics:
                metrics_collector.update_model_metrics(
                    accuracy=app.state.model.metrics.accuracy,
                    precision=app.state.model.metrics.precision,
                    recall=app.state.model.metrics.recall,
                    f1_score=app.state.model.metrics.f1_score
                )
        else:
            logger.warning("⚠️ Modelo não encontrado. Execute o treinamento primeiro!")
            logger.warning("   Use: python training/train_model.py")

        # Inicializa coletor de métricas
        app.state.metrics_collector = get_metrics_collector()

        # Atualiza status dos componentes
        health_status = HealthChecker.perform_full_health_check(
            model=app.state.model,
            redis_client=app.state.redis_client
        )

        logger.info("✅ API iniciada com sucesso!")
        logger.info(f"   📊 Status dos componentes: {health_status}")

    except Exception as e:
        logger.error(f"❌ Erro ao iniciar aplicação: {e}")
        raise

    yield  # Aplicação roda aqui

    # SHUTDOWN
    logger.info("👋 Encerrando API de Detecção de Fraudes...")

    try:
        # Fecha conexão com Redis
        close_redis_connection()
        logger.info("✅ Conexões fechadas com sucesso!")

    except Exception as e:
        logger.error(f"❌ Erro ao encerrar aplicação: {e}")


# ==================== APLICAÇÃO FASTAPI ====================

app = FastAPI(
    title="Sistema de Detecção de Fraudes",
    description="""
    API REST para detecção de fraudes em tempo real usando Machine Learning.

    ## Funcionalidades

    * **Análise de Transações**: Detecta fraudes com base em padrões comportamentais
    * **Histórico de Usuários**: Consulta histórico e estatísticas de transações
    * **Monitoramento**: Métricas Prometheus e health checks
    * **Cache Inteligente**: Redis para performance otimizada

    ## Como Usar

    1. Envie uma transação via POST /predict
    2. Receba análise completa com probabilidade de fraude
    3. Tome ação baseada no nível de risco retornado

    Desenvolvido por: Natália Barros
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Permite acesso de qualquer origem (configurar para produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui routers empresariais se disponíveis
if ENTERPRISE_ENABLED:
    app.include_router(enterprise_router)
    logger.info("✅ Endpoints empresariais habilitados")


# ==================== TEMPLATES E ARQUIVOS ESTÁTICOS ====================

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Mount static files if directory exists
if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ==================== MIDDLEWARE ====================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware que adiciona tempo de processamento ao header
    e registra métricas de requisições
    """
    start_time = time.time()

    # Processa a requisição
    response = await call_next(request)

    # Calcula tempo de processamento
    process_time = time.time() - start_time
    process_time_ms = process_time * 1000

    # Adiciona header com tempo de processamento
    response.headers["X-Process-Time-Ms"] = str(process_time_ms)

    # Registra métricas
    if hasattr(app.state, 'metrics_collector'):
        app.state.metrics_collector.record_http_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_seconds=process_time
        )

    # Log estruturado
    log_api_request(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
        duration_ms=process_time_ms
    )

    return response


# ==================== ENDPOINTS ====================

@app.get("/api", tags=["Info"])
@app.get("/api/info", tags=["Info"])
async def api_info():
    """
    Endpoint com informações da API (JSON)
    """
    return {
        "message": "API de Detecção de Fraudes em Tempo Real",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "web_interface": "/",
            "fraudguard_interface": "/fraudguard",
            "predict": "/predict",
            "batch_predict": "/predict/batch",
            "user_history": "/user/{user_id}/history",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        },
        "author": "Natália Barros"
    }


@app.get("/", response_class=HTMLResponse, tags=["Web Interface"], include_in_schema=False)
@app.get("/fraudguard", response_class=HTMLResponse, tags=["Web Interface"])
async def fraudguard_interface(request: Request):
    """
    Serve the FraudGuard® Risk Solutions HTML interface

    Professional web interface with:
    - Corporate branding with modern design
    - Interactive demo form for fraud detection
    - Real-time analysis with /predict API integration
    - Statistics dashboard (99.7% accuracy, <50ms response time)
    - Mobile-responsive Bootstrap 5 layout
    """
    return templates.TemplateResponse("fraudguard.html", {"request": request})


@app.post("/predict", response_model=FraudPrediction, tags=["Predições"])
async def predict_fraud(transaction: Transaction) -> FraudPrediction:
    """
    Analisa uma transação e retorna predição de fraude

    ## Exemplo de Requisição

    ```json
    {
      "transaction_id": "tx_001",
      "user_id": "user_123",
      "amount": 1500.00,
      "merchant": "Loja Suspeita",
      "category": "electronics",
      "location": "São Paulo, SP",
      "device": "device_mobile_001"
    }
    ```

    ## Resposta

    Retorna análise completa com:
    - Probabilidade de fraude
    - Nível de risco (low/medium/high)
    - Explicação da decisão
    - Fatores de risco identificados
    - Recomendações de ação
    """
    try:
        # Verifica se modelo está carregado
        if not app.state.model.is_loaded():
            raise HTTPException(
                status_code=503,
                detail="Modelo não está carregado. Aguarde inicialização ou execute treinamento."
            )

        # Verifica cache primeiro
        cached_prediction = app.state.redis_client.get_cached_prediction(
            transaction.transaction_id
        )

        if cached_prediction:
            logger.info(f"🎯 Retornando predição do cache: {transaction.transaction_id}")
            return cached_prediction

        # Realiza predição
        prediction = app.state.model.predict(transaction)

        # Cacheia resultado
        app.state.redis_client.cache_prediction(
            transaction.transaction_id,
            prediction,
            ttl=3600  # 1 hora
        )

        # Salva transação no histórico
        app.state.redis_client.save_transaction(
            user_id=transaction.user_id,
            transaction=transaction,
            is_fraud=prediction.is_fraud
        )

        # Atualiza métricas
        app.state.redis_client.increment_predictions_count()
        app.state.metrics_collector.record_prediction(
            is_fraud=prediction.is_fraud,
            fraud_probability=prediction.fraud_probability,
            processing_time_seconds=prediction.processing_time_ms / 1000
        )

        # Atualiza taxa de cache
        cache_hit_rate = app.state.redis_client.get_cache_hit_rate()
        app.state.metrics_collector.update_cache_metrics(cache_hit_rate)

        # Registra tempo de resposta
        app.state.redis_client.record_response_time(prediction.processing_time_ms)

        # Log estruturado
        log_prediction_result(
            transaction_id=transaction.transaction_id,
            is_fraud=prediction.is_fraud,
            fraud_probability=prediction.fraud_probability,
            processing_time_ms=prediction.processing_time_ms
        )

        return prediction

    except ValueError as e:
        logger.error(f"❌ Erro de validação: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"❌ Erro ao processar predição: {e}")
        app.state.metrics_collector.record_error('prediction_error')
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar predição: {str(e)}"
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Predições"])
async def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """
    Analisa múltiplas transações em lote

    ## Limite
    Máximo de 100 transações por requisição

    ## Retorno
    Lista com predições de todas as transações
    """
    try:
        if not app.state.model.is_loaded():
            raise HTTPException(
                status_code=503,
                detail="Modelo não está carregado."
            )

        start_time = time.time()

        # Processa cada transação
        predictions = app.state.model.predict_batch(request.transactions)

        # Salva transações e atualiza métricas
        fraud_count = 0
        for tx, pred in zip(request.transactions, predictions):
            # Salva no histórico
            app.state.redis_client.save_transaction(
                user_id=tx.user_id,
                transaction=tx,
                is_fraud=pred.is_fraud
            )

            # Conta fraudes
            if pred.is_fraud:
                fraud_count += 1

            # Atualiza métricas
            app.state.metrics_collector.record_prediction(
                is_fraud=pred.is_fraud,
                fraud_probability=pred.fraud_probability,
                processing_time_seconds=pred.processing_time_ms / 1000
            )

        # Tempo total de processamento
        total_time_ms = (time.time() - start_time) * 1000

        # Incrementa contador total
        for _ in range(len(predictions)):
            app.state.redis_client.increment_predictions_count()

        logger.info(
            f"📦 Lote processado: {len(predictions)} transações | "
            f"{fraud_count} fraudes detectadas | "
            f"Tempo: {total_time_ms:.1f}ms"
        )

        return BatchPredictionResponse(
            total_transactions=len(predictions),
            fraud_detected=fraud_count,
            predictions=predictions,
            processing_time_ms=total_time_ms
        )

    except Exception as e:
        logger.error(f"❌ Erro ao processar lote: {e}")
        app.state.metrics_collector.record_error('batch_prediction_error')
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/history", response_model=UserHistory, tags=["Usuários"])
async def get_user_history(user_id: str) -> UserHistory:
    """
    Recupera histórico e estatísticas de um usuário

    ## Informações Retornadas
    - Total de transações
    - Valor total transacionado
    - Taxa de fraude
    - Padrões de comportamento
    - Dispositivos conhecidos
    - Localizações e categorias mais comuns
    """
    try:
        history = app.state.redis_client.get_user_history(user_id)

        if history is None:
            raise HTTPException(
                status_code=404,
                detail=f"Usuário {user_id} não encontrado ou sem histórico"
            )

        logger.info(f"📊 Histórico recuperado para usuário {user_id}")

        return history

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"❌ Erro ao recuperar histórico: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=SystemHealth, tags=["Monitoramento"])
async def health_check() -> SystemHealth:
    """
    Verifica status de saúde do sistema

    ## Componentes Verificados
    - API
    - Modelo de ML
    - Redis

    ## Métricas Incluídas
    - Total de predições
    - Taxa de acerto do cache
    - Tempo médio de resposta
    """
    try:
        # Verifica status de todos os componentes
        health_status = HealthChecker.perform_full_health_check(
            model=app.state.model,
            redis_client=app.state.redis_client
        )

        # Determina status geral
        all_healthy = all(health_status.values())
        overall_status = "healthy" if all_healthy else "unhealthy"

        # Coleta métricas
        total_predictions = app.state.redis_client.get_total_predictions()
        cache_hit_rate = app.state.redis_client.get_cache_hit_rate()
        avg_response_time = app.state.redis_client.get_average_response_time()

        # Informações do modelo
        model_accuracy = None
        last_training = None

        if app.state.model.metrics:
            model_accuracy = app.state.model.metrics.accuracy

        if app.state.model.trained_at:
            last_training = app.state.model.trained_at

        return SystemHealth(
            status=overall_status,
            api_status="operational" if health_status['api'] else "error",
            model_status="operational" if health_status['model'] else "error",
            redis_status="operational" if health_status['redis'] else "error",
            total_predictions=total_predictions,
            cache_hit_rate=cache_hit_rate,
            average_response_time_ms=avg_response_time,
            model_version=app.state.model.model_version,
            model_accuracy=model_accuracy,
            last_training_date=last_training
        )

    except Exception as e:
        logger.error(f"❌ Erro no health check: {e}")
        return SystemHealth(
            status="unhealthy",
            api_status="error",
            model_status="error",
            redis_status="error",
            total_predictions=0,
            cache_hit_rate=0.0,
            average_response_time_ms=0.0
        )


@app.get("/metrics", tags=["Monitoramento"])
async def metrics() -> Response:
    """
    Retorna métricas no formato Prometheus

    ## Uso
    Configure seu Prometheus para fazer scraping deste endpoint:

    ```yaml
    scrape_configs:
      - job_name: 'fraud-detection'
        static_configs:
          - targets: ['localhost:8000']
        metrics_path: '/metrics'
    ```
    """
    try:
        # Atualiza taxa de cache antes de retornar métricas
        cache_hit_rate = app.state.redis_client.get_cache_hit_rate()
        app.state.metrics_collector.update_cache_metrics(cache_hit_rate)

        # Gera métricas Prometheus
        metrics_data = get_prometheus_metrics()

        return Response(
            content=metrics_data,
            media_type=get_content_type()
        )

    except Exception as e:
        logger.error(f"❌ Erro ao gerar métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["Monitoramento"])
async def get_stats():
    """
    Retorna estatísticas gerais do sistema

    Endpoint adicional para visualização rápida de métricas
    """
    try:
        summary = app.state.metrics_collector.get_summary()

        return {
            **summary,
            "cache_hit_rate": app.state.redis_client.get_cache_hit_rate(),
            "total_predictions": app.state.redis_client.get_total_predictions(),
            "avg_response_time_ms": app.state.redis_client.get_average_response_time()
        }

    except Exception as e:
        logger.error(f"❌ Erro ao gerar stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/cache/clear", tags=["Administração"])
async def clear_cache():
    """
    Limpa o cache de predições

    ⚠️ Use com cuidado em produção
    """
    try:
        success = app.state.redis_client.clear_cache()

        if success:
            return {"message": "Cache limpo com sucesso", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao limpar cache")

    except Exception as e:
        logger.error(f"❌ Erro ao limpar cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== TRATAMENTO DE ERROS ====================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Trata erros de validação"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "validation_error"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Trata erros gerais"""
    logger.error(f"❌ Erro não tratado: {exc}")
    app.state.metrics_collector.record_error('unhandled_error')

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "type": "internal_error"
        }
    )


# ==================== INICIALIZAÇÃO ====================

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("🚀 INICIANDO API DE DETECÇÃO DE FRAUDES")
    print("=" * 70)
    print("")
    print("📡 Servidor: http://0.0.0.0:8000")
    print("📚 Documentação: http://localhost:8000/docs")
    print("📖 Redoc: http://localhost:8000/redoc")
    print("")
    print("💡 Pressione CTRL+C para parar")
    print("=" * 70)
    print("")

    uvicorn.run(
        "app.main:app",  # CORRETO: módulo completo
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
