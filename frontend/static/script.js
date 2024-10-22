const messageInput = document.getElementById("user-input");
const img = document.getElementById("myImage");
const criativo = document.getElementById('criativo');
const preciso = document.getElementById('preciso');
let btn_type = "conservador"

// mesnagem de boas vindas
const bot = "sus"
const txt = "Olá! Sou sua assistente virtual especializada em busca de propostas políticas. Estou aqui para ajudá-lo a explorar e entender diferentes iniciativas governamentais e políticas públicas, desde planos de incentivo à saúde até estratégias de gestão de recursos públicos. Se desejar buscar por planos de governos ou ver propostas inovadoras de determinado tema, é só pesquisar! Vamos começar?"
addMessageToChat(bot, txt);

// Adiciona evento de clique na imagem
img.addEventListener("click", animateImage);

messageInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        animateImage();
        sendMessage();
        event.preventDefault(); // Previne a quebra de linha ao pressionar Enter
    }
});

criativo.addEventListener('click', function() {
    criativo.classList.remove('glow-on-hover');
    criativo.classList.add('clicked'); // Alterna a classe
    preciso.classList.remove("clicked");
    btn_type = "criativo";
});

preciso.addEventListener('click', function() {
    preciso.classList.add('clicked'); // Alterna a classe
    criativo.classList.remove("clicked");
    criativo.classList.add('glow-on-hover');
    btn_type = "preciso";
});


function openNewTab() {
    var newWindow = window.open(window.location.href, '_blank');
    newWindow.focus();
}

function addTextToChat(text) {
    // Adiciona o texto ao campo de entrada do chat
    document.getElementById('user-input').value = text;
}

// Função para aplicar o efeito de movimento e desaparecimento
function animateImage() {
    img.classList.add("move");

    // Aguarda o final da animação para remover a classe e restaurar o estado
    setTimeout(function() {
        img.classList.remove("move");
    }, 500); // O tempo deve ser igual à duração da animação em CSS
}

function loading() {
    const chatbx = document.querySelector('.chat-box'); // Seleciona o contêiner do chat

    // Cria o elemento de carregamento
    const loadingMessage = document.createElement('div');
    loadingMessage.classList.add('message-container', 'bot-message-container', 'load');
    loadingMessage.innerHTML = `
        <img src="static/images/logo.png" class="profile-image">
        <div class="message bot-message">
          <div class="sec-loading">
            <div class="one"></div>
          </div>
        </div>
    `;

    // Adiciona o elemento ao contêiner do chat
    chatbx.appendChild(loadingMessage);
    chatbx.scrollTop = chatbx.scrollHeight;
}

function removeLoadingMessage() {
    const chatb = document.querySelector('.chat-box'); // Seleciona o contêiner do chat
    const loadingMessage = chatb.querySelector('.load'); // Seleciona a mensagem de carregamento

    // Remove o elemento se ele existir
    if (loadingMessage) {
        chatb.removeChild(loadingMessage);
    }
}

function sendMessage() {
    const userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return; // Não envia mensagem se estiver vazia
  
    // Adiciona a mensagem do usuário ao chat
    addMessageToChat("user", userInput);
    loading();
  
    // Limpa o campo de entrada de texto
    document.getElementById("user-input").value = "";
  
    // Envia a mensagem para o backend
    fetch("/chat", {
          method: "POST",
          headers: {
              "Content-Type": "application/json"
          },
          body: JSON.stringify({ message: userInput , style : btn_type})
      })
      .then(response => response.json())
      .then(data => {
          // data.reply agora deve ser uma lista de strings
          // console.log(typeof(data.reply))
          if (Array.isArray(data.reply)) {
              data.reply.forEach(replyMessage => {
                  // Adiciona cada resposta do chatbot à caixa de chat
                  addMessageToChat("Chatbot", replyMessage);
              });
          } else {
              // Caso não seja uma lista, lida como antes (fallback)
              addMessageToChat("Chatbot", data.reply);
          }
      })
      .catch(error => {
          console.error("Erro ao enviar a mensagem:", error);
      });
  }
  
  function addMessageToChat(sender, message) {
    const chatBox = document.getElementById("chat-box");
    const messageContainer = document.createElement("div");
    const messageElement = document.createElement("div");
    const profileImage = document.createElement("img");
  
    // Define a classe do contêiner e da imagem de perfil com base no remetente
    if (sender === "user") {
        messageContainer.className = "message-container user-message-container";
        profileImage.src = "static/images/profile.png"; // Caminho para a imagem de perfil do usuário
    } else {
        messageContainer.className = "message-container bot-message-container";
        profileImage.src = "static/images/logo.png"; // Caminho para a imagem de perfil do bot
    }
  
    profileImage.className = "profile-image";
    messageElement.className = "message " + (sender === "user" ? "user-message" : "bot-message");
    messageElement.innerHTML = message;  // Use innerHTML para suportar quebras de linha

    removeLoadingMessage();
  
    // Adiciona a imagem de perfil e a mensagem ao contêiner
    if (sender === "user") {
        messageContainer.appendChild(messageElement);
        messageContainer.appendChild(profileImage);
        chatBox.appendChild(messageContainer);
    } else {
        messageContainer.appendChild(profileImage);
        messageContainer.appendChild(messageElement);
        chatBox.appendChild(messageContainer);
    }
  
    chatBox.scrollTop = chatBox.scrollHeight; // Rola para a última mensagem
  }