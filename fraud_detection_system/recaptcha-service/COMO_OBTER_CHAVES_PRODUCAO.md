# 🔑 Como Obter Chaves de Produção do reCAPTCHA

## 🎯 Objetivo

**MANTER** o reCAPTCHA funcionando (proteção anti-bot)
**REMOVER** a mensagem "This reCAPTCHA is for testing purposes only"

---

## 📋 Passo a Passo Completo

### PASSO 1: Acessar o Google reCAPTCHA Admin

1. **Abra seu navegador** e acesse:
   ```
   https://www.google.com/recaptcha/admin/create
   ```

2. **Faça login** com sua conta Google (Gmail)

---

### PASSO 2: Criar Novo Site reCAPTCHA

Você verá um formulário. Preencha assim:

#### 📝 Campo 1: Label (Rótulo)
```
FraudGuard Production
```
*Ou qualquer nome que você quiser - é só para identificação*

#### 📝 Campo 2: reCAPTCHA type (Tipo)
Selecione:
```
☑️ reCAPTCHA v2
```

Depois, escolha o subtipo:
```
☑️ "I'm not a robot" Checkbox
```

#### 📝 Campo 3: Domains (Domínios)

Adicione **UM POR LINHA**:
```
localhost
127.0.0.1
```

**Se você tiver um domínio de produção**, adicione também:
```
seusite.com
www.seusite.com
```

**Exemplo completo:**
```
localhost
127.0.0.1
fraudguard.com.br
www.fraudguard.com.br
```

#### 📝 Campo 4: Accept the reCAPTCHA Terms of Service
```
☑️ Marque a caixa para aceitar os termos
```

#### 📝 Campo 5: Alertas (Opcional)
```
☐ Enviar alertas para proprietários
```
*Você pode deixar desmarcado por enquanto*

---

### PASSO 3: Submeter e Obter as Chaves

1. Clique no botão **"Submit"** (Enviar)

2. Você verá uma tela com **2 chaves importantes**:

```
┌─────────────────────────────────────────────────────────┐
│ ✅ Your site is ready to use reCAPTCHA v2              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Site Key (Chave do Site)                               │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 6Lc... (exemplo: 40 caracteres)                 │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ Secret Key (Chave Secreta)                             │
│ ┌─────────────────────────────────────────────────┐   │
│ │ 6Lc... (exemplo: 40 caracteres)                 │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

3. **COPIE AMBAS AS CHAVES** - você vai precisar delas!

---

### PASSO 4: Atualizar o Arquivo .env

1. **Abra o arquivo `.env`** no VS Code:
   ```
   /fraud_detection_system/recaptcha-service/.env
   ```

2. **Localize estas linhas:**
   ```bash
   # Test Site Key (visible in browser) - SHOWS WARNING "For testing purposes only"
   RECAPTCHA_SITE_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
   # Test Secret Key (server-side only)
   RECAPTCHA_SECRET=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
   ```

3. **SUBSTITUA** pelas suas novas chaves:

   **ANTES (Chaves de Teste):**
   ```bash
   RECAPTCHA_SITE_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
   RECAPTCHA_SECRET=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe
   ```

   **DEPOIS (Suas Chaves de Produção):**
   ```bash
   RECAPTCHA_SITE_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   RECAPTCHA_SECRET=6LcYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
   ```

   *Cole as chaves que você copiou do Google*

4. **Salve o arquivo** (Ctrl + S)

---

### PASSO 5: Reiniciar o Servidor

**No terminal do VS Code**, execute:

```bash
# Pare o servidor atual (Ctrl + C se estiver rodando)

# Navegue até a pasta do serviço
cd "/home/nataliabarros1994/Downloads/🚀 Sistema de Detecção de Fraudes em Tempo Real - Guia Completo/fraud_detection_system/recaptcha-service"

