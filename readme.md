# API de Apostadores

Esta é uma API robusta desenvolvida com **FastAPI** para o gerenciamento de apostadores. O projeto foi estruturado para ser implantado no **Render**, utilizando **PostgreSQL** em produção e **SQLite** para desenvolvimento local, contando com uma camada adicional de segurança via criptografia simétrica.

---

## Tecnologias

*   **Linguagem:** Python 3.10+
*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
*   **Banco de Dados:** PostgreSQL (Produção) / SQLite (Dev)
*   **ORM:** SQLAlchemy
*   **Segurança:** Cryptography (Fernet)
*   **Servidor:** Uvicorn

---

## Medidas de Segurança

Para proteger os dados sensíveis dos usuários, como a **Chave PIX**, implementamos criptografia em repouso:
*   **Criptografia Simétrica:** Os dados são transformados em um hash ilegível antes de serem salvos no banco de dados.
*   **Descriptografia Dinâmica:** Os dados só são convertidos de volta para texto legível no momento da resposta da API.
*   **Ambiente Isolado:** A chave de criptografia é gerenciada via variáveis de ambiente, nunca ficando exposta no código-fonte.

---

## Acesso Online

*   **API Base:** `https://api-sd-df8o.onrender.com`
*   **Documentação Interativa (Swagger):** [https://api-sd-df8o.onrender.com/docs](https://api-sd-df8o.onrender.com/docs)

---

## Endpoints Principais

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| **GET** | `/apostadores/` | Lista todos os apostadores cadastrados. |
| **POST** | `/apostadores/` | Cria um novo registro (Chave PIX é criptografada). |
| **GET** | `/apostadores/{id}` | Busca os detalhes de um apostador específico. |
| **PUT** | `/apostadores/{id}` | Atualiza os dados de um apostador. |
| **DELETE** | `/apostadores/{id}` | Remove um apostador do sistema. |

### Exemplo de JSON para Criação (POST):
```json
{
  "nome": "João Silva",
  "idade": 25,
  "chave_pix": "joao@email.com"
}

## Instalação e Execução Local

### 1. Clone o repositório:
``` git clone https://github.com/m-valentim/api-sd.git

### 2. Instale as dependências:
    ```bash
    pip install -r requirements.txt

### 3. Gere uma chave de criptografia local:
    ``` python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

### Inicie o servidor:
```bash
    uvicorn main:app --reload

**A API estará disponível em `http://127.0.0.1:8000`.**