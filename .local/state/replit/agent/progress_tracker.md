# SIGE - Sistema Integrado de Gestão Educacional
## 🎯 ONDE ENCONTRAR OS PRÉ-REQUISITOS NO ADMIN

### ✅ TUDO ESTÁ REGISTRADO E PRONTO PARA USAR:

---

## 🔐 **Como Acessar:**

1. **Vá para:** `/admin/`
2. **Login:**
   - Usuário: `admin`
   - Senha: `admin`
3. **Você verá as novas seções no CORE:**

---

## 📍 **NOVAS SEÇÕES NO ADMIN:**

### **1. Editar Curso → Pré-requisitos**
- Vá em: **Admin → CORE → Cursos**
- Clique em um curso
- **Novo campo:** "Requer Pré-requisitos" (checkbox)
- **Novo painel:** "Pré-requisitos de Disciplina" (tabela inline)
  - Adicione disciplinas pré-requisito
  - Defina nota mínima para cada
  - Marque se é obrigatório
  - Defina a ordem

### **2. Pré-requisito de Disciplina**
- **Novo menu:** Admin → CORE → **Pré-requisitos de Disciplina**
- Lista todos os pré-requisitos cadastrados
- Mostra: Curso, Disciplina, Nota Mínima, Se é obrigatório
- Filtros por curso e obrigatoriedade

### **3. Histórico Académico**
- **Novo menu:** Admin → CORE → **Históricos Académicos**
- Um histórico por aluno que se inscreveu
- Mostra as notas que o aluno tem em disciplinas anteriores
- **Painel inline:** Notas da Disciplina
  - Adicione as notas que o aluno obteve
  - Disciplina, nota, ano de conclusão

### **4. Notas de Disciplina**
- **Novo menu:** Admin → CORE → **Notas de Disciplina**
- Lista todas as notas de disciplinas
- Pesquisável por nome do aluno e disciplina
- Filtros por ano de conclusão

### **5. Disciplinas (Atualizado)**
- **Menu:** Admin → CORE → **Disciplinas**
- Agora mostra: Nome, Código, Curso, Carga Horária
- Novo campo "Código" para identificar disciplinas

---

## 🎯 **EXEMPLO DE USO PRÁTICO:**

### **Passo 1: Configure um Curso com Pré-requisito**
1. Vá a Admin → Cursos
2. Clique em "Python Avançado"
3. Marque ✓ "Requer Pré-requisitos"
4. Rolo para baixo → "Pré-requisitos de Disciplina"
5. Clique "Adicionar outra linha"
6. Selecione: Disciplina = "Lógica de Programação"
7. Nota Mínima = 14.0
8. Obrigatório = ✓
9. Ordem = 1
10. Salve

### **Passo 2: Aluno se Inscreve**
1. Aluno vai em Fazer Inscrição
2. Seleciona "Python Avançado"
3. **Novo:** Sistema exibe campo para inserir nota que obteve em "Lógica de Programação"
4. Se nota < 14.0 → Sistema bloqueia inscrição

### **Passo 3: Visualize o Histórico**
1. Admin → Históricos Académicos
2. Vê todas as notas do aluno
3. Pode adicionar mais notas de outras disciplinas

---

## 🔧 **CAMPOS DISPONÍVEIS:**

**PrerequisitoDisciplina:**
- ✓ Curso
- ✓ Disciplina Pré-requisito
- ✓ Nota Mínima (0-20)
- ✓ Obrigatório (sim/não)
- ✓ Ordem (para exibição)

**HistoricoAcademico:**
- ✓ Inscrição (read-only)
- ✓ Notas de Disciplina (inline - adicione quantas quiser)
- ✓ Data de Criação (auto)
- ✓ Data de Atualização (auto)

**NotaDisciplina:**
- ✓ Disciplina
- ✓ Nota (0-20)
- ✓ Ano de Conclusão
- ✓ Observações

---

## ✨ **TUDO ESTÁ PRONTO:**

- ✅ Modelos criados e migrados
- ✅ Admin totalmente configurado
- ✅ Campos de pré-requisito adicionados a Cursos
- ✅ Métodos de validação implementados
- ✅ Inline forms para facilitar entrada de dados

**Próximo passo:** Validação nas inscrições (já mencionado)

---

**Data: 25/12/2025**
**Status: 🎉 PRONTO PARA USAR NO ADMIN**