# 🏥 ClinicCall

O **ClinicCall** é um sistema leve de chamados e suporte interno em tempo real, projetado especificamente para otimizar a comunicação entre os setores de uma clínica (como Recepção, Triagem e Consultórios) e a equipe de TI. 

O sistema elimina a necessidade de ferramentas externas ou internet, rodando de forma descentralizada na rede local (LAN) através de uma arquitetura cliente-servidor baseada em WebSockets.

---

## 📂 Estrutura do Projeto

Abaixo está a organização dos arquivos necessários para o funcionamento do ecossistema:

| Arquivo | Componente | Descrição |
| :--- | :--- | :--- |
| `server.py` | **Servidor (Backend)** | Gerencia as conexões WebSocket, identifica os nós da rede e roteia as mensagens instantaneamente. |
| `admin.py` | **Painel do Técnico (TI)** | Interface gráfica central onde chegam os alertas de chamados e onde o suporte interage via chat. |
| `client.py` | **App do Funcionário** | Interface simplificada com o botão de emergência e chat, instalada nos computadores da clínica. |

---

## 🛠️ Tecnologias Utilizadas

* [Python 3.11/3.12](https://www.python.org/) - Linguagem base do projeto.
* [FastAPI](https://fastapi.tiangolo.com/) - Framework web de alta performance para o servidor.
* [WebSockets](https://developer.mozilla.org/pt-BR/docs/Web/API/WebSockets_API) - Comunicação bidirecional assíncrona em tempo real.
* [Tkinter](https://docs.python.org/3/library/tkinter.html) - Interface gráfica (GUI) nativa e leve para os painéis.
* [PyInstaller](https://pyinstaller.org/) - Empacotamento do cliente em um executável (.exe) independente.

---

## 🔄 Protocolo de Comunicação (JSON)

Os dados trafegam pela rede utilizando estruturas simples em JSON via WebSocket. O servidor interpreta as mensagens de acordo com os seguintes formatos:

### 1. Envio de Chamado (Cliente ➔ Servidor ➔ ADM)
```json
{
  "type": "call",
  "sender": "DESKTOP-RECEPÇÃO",
  "sector": "Faturamento",
  "message": "Solicitou presença no setor."
}
