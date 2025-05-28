# PYGAME: Fórmula Insper
Enrique Pellaes, Lucas Moreira, e Raphael Primo - Engenharia Turma A

O código está organizado em dois arquivos principais:

engine.py: contém todas as constantes, classes (ParticleSystem, Car) e funções de renderização (draw_track, draw_hud, draw_intro, draw_countdown).

main.py: entrypoint do jogo, responsável por inicializar o Pygame, carregar assets e executar o loop principal em tela cheia.


Como rodar o jogo:

Pré-requisitos:
VIsual Studio Code instalado, expansões Pylance, Python, Python Debugger e GitHub Copilot Chat instaladas, e Biblioteca Pygame instalada;


Instalação:
1- Clone o repositório no VSCode:
git clone https://github.com/raphaelcp22/PYGAME

2-Instale as dependências:
pip install pygame

3- Execute o jogo:
PYGAME/Código/main.py


Controles:
Jogador 1 (Carro Vermelho):

W: Acelerar

S: Frear/Ré

A/D: Virar para esquerda/direita

Shift: Turbo

Jogador 2 (Carro Azul):

Setas: Movimentação

Ctrl: Turbo


O Fórmula Insper é um jogo de carro de corrida em pixel art, seguindo uma essência de Fórmula 1 e StockCar. Neste jogo, implementamos um 1v1 local (mesma máquina) de dois carros: o vermelho e o azul. Seja mais veloz e mais inteligente que seu oponente e termine as voltas primeiro.

Principais Características:
Corrida Multijogador Local: Batalhe contra um amigo na mesma tela

Sistema de Drift Realista: Controle deslizamentos e derrapagens com uma animação lembrando a física real

Pista com curvas, retas e obstáculos

Sistema de Turbo: Gerencie seu boost para ultrapassagens estratégicas, mas há de se tomar cuidado, pois ele é limitado

Mecânicas:
Sistema de Dano e vida útil do carro: Colisões e contato direto com a grama reduzem sua vida, o que pode modificar sua velocidade máxima

Pit Stop: Área para reparos durante a corrida; Caso tenha perdido sua vida útil, use o Pit Stop, mas com sabedoria, pois é uma área lenta

Efeitos Visuais: Partículas, marcas de derrapagem e efeitos de velocidade e de danificação do carro

Trilha Sonora: Música temática e efeitos sonoros imersivos (som da batida, do turbo e da ignição ao iniciar o carro)


Link do vídeo no Youtube, do jogo funcionando e suas mecânicas:
https://youtu.be/kxz9ZFgJgtg



Usos de Inteligencia Artificial para desenvolver o jogo: Deepseek, Git Copilot, ChatGPT (implementamos somente imagens)

A função de detecção e resposta à colisão entre os carros, usada no jogo, foi gerada com auxílio de IA em cerca de 90%.  Utilizamos o DeepSeek (não tem histórico do chat disponível) e o prompt utilizado foi: "Estou criando um jogo de Fórmula 1 no Pygame. Quero implementar um sistema de colisão entre os carros que considere tempo de recarga, força do impacto baseada na diferença de velocidade, e gere partículas visuais quando o impacto for forte. Também quero aplicar um empurro (impulso) nos carros e tocar um som de colisão, se o som estiver disponível. Adicione esse trecho de código para mim?" 

A lógica de direção e drift dos carros foi aproximadamente 85% gerada com ajuda de IA. O DeepSeek e o Git Copilot foram utilizados e usamos o seguinte prompt: "Complete o código para que os carros façam curvas suavemente, com velocidade influenciando o ângulo de giro. Além disso, quero implementar uma mecânica de drift: quando o carro estiver rápido e fizer curvas acentuadas, ele deve derrapar, perder tração, criar marcas de pneu e soltar partículas de fumaça. Pode criar esse trecho para mim?" 

A função draw_skid_marks foi 100% gerada com ajuda do DeepSeek. O prompt usado foi: "Adicione uma função no Pygame que desenhe marcas de skid marks (derrapagem) na pista, com base na posição e ângulo do carro. As marcas devem desaparecer com o tempo e ter um efeito de transparência gradual. " 

A classe Car foi aproximadamente 40% auxiliada por IA, especificamente em trechos que envolvem uso de vetores (Vector2), física básica e parâmetros de movimentação. O prompt utilizado foi: "Estou criando uma classe de carro em um jogo de Fórmula 1 usando Pygame. Preciso de ajuda com a estrutura geral e principalmente com os atributos de movimentação, como vetores de posição, velocidade, aceleração, ângulo de giro, e atrito. Pode adicionar e indicar onde preciso alterar no código para ficar mais fluído" 