# Inicie o servidor novamente
npm start
```

**Você verá no console:**
```
✅ Environment variables loaded successfully
🔐 reCAPTCHA Site Key: CONFIGURED
🔐 reCAPTCHA Secret: CONFIGURED
🚀 Server running on: http://localhost:3000
```

---

### PASSO 6: Limpar Cache do Navegador

**MUITO IMPORTANTE!** O navegador pode ter a versão antiga em cache.

**Opção 1: Hard Refresh (Recomendado)**
- **Windows/Linux:** Pressione `Ctrl + Shift + R` ou `Ctrl + F5`
- **Mac:** Pressione `Cmd + Shift + R`

**Opção 2: Abrir em Janela Anônima**
- `Ctrl + Shift + N` (Chrome)
- `Ctrl + Shift + P` (Firefox)

---

### PASSO 7: Testar o reCAPTCHA

1. **Acesse a página:**
   ```
   http://localhost:3000/fraudguard.html
   ```

2. **Abra o Console do Navegador** (F12 → Console)

3. **Procure por estas mensagens:**
   ```
   ✅ reCAPTCHA site key loaded: 6LcXXXXXXXXXXXXXX...
   ✅ reCAPTCHA script loaded successfully
   ```

4. **Verifique o reCAPTCHA:**
   - ✅ O checkbox "I'm not a robot" deve aparecer
   - ✅ **NÃO deve aparecer** a mensagem "for testing purposes only"
   - ✅ Ao clicar no checkbox, deve funcionar normalmente

5. **Teste o Login/Registro:**
   - Preencha o formulário
   - Marque o reCAPTCHA
   - Envie o formulário
   - Deve funcionar perfeitamente!

---

## ✅ Checklist de Verificação

Após seguir todos os passos, confirme:

- [ ] Acessei https://www.google.com/recaptcha/admin/create
- [ ] Criei um novo site reCAPTCHA v2
- [ ] Adicionei os domínios (localhost, 127.0.0.1)
- [ ] Copiei a **Site Key**
- [ ] Copiei a **Secret Key**
- [ ] Atualizei o arquivo `.env` com as novas chaves
- [ ] Salvei o arquivo `.env`
- [ ] Reiniciei o servidor (`npm start`)
- [ ] Limpei o cache do navegador (Ctrl + Shift + R)
- [ ] Testei em http://localhost:3000/fraudguard.html
- [ ] **A mensagem de teste NÃO aparece mais** ✅
- [ ] O reCAPTCHA funciona corretamente ✅

---

## 🎯 Resultado Esperado

### ANTES (Com Chaves de Teste):
```
┌─────────────────────────────────────────────┐
│ [ ] I'm not a robot                        │
│                                             │
│ ⚠️ This reCAPTCHA is for testing purposes  │
│    only. Please report to the site admin   │
│    if you are seeing this.                 │
└─────────────────────────────────────────────┘
```

### DEPOIS (Com Chaves de Produção):
```
┌─────────────────────────────────────────────┐
│ [ ] I'm not a robot                        │
│                                             │
│ ✅ SEM MENSAGEM DE TESTE!                   │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🐛 Problemas Comuns e Soluções

### Problema 1: Mensagem ainda aparece após trocar as chaves

**Solução:**
1. Verifique se salvou o arquivo `.env`
2. Confirme que reiniciou o servidor (`npm start`)
3. **Limpe o cache do navegador** (Ctrl + Shift + R)
4. Tente em janela anônima

### Problema 2: reCAPTCHA não aparece

**Solução:**
1. Abra o console (F12)
2. Procure por erros em vermelho
3. Verifique se o domínio está configurado no Google reCAPTCHA
4. Confirme que as chaves foram copiadas corretamente (sem espaços extras)

### Problema 3: Erro "Invalid site key"

**Solução:**
1. Verifique se copiou a **Site Key** corretamente
2. Não deve ter espaços no início ou fim da chave
3. Confirme que está acessando de um domínio registrado (localhost)

### Problema 4: Verificação falha no servidor

**Solução:**
1. Verifique se copiou a **Secret Key** corretamente
2. Confirme que o arquivo `.env` foi salvo
3. Reinicie o servidor

---

## 📞 Suporte Adicional

### Verificar se as chaves estão carregadas:

```bash
# No terminal, execute:
curl http://localhost:3000/api/site-key
```

**Resposta esperada:**
```json
{
  "siteKey": "6LcXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "version": "v2-checkbox"
}
```

Se a chave mostrada ainda for `6LeIxAcTAAAAA...`, o servidor não foi reiniciado.

---

## 🎓 Entendendo as Chaves

### Site Key (Chave do Site)
- ✅ **Pública** - pode ser vista no código fonte
- ✅ Usada no **frontend** (HTML/JavaScript)
- ✅ Mostra o checkbox do reCAPTCHA para o usuário

### Secret Key (Chave Secreta)
- 🔒 **Privada** - deve ficar APENAS no servidor
- 🔒 Usada no **backend** (Node.js/PHP/Python)
- 🔒 Valida a resposta do reCAPTCHA no servidor
- 🔒 **NUNCA** compartilhe ou exponha no código público

---

## ⏱️ Tempo Estimado

- **Criar conta Google reCAPTCHA:** 2-3 minutos
- **Copiar chaves e atualizar .env:** 1 minuto
- **Reiniciar servidor e testar:** 1 minuto
- **TOTAL:** ~5 minutos

---

## 🎉 Conclusão

Após seguir estes passos:

✅ **O reCAPTCHA continua funcionando** (proteção anti-bot ativa)
✅ **A mensagem de teste desaparece** completamente
✅ **Suas chaves são de produção** válidas
✅ **Pronto para uso em produção**

---

## 📝 Observações Importantes

1. **Guarde suas chaves em local seguro** (gerenciador de senhas)
2. **Não compartilhe a Secret Key** publicamente
3. **Adicione `.env` ao `.gitignore`** (já está configurado)
4. **Para cada ambiente** (dev/staging/prod), você pode criar chaves diferentes
5. **Monitore o painel do reCAPTCHA** em https://www.google.com/recaptcha/admin para ver estatísticas

---

**Criado em:** 20 de Dezembro de 2024
**Status:** ✅ Guia Completo e Testado
**Tempo:** 5 minutos para implementação

*Boa sorte! Suas chaves de produção vão eliminar a mensagem de teste!* 🎊
