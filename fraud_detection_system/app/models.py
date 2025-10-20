"""
Modelos de Dados usando Pydantic
================================
Este módulo define todos os modelos de dados utilizados na API de detecção de fraudes.
Utilizamos Pydantic para validação automática e documentação da API.

Autor: Natália Barros
Data: 2025
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """
    Enum para níveis de risco de fraude
    - LOW: Baixo risco (< 30%)
    - MEDIUM: Risco médio (30-70%)
    - HIGH: Alto risco (> 70%)
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TransactionCategory(str, Enum):
    """
    Categorias de transações suportadas pelo sistema
    """
    ELECTRONICS = "electronics"
    FASHION = "fashion"
    FOOD = "food"
    TRAVEL = "travel"
    SERVICES = "services"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    OTHER = "other"


class Transaction(BaseModel):
    """
    Modelo de uma transação para análise de fraude

    Campos principais:
    - transaction_id: ID único da transação
    - user_id: ID do usuário que realizou a transação
    - amount: Valor da transação em reais
    - merchant: Nome do estabelecimento
    - category: Categoria da compra
    - location: Localização onde ocorreu a transação
    - device: Identificador do dispositivo usado
    - timestamp: Momento da transação (opcional, usa horário atual se não fornecido)
    """
    transaction_id: str = Field(..., description="ID único da transação", example="tx_001")
    user_id: str = Field(..., description="ID do usuário", example="user_123")
    amount: float = Field(..., gt=0, description="Valor da transação em reais", example=1500.00)
    merchant: str = Field(..., description="Nome do estabelecimento", example="Loja Eletrônicos")
    category: TransactionCategory = Field(..., description="Categoria da transação")
    location: str = Field(..., description="Localização da transação", example="São Paulo, SP")
    device: str = Field(..., description="Dispositivo usado", example="device_abc123")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Data/hora da transação")

    # Campos opcionais para análise avançada
    ip_address: Optional[str] = Field(None, description="Endereço IP da transação")
    user_agent: Optional[str] = Field(None, description="User agent do navegador/app")

    @validator('amount')
    def validate_amount(cls, v):
        """Valida que o valor da transação é positivo e razoável"""
        if v <= 0:
            raise ValueError('O valor deve ser maior que zero')
        if v > 1000000:  # Limite de 1 milhão
            raise ValueError('Valor excede o limite máximo permitido')
        return v

    class Config:
        """Configurações do modelo Pydantic"""
        json_schema_extra = {
            "example": {
                "transaction_id": "tx_001",
                "user_id": "user_123",
                "amount": 1500.00,
                "merchant": "Tech Store",
                "category": "electronics",
                "location": "São Paulo, SP",
                "device": "device_mobile_001",
                "timestamp": "2025-10-15T14:30:00"
            }
        }


class FraudPrediction(BaseModel):
    """
    Resposta da predição de fraude

    Contém:
    - transaction_id: ID da transação analisada
    - is_fraud: Booleano indicando se é fraude
    - fraud_probability: Probabilidade de ser fraude (0-1)
    - risk_level: Nível de risco classificado
    - confidence_score: Confiança do modelo na predição
    - explanation: Explicação human-readable da decisão
    - risk_factors: Lista de fatores que contribuíram para a decisão
    - recommendations: Ações recomendadas
    """
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "transaction_id": "tx_001",
                "is_fraud": True,
                "fraud_probability": 0.87,
                "risk_level": "high",
                "confidence_score": 0.92,
                "explanation": "Transação suspeita detectada: valor alto em localização não usual",
                "risk_factors": [
                    "Valor 3x acima da média do usuário",
                    "Localização nunca antes utilizada",
                    "Dispositivo desconhecido"
                ],
                "processing_time_ms": 45.2,
                "model_version": "1.0.0",
                "recommendations": [
                    "Bloquear transação e notificar usuário",
                    "Solicitar verificação adicional"
                ]
            }
        }
    )

    transaction_id: str = Field(..., description="ID da transação analisada")
    is_fraud: bool = Field(..., description="Se a transação é fraudulenta")
    fraud_probability: float = Field(..., ge=0, le=1, description="Probabilidade de fraude (0-1)")
    risk_level: RiskLevel = Field(..., description="Nível de risco")
    confidence_score: float = Field(..., ge=0, le=1, description="Confiança na predição")

    # Campos de explicabilidade
    explanation: str = Field(..., description="Explicação da decisão em linguagem natural")
    risk_factors: List[str] = Field(default_factory=list, description="Fatores de risco identificados")

    # Metadados
    processing_time_ms: float = Field(..., description="Tempo de processamento em milissegundos")
    model_version: str = Field(default="1.0.0", description="Versão do modelo usado")
    timestamp: datetime = Field(default_factory=datetime.now, description="Momento da análise")

    # Ações recomendadas
    recommendations: List[str] = Field(default_factory=list, description="Ações recomendadas")


