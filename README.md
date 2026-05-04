# API de Apostadores

Esta API permite o gerenciamento de apostadores, permitindo criar, listar, 
buscar, atualizar e deletar registros em um banco de dados PostgreSQL.

## 1. Acesso Online
A API está hospedada no Render e pode ser acessada pelo link:
https://api-sd-df8o.onrender.com

## 2. Documentação Interativa
Para testar todos os endpoints visualmente, acesse:
https://api-sd-df8o.onrender.com/docs

## 3. Endpoints Principais

### Listar todos os apostadores
- **Método:** GET
- **Rota:** `https://api-sd-df8o.onrender.com/apostadores/`
- **Resposta esperada:** 200 OK com uma lista de objetos.

### Criar um novo apostador
- **Método:** POST
- **Rota:** `https://api-sd-df8o.onrender.com/apostadores/`
- **Corpo da requisição (JSON):**
  {
    "nome": "João Silva",
    "idade": 25,
    "chave_pix": "joao@email.com"
  }

### Buscar apostador por ID
- **Método:** GET
- **Rota:** `https://api-sd-df8o.onrender.com/apostadores/{id}`

### Atualizar um apostador
- **Método:** PUT
- **Rota:** `https://api-sd-df8o.onrender.com/apostadores/{id}`
- **Corpo da requisição (JSON):** Dados atualizados no mesmo formato do POST.

### Deletar um apostador
- **Método:** DELETE
- **Rota:** `https://api-sd-df8o.onrender.com/apostadores/{id}`

## 4. Como rodar localmente
1. Instale as dependências: `pip install -r requirements.txt`
2. Inicie o servidor: `uvicorn main:app --reload`
3. A API utilizará SQLite localmente por padrão caso a variável DATABASE_URL não esteja definida.