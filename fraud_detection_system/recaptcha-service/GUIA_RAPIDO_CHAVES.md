# ⚡ Guia Rápido - Remover Mensagem de Teste do reCAPTCHA

## 🎯 Objetivo: Eliminar "This reCAPTCHA is for testing purposes only"

---

## 📋 5 Passos Simples (~5 minutos)

### 1️⃣ OBTER CHAVES
Acesse: **https://www.google.com/recaptcha/admin/create**

Preencha:
- **Label:** FraudGuard Production
- **Tipo:** reCAPTCHA v2 → "I'm not a robot"
- **Domínios:** (um por linha)
  ```
  localhost
  127.0.0.1
  ```
- Marque: ☑️ Aceitar termos
- Clique: **Submit**

---

### 2️⃣ COPIAR AS 2 CHAVES

Você receberá:
```
Site Key:   6LcXXXXXXXXXXXXXXXXXXXXXXXXXX... (Cole no .env)
Secret Key: 6LcYYYYYYYYYYYYYYYYYYYYYYYYYY... (Cole no .env)
```

---

### 3️⃣ ATUALIZAR O ARQUIVO .env

**Abra:** `.env` no VS Code

**Localize:**
```bash
RECAPTCHA_SITE_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
RECAPTCHA_SECRET=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
```

**Substitua por suas chaves:**
```bash
RECAPTCHA_SITE_KEY=SUA_SITE_KEY_COPIADA_AQUI
RECAPTCHA_SECRET=SUA_SECRET_KEY_COPIADA_AQUI
```

**Salve:** Ctrl + S

---

### 4️⃣ REINICIAR SERVIDOR

**No terminal:**
```bash
cd recaptcha-service
npm start
```

Aguarde ver:
```
✅ reCAPTCHA Site Key: CONFIGURED
🚀 Server running on: http://localhost:3000
```

---

### 5️⃣ LIMPAR CACHE E TESTAR

**Limpe o cache:**
- Windows/Linux: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

**Acesse:**
```
http://localhost:3000/fraudguard.html
```

**Verifique:**
- ✅ reCAPTCHA aparece
- ✅ **Mensagem de teste SUMIU!**
- ✅ Funciona normalmente

---

## ✅ Checklist Rápido

- [ ] 1. Acessei https://www.google.com/recaptcha/admin/create
- [ ] 2. Criei novo site reCAPTCHA v2
- [ ] 3. Copiei Site Key e Secret Key
- [ ] 4. Atualizei arquivo `.env`
- [ ] 5. Salvei `.env` (Ctrl + S)
- [ ] 6. Reiniciei servidor (`npm start`)
- [ ] 7. Limpei cache (Ctrl + Shift + R)
- [ ] 8. Testei em http://localhost:3000/fraudguard.html
- [ ] 9. ✅ **Mensagem de teste NÃO aparece mais!**

---

## 🚨 Se Algo Der Errado

### Cache não limpo?
→ Abra em **janela anônima** (Ctrl + Shift + N)

### Servidor não reiniciou?
→ Pare com Ctrl + C e rode `npm start` novamente

### Chaves incorretas?
→ Verifique se não há espaços extras ao copiar

### Ainda com dúvidas?
→ Veja o guia completo em: **COMO_OBTER_CHAVES_PRODUCAO.md**

---

## 📍 Localização do Arquivo .env

```
/fraud_detection_system/recaptcha-service/.env
```

Já está aberto no seu VS Code! 👆

---

## ⏱️ Tempo Total: 5 minutos

**Pronto! Mensagem de teste eliminada e reCAPTCHA funcionando!** ✅
