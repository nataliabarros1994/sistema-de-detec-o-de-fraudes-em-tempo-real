@echo off
REM ===================================================================
REM Script de Inicialização do Frontend - Sistema de Detecção de Fraudes
REM ===================================================================
REM Inicia o backend (API) e o frontend (Streamlit) automaticamente
REM
REM Uso: start_frontend.bat
REM
REM Autor: Natália Barros
REM Data: 2025
REM ===================================================================

echo =================================================================
echo 🚀 Sistema de Detecção de Fraudes - Inicialização
echo =================================================================
echo.

REM Verifica se está no diretório correto
if not exist "requirements.txt" (
    echo ❌ Erro: Execute este script na raiz do projeto
    pause
    exit /b 1
)

REM Verifica ambiente virtual
if not exist "venv" (
    echo ❌ Ambiente virtual não encontrado!
    echo 💡 Execute: python -m venv venv
    pause
    exit /b 1
)

REM Ativa ambiente virtual
echo 📦 Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verifica dependências
echo 🔍 Verificando dependências...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ⚠️  Streamlit não encontrado. Instalando dependências...
    pip install -r requirements.txt
)

REM Verifica Redis
echo 🐳 Verificando Redis...
docker ps | findstr redis >nul
if errorlevel 1 (
    echo 📡 Iniciando Redis com Docker...
    docker-compose up -d redis
    timeout /t 3 >nul
)

REM Verifica se a API já está rodando
echo 🔍 Verificando API...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API já está rodando
) else (
    echo 🚀 Iniciando API em background...
    if not exist "logs" mkdir logs
    start /B python start_api.py > logs\api.log 2>&1

    REM Aguarda API iniciar
    echo ⏳ Aguardando API iniciar...
    timeout /t 10 >nul

    curl -s http://localhost:8000/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ API iniciada com sucesso!
    ) else (
        echo ⚠️  API pode não ter iniciado corretamente
    )
)

echo.
echo =================================================================
echo ✅ Sistema Pronto!
echo =================================================================
echo.
echo 📡 API Backend:      http://localhost:8000
echo 📚 Documentação:     http://localhost:8000/docs
echo 🎨 Frontend:         http://localhost:8501
echo.
echo 💡 Pressione CTRL+C para parar
echo =================================================================
echo.

REM Inicia Frontend (Streamlit)
echo 🎨 Iniciando Dashboard Streamlit...
echo.
streamlit run frontend/app.py

echo.
echo 🛑 Sistema encerrado
pause
