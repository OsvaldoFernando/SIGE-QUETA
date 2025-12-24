# SIGE - Sistema Integrado de Gestão Educacional

## 📋 Visão Geral
Sistema completo de gestão educacional em Django com interface moderna e profissional. Implementa gerenciamento de cursos, disciplinas, e sistema de autenticação com subscrição.

**Status:** ✅ MVP Completo e Funcional
**Última Atualização:** 24 de Dezembro de 2025

---

## 🎯 Funcionalidades Principais

### 1. Autenticação e Autorização
- Sistema de login/logout
- Registro de usuários
- Subscrição com data de expiração
- Controle de acesso por papel (admin, professor, aluno)

### 2. Gestão de Cursos ✨ PROFISSIONAL
**Aba: Cursos** (com destaque visual azul claro)
- ✅ Criar novo curso
- ✅ Editar informações de curso
- ✅ Deletar curso (com confirmação)
- ✅ **Toggle Ativo/Inativo** (com feedback visual imediato)
- Campos: Código, Nome, Vagas, Duração, Nota Mínima

**Duração disponível:** 3 meses, 6 meses, 1 ano, 2 anos, 3 anos, 4 anos, **5 anos**

### 3. Gestão de Disciplinas
**Aba: Disciplinas** (com destaque visual cinzento)
- ✅ Criar nova disciplina
- ✅ Listar disciplinas por curso
- Campos: Nome, Curso, Carga Horária

---

## 🎨 Design e UX

### Paleta de Cores Profissional
```css
--primary-color: #2c3e50;      /* Cinza escuro */
--secondary-color: #3498db;     /* Azul */
--danger-color: #e74c3c;        /* Vermelho */
--success-color: #27ae60;       /* Verde */
--inactive-color: #95a5a6;      /* Cinzento */
--border-color: #e0e0e0;        /* Bordas suaves */
--bg-light: #f5f6f7;            /* Fundo claro */
--text-muted: #7f8c8d;          /* Texto secundário */
```

### Destaque das Abas (NOVO!)
- **Aba Ativa:** Bordinha inferior colorida (azul para Cursos, cinzento para Disciplinas)
- **Hover:** Fundo suave e transição suave
- **Visual Feedback:** Animação de transição 0.3s

### Detalhes Profissionais
- Border-radius suave em cards (12px)
- Sombras sutis (shadow-sm)
- Transições suaves em hover (translateY -2px)
- Cards com campos bem organizados
- Modais elegantes com headers contrastantes
- Tabelas com linhas claras e hover effects
- Botões com ícones FontAwesome
- Alertas fixos no canto superior direito

---

## 📁 Estrutura do Projeto

```
core/
├── models.py              # Modelos (Curso, Disciplina, Usuário)
├── views.py              # Views com AJAX para CRUD
├── urls.py               # URLs da app
├── admin.py              # Admin customizado
├── templates/
│   ├── core/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── painel_principal.html
│   │   └── cursos_disciplinas.html  # ← INTERFACE PRINCIPAL
│   └── ...
├── static/
│   ├── css/
│   └── js/
│
escola_sistema/
├── settings.py           # Configurações Django
├── urls.py              # URLs principais
└── wsgi.py
```

---

## 🔧 Modelos de Dados

### Curso
```python
- codigo (CharField, unique)
- nome (CharField)
- descrição (TextField, opcional)
- vagas (IntegerField)
- duracao_meses (IntegerField) # 3, 6, 12, 24, 36, 48, 60 meses
- nota_minima (DecimalField)
- ativo (BooleanField) ✨ DEFAULT: True
- criado_em (DateTimeField)
```

### Disciplina
```python
- nome (CharField)
- curso (ForeignKey → Curso)
- carga_horaria (IntegerField)
- criada_em (DateTimeField)
```

### Usuário (Django User)
```python
- username
- email
- password (hashed)
- is_staff (for admin)
- subscription_expiry (DateField)
```

---

