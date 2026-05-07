# 🎰 API de Apostadores

Esta é uma API robusta desenvolvida com **FastAPI** para o gerenciamento de apostadores. O projeto foi estruturado para ser implantado no **Render**, utilizando **PostgreSQL** em produção e **SQLite** para desenvolvimento local, contando com uma rigorosa camada de segurança via criptografia simétrica.

---

## 🚀 Tecnologias

*   **Linguagem:** Python 3.10+
*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
*   **Banco de Dados:** PostgreSQL (Produção) / SQLite (Dev)
*   **ORM:** SQLAlchemy
*   **Segurança:** Cryptography (Fernet) + Fail-Fast Design
*   **Ambiente:** `python-dotenv` para variáveis de ambiente locais
*   **Servidor:** Uvicorn

---

## 🔒 Medidas de Segurança (Criptografia Simétrica Estrita)

Para proteger os dados sensíveis dos usuários (como a **Chave PIX**), implementamos criptografia em repouso com um sistema de **Fail-Fast**:
*   **Criptografia Simétrica (Fernet):** Os dados são transformados em um hash ilegível antes de serem salvos no banco de dados e descriptografados apenas no momento do retorno da requisição.
*   **Fail-Fast Design:** A API **não inicia** se não detectar a variável de ambiente `ENCRYPTION_KEY`. Isso impede a criação acidental de dados com chaves temporárias, garantindo que nenhum registro se torne inacessível no futuro.
*   **Isolamento de Segredos:** A chave de criptografia nunca é exposta no código-fonte, sendo gerenciada exclusivamente via `.env` (localmente) ou Painel do Render (produção).

---

## 🌐 Acesso Online

*   **API Base:** `https://api-sd-df8o.onrender.com`
*   **Documentação Interativa (Swagger):** [https://api-sd-df8o.onrender.com/docs](https://api-sd-df8o.onrender.com/docs)

---

## 📡 Endpoints Principais

| Método | Rota | Descrição |
| :--- | :--- | :--- |
| **GET** | `/apostadores/` | Lista todos os apostadores cadastrados (PIX descriptografado). |
| **POST** | `/apostadores/` | Cria um novo registro (Chave PIX é criptografada no banco). |
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
```
## Instalação e Execução Local

### 1. Clone o repositório:
    git clone https://github.com/m-valentim/api-sd.git

### 2.  Crie um ambiente virtual e instale as dependências:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    pip install -r requirements.txt
```
### 3. Gere uma chave de criptografia local:
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

### 4. Configure o arquivo `.env`:
    Crie um arquivo chamado `.env` na raiz do projeto e insira a chave gerada:
    ```env
    ENCRYPTION_KEY=cole_a_chave_gerada_aqui
    ```
### 4. Instale as dependências:
    pip install -r requirements.txt

### 5. Inicie o servidor:
    uvicorn main:app --reload

**A API estará disponível em `http://127.0.0.1:8000`.**