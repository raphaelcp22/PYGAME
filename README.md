# PYGAME: Fórmula Insper
Enrique Pellaes, Lucas Moreira, e Raphael Primo - Engenharia Turma A

Como rodar o jogo:








Usos de Inteligencia Artificial para desenvolver o jogo: Deepseek, Git Copilot, ChatGPT (implementamos somente imagens)

A função de detecção e resposta à colisão entre os carros, usada no jogo, foi gerada com auxílio de IA em cerca de 90%.  Utilizamos o DeepSeek (não tem histórico do chat disponível) e o prompt utilizado foi: "Estou criando um jogo de Fórmula 1 no Pygame. Quero implementar um sistema de colisão entre os carros que considere tempo de recarga, força do impacto baseada na diferença de velocidade, e gere partículas visuais quando o impacto for forte. Também quero aplicar um empurro (impulso) nos carros e tocar um som de colisão, se o som estiver disponível. Adicione esse trecho de código para mim?" 

A lógica de direção e drift dos carros foi aproximadamente 85% gerada com ajuda de IA. O DeepSeek e o Git Copilot foram utilizados e usamos o seguinte prompt: "Complete o código para que os carros façam curvas suavemente, com velocidade influenciando o ângulo de giro. Além disso, quero implementar uma mecânica de drift: quando o carro estiver rápido e fizer curvas acentuadas, ele deve derrapar, perder tração, criar marcas de pneu e soltar partículas de fumaça. Pode criar esse trecho para mim?" 

A função draw_skid_marks foi 100% gerada com ajuda do DeepSeek. O prompt usado foi: "Adicione uma função no Pygame que desenhe marcas de skid marks (derrapagem) na pista, com base na posição e ângulo do carro. As marcas devem desaparecer com o tempo e ter um efeito de transparência gradual. " 

A classe Car foi aproximadamente 40% auxiliada por IA, especificamente em trechos que envolvem uso de vetores (Vector2), física básica e parâmetros de movimentação. O prompt utilizado foi: "Estou criando uma classe de carro em um jogo de Fórmula 1 usando Pygame. Preciso de ajuda com a estrutura geral e principalmente com os atributos de movimentação, como vetores de posição, velocidade, aceleração, ângulo de giro, e atrito. Pode adicionar e indicar onde preciso alterar no código para ficar mais fluído" 