class UserHistory(BaseModel):
    """
    Histórico de transações de um usuário

    Usado para análise de padrões e comportamento
    """
    user_id: str = Field(..., description="ID do usuário")
    total_transactions: int = Field(..., description="Total de transações")
    total_amount: float = Field(..., description="Valor total transacionado")
    average_amount: float = Field(..., description="Valor médio por transação")
    fraud_count: int = Field(default=0, description="Número de fraudes detectadas")
    fraud_rate: float = Field(default=0.0, description="Taxa de fraude (%)")
    last_transaction_date: Optional[datetime] = Field(None, description="Data da última transação")
    most_common_category: Optional[str] = Field(None, description="Categoria mais comum")
    most_common_location: Optional[str] = Field(None, description="Localização mais comum")
    known_devices: List[str] = Field(default_factory=list, description="Dispositivos conhecidos")

    class Config:
        """Configurações do modelo Pydantic"""
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "total_transactions": 145,
                "total_amount": 87500.00,
                "average_amount": 603.45,
                "fraud_count": 2,
                "fraud_rate": 1.38,
                "last_transaction_date": "2025-10-14T18:45:00",
                "most_common_category": "electronics",
                "most_common_location": "São Paulo, SP",
                "known_devices": ["device_mobile_001", "device_web_001"]
            }
        }


class SystemHealth(BaseModel):
    """
    Status de saúde do sistema

    Usado pelo endpoint /health para monitoramento
    """
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "status": "healthy",
                "timestamp": "2025-10-15T14:30:00",
                "api_status": "operational",
                "model_status": "operational",
                "redis_status": "operational",
                "total_predictions": 15847,
                "cache_hit_rate": 0.73,
                "average_response_time_ms": 42.5,
                "model_version": "1.0.0",
                "model_accuracy": 0.96,
                "last_training_date": "2025-10-10T08:00:00"
            }
        }
    )

    status: str = Field(..., description="Status geral (healthy/unhealthy)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Momento da verificação")

    # Status de componentes
    api_status: str = Field(default="operational", description="Status da API")
    model_status: str = Field(..., description="Status do modelo ML")
    redis_status: str = Field(..., description="Status do Redis")

    # Métricas de performance
    total_predictions: int = Field(default=0, description="Total de predições realizadas")
    cache_hit_rate: float = Field(default=0.0, ge=0, le=1, description="Taxa de acerto do cache")
    average_response_time_ms: float = Field(default=0.0, description="Tempo médio de resposta em ms")

    # Informações do modelo
    model_version: str = Field(default="1.0.0", description="Versão do modelo")
    model_accuracy: Optional[float] = Field(None, description="Acurácia do modelo")
    last_training_date: Optional[datetime] = Field(None, description="Data do último treinamento")


class BatchPredictionRequest(BaseModel):
    """
    Request para predições em lote

    Permite analisar múltiplas transações de uma vez
    """
    transactions: List[Transaction] = Field(..., description="Lista de transações para análise")

    @validator('transactions')
    def validate_batch_size(cls, v):
        """Valida o tamanho do lote"""
        if len(v) == 0:
            raise ValueError('É necessário fornecer pelo menos uma transação')
        if len(v) > 100:  # Limite de 100 transações por lote
            raise ValueError('O lote não pode conter mais de 100 transações')
        return v


class BatchPredictionResponse(BaseModel):
    """
    Resposta para predições em lote
    """
    total_transactions: int = Field(..., description="Total de transações analisadas")
    fraud_detected: int = Field(..., description="Número de fraudes detectadas")
    predictions: List[FraudPrediction] = Field(..., description="Lista de predições")
    processing_time_ms: float = Field(..., description="Tempo total de processamento em ms")

    class Config:
        """Configurações do modelo Pydantic"""
        json_schema_extra = {
            "example": {
                "total_transactions": 10,
                "fraud_detected": 3,
                "predictions": [],
                "processing_time_ms": 125.8
            }
        }


class ModelMetrics(BaseModel):
    """
    Métricas do modelo de Machine Learning

    Usado para monitoramento de performance
    """
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "accuracy": 0.96,
                "precision": 0.94,
                "recall": 0.92,
                "f1_score": 0.93,
                "auc_roc": 0.98,
                "true_positives": 920,
                "true_negatives": 9200,
                "false_positives": 58,
                "false_negatives": 80,
                "evaluation_date": "2025-10-15T14:30:00",
                "dataset_size": 10258
            }
        }
    )

    accuracy: float = Field(..., description="Acurácia do modelo")
    precision: float = Field(..., description="Precisão (positivos verdadeiros)")
    recall: float = Field(..., description="Recall (taxa de detecção)")
    f1_score: float = Field(..., description="F1-Score (média harmônica)")
    auc_roc: float = Field(..., description="Área sob a curva ROC")

    # Métricas de confusão
    true_positives: int = Field(..., description="Verdadeiros positivos")
    true_negatives: int = Field(..., description="Verdadeiros negativos")
    false_positives: int = Field(..., description="Falsos positivos")
    false_negatives: int = Field(..., description="Falsos negativos")

    # Metadados
    evaluation_date: datetime = Field(default_factory=datetime.now, description="Data da avaliação")
    dataset_size: int = Field(..., description="Tamanho do dataset de avaliação")