## 🚀 Funcionalidades de CRUD via AJAX

### Criar Curso
- Modal com formulário validado
- Salva via POST AJAX
- Recarrega página ao sucesso
- Alerta visual de confirmação

### Editar Curso
- Pré-carrega dados do curso
- Modal com campos preenchidos
- Salva via POST AJAX
- Recarrega página ao sucesso

### Deletar Curso
- Confirmação JS antes de deletar
- Salva via POST AJAX
- Feedback visual

### Toggle Ativo/Inativo
- Botão que muda entre Verde (Ativo) e Cinzento (Inativo)
- Clique alterna status
- Recarrega página para atualizar visual
- Alerta de confirmação

### Criar Disciplina
- Seletor de curso
- Nome e carga horária
- Salva via POST AJAX
- Recarrega página ao sucesso

---

## 🔐 Credenciais Padrão

**Admin (Superuser):**
- Usuário: `admin`
- Senha: `admin`
- Subscrição: Ativa até 23/01/2026

---

## 📱 Responsividade

- **Desktop:** Cards em 3 colunas
- **Tablet:** Cards em 2 colunas  
- **Mobile:** Cards em 1 coluna
- Tabelas com scroll horizontal em mobile

---

## 🎯 Workflow de Uso

1. **Login** → `http://127.0.0.1:5000/login/`
2. **Painel Principal** → Menu com módulos
3. **Gestão de Cursos** → `/cursos-disciplinas/`
   - Clique em "Cursos" para gerenciar cursos
   - Clique em "Disciplinas" para gerenciar disciplinas

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Django 5.2.7
- **Frontend:** Bootstrap 5, FontAwesome
- **Database:** PostgreSQL (Replit)
- **JavaScript:** AJAX com Fetch API
- **CSS:** Grid, Flexbox, CSS Variables

---

## 📝 Preferências de Desenvolvimento

### Código
- Código limpo e bem organizado
- Nomes descritivos em português/inglês (misturado conforme necessário)
- Componentes reutilizáveis
- DRY (Don't Repeat Yourself)

### UI/UX
- Design profissional e minimalista
- Feedback visual claro em todas as ações
- Transições suaves
- Acessibilidade considerada

### Performance
- AJAX para evitar recarregamentos desnecessários
- Validação lado cliente quando possível
- Otimização de consultas ao banco

---

## 🔄 Fluxo de Dados

```
Cliente (Browser)
    ↓
Modal/Form (HTML)
    ↓
JavaScript AJAX
    ↓
Django View (views.py)
    ↓
Database (PostgreSQL)
    ↓
JSON Response
    ↓
JavaScript Alert
    ↓
Page Reload
    ↓
Atualização Visual
```

---

## ✅ Checklist de Funcionalidades

- [x] Autenticação e login
- [x] Painel principal
- [x] CRUD Cursos (Create, Read, Update, Delete)
- [x] CRUD Disciplinas (Create, Read)
- [x] Toggle Ativo/Inativo com feedback visual
- [x] Interface com abas (Cursos/Disciplinas)
- [x] Destaque visual das abas ativas
- [x] Design profissional e minimalista
- [x] Responsividade mobile
- [x] Validação de formulários
- [x] Alertas de sucesso/erro
- [x] AJAX sem recarregar página
- [x] Modalidades 3-5 anos de duração

---

## 🎓 Próximas Melhorias (Futuro)

- [ ] Editar/Deletar Disciplinas
- [ ] Gerenciar Alunos
- [ ] Atribuir Disciplinas a Professores
- [ ] Relatórios de Cursos
- [ ] Exportar dados (PDF/Excel)
- [ ] Dashboard com gráficos
- [ ] Notificações
- [ ] Sistema de permissões granular

---

## 📞 Suporte Técnico

**Status do Servidor:** ✅ Running
**URL Local:** http://127.0.0.1:5000/
**Database:** PostgreSQL (Replit)
**Workflow:** Django Server (python manage.py runserver 0.0.0.0:5000)
