# Análise de Recorrência POSCOMP para 2026

Base analisada: cadernos disponíveis em `Provas-POSCOMP/` de 2002 a 2019 e de 2022 a 2025. Não há 2020 e 2021 na pasta.

Nota sobre formato: o POSCOMP passou para prova online em 2024. Por isso, para previsão de 2026, o recorte `2024-2025` recebe atenção especial. Ainda assim, o histórico completo continua útil para separar assunto estrutural do edital de repetição recente.

Observação metodológica: os cadernos de 2002 e 2003 têm trechos de Fundamentos com extração ruim via `pdftotext`, então usei OCR para recuperar esse bloco. Questões muito dependentes de figura podem ter menor precisão na leitura automática, mas os temas principais aparecem pelo enunciado e alternativas.

Peso usado na análise:

| Peso | Significado |
|---|---|
| Muito alto | Tema recorrente historicamente e também forte em 2022-2025, incluindo o formato online quando aplicável |
| Alto | Tema recorrente, com presença recente clara |
| Médio | Tema aparece bastante, mas alterna subtópicos ou ficou menos recente |
| Baixo | Está no edital, mas aparece pouco no histórico ou só indiretamente |

## Conclusão Executiva

Não encontrei padrão confiável par/ímpar. O padrão mais útil é por blocos recorrentes e por estilo recente.

Para 2026, os assuntos com melhor custo-benefício são:

| Área | Prioridade máxima |
|---|---|
| Matemática | Gauss/sistemas, matrizes/vetores, retas/planos/distâncias, limites/gradiente/integral, lógica proposicional/quantificadores, Boole/Karnaugh, estatística básica |
| Fundamentos | Big-O/recorrência, ordenação/pesquisa/hash/árvores/pilhas/filas, cache/memória/processos, circuitos booleanos/FSM, regex/autômatos/bombeamento/gramáticas, grafos/BFS/DFS/topológica |
| Tecnologia | BD transações/recuperação/SQL, compiladores análise léxica/sintática/tradução, gráfica shading/texturas/Z-buffer, engenharia requisitos/testes/manutenção, IA/ML, imagens JPEG/filtros, redes TCP/UDP/DNS/sub-redes, distribuídos transparência/exclusão mútua |

## Melhores Assuntos por Tema

Esta é a tabela mais prática para montar plano de estudo. A ordem dentro da célula também importa: os primeiros são os que eu priorizaria.

| Área | Tema do edital | Melhores subtópicos para 2026 |
|---|---|---|
| Matemática | Álgebra Linear | Sistemas lineares/Gauss; transformações lineares e matrizes; subespaços/bases; autovalores/autovetores; projeção ortogonal |
| Matemática | Análise Combinatória | Combinações; permutações; permutações com restrições; inclusão-exclusão; distribuição de objetos/convites |
| Matemática | Cálculo Diferencial e Integral | Limites; continuidade; integral definida; gradiente; máximos/mínimos; Lagrange; regra dos trapézios |
| Matemática | Geometria Analítica | Retas; planos; distância/ângulo/interseção; vetores e produtos; círculo/esfera; coordenadas polares/esféricas |
| Matemática | Lógica Matemática | Equivalência proposicional; contrapositiva; negação de quantificadores; tabela verdade; argumentos por premissas |
| Matemática | Matemática Discreta | Conjuntos; álgebra booleana; De Morgan; Karnaugh/mintermos; Hamming/paridade; recursão/indução |
| Matemática | Probabilidade e Estatística | Média/mediana/moda; variância/desvio; probabilidade discreta; distribuição discreta; esperança; correlação/regressão |
| Fundamentos | Análise de Algoritmos | Big-O/Theta/Omega; comparação de crescimento; recorrências; análise de laços; recursão tipo Fibonacci/divisão |
| Fundamentos | Algoritmos e Estrutura de Dados | Ordenação; busca; hash; listas/pilhas/filas; árvores/BST/AVL/heap; guloso; dividir e conquistar |
| Fundamentos | Arquitetura e Organização de Computadores | Cache; hierarquia de memória; barramento; interrupções; pipeline; paralelismo; RISC/CISC |
| Fundamentos | Circuitos Digitais | Karnaugh/mintermos; circuitos combinatórios; portas lógicas; binário/hexadecimal; flip-flops/contadores; FSM Moore/Mealy |
| Fundamentos | Linguagens de Programação | Paradigmas; polimorfismo; sistemas de tipos; verificação/inferência de tipos; passagem de parâmetros |
| Fundamentos | Linguagens Formais, Autômatos e Computabilidade | Expressões regulares; AFD/AFND; gramáticas; livres de contexto/PDA; lema do bombeamento; Turing; P/NP |
| Fundamentos | Organização de Arquivos e Dados | Arquivos/registros/metadados; organização de arquivos; pesquisa full-text/índices; compressão RLE/Huffman/LZW |
| Fundamentos | Sistemas Operacionais | Memória virtual; paginação/page fault; working set; processos/threads/fork; escalonamento; deadlock; E/S |
| Fundamentos | Técnicas de Programação | Trace de código; `if`/`for`/`while`; seleção/laços; tipos básicos; modularidade/abstração |
| Fundamentos | Teoria dos Grafos | Conceitos de grafos; caminhos/ciclos; BFS/DFS; ordenação topológica; árvore geradora mínima; menor caminho |
| Tecnologia | Banco de Dados | Serializabilidade; transações; concorrência; recuperação/UNDO/REDO; SQL/álgebra relacional; normalização; chaves |
| Tecnologia | Compiladores | Análise léxica; análise sintática LL/LR; derivação; tradução dirigida pela sintaxe; representação intermediária; registradores/otimização |
| Tecnologia | Computação Gráfica | Z-buffer/superfícies ocultas; Phong/Gouraud; texturas/mipmapping; fontes de luz/rendering; transformações 2D/3D |
| Tecnologia | Engenharia de Software | Requisitos; testes/V&V; qualidade; manutenção; reengenharia; ciclo de vida; padrões de projeto |
| Tecnologia | Inteligência Artificial | Aprendizado de máquina; árvore de decisão; redes neurais/transfer learning; Bayes; algoritmos genéticos; fuzzy; sistemas especialistas |
| Tecnologia | Processamento de Imagens | Filtros; suavização/restauração; histograma/realce; JPEG/DCT; amostragem/quantização; visão computacional |
| Tecnologia | Redes de Computadores | TCP/UDP/DNS/HTTP; modelo OSI/TCP-IP; camadas; sub-redes/prefixos; roteadores; baud/taxa; DDoS/SYN |
| Tecnologia | Sistemas Distribuídos | Transparência; sistemas de arquivos distribuídos; exclusão mútua por token/anel; falhas; transações distribuídas; RPC/mensagens |

## Ranking Direto por Tema

### Matemática

#### Álgebra Linear

1. Sistemas de equações lineares, principalmente eliminação de Gauss.
2. Transformações lineares e matrizes, incluindo determinante, inversa e produto.
3. Espaços vetoriais, subespaços e bases.
4. Autovalores, autovetores e diagonalização.
5. Produto interno e projeções ortogonais.
6. Método dos mínimos quadrados.
7. Operadores simétricos/ortogonais/normais e teorema espectral.
8. Adjunta, formas canônicas e teoremas mais abstratos.

#### Análise Combinatória

1. Combinações simples e com restrições.
2. Permutações e anagramas.
3. Permutações com posições restritas e restrições de adjacência.
4. Princípio de inclusão e exclusão.
5. Distribuição de objetos/convites/itens indistinguíveis.
6. Enumeração por recursão.
7. Funções geradoras ordinárias e exponenciais.
8. Enumeração de partições, grafos, árvores e redes.

#### Cálculo Diferencial e Integral

1. Limites de funções e sequências.
2. Continuidade e diferenciabilidade de uma variável.
3. Integração de uma variável, especialmente integral definida.
4. Gradiente e derivadas parciais.
5. Máximos e mínimos.
6. Integração aproximada, especialmente regra dos trapézios.
7. Multiplicadores de Lagrange.
8. Funções de várias variáveis.
9. Taylor, Newton, jacobianas e diferenciação implícita.
10. Integrais múltiplas, mudança de coordenadas e integral de linha.

#### Geometria Analítica

1. Reta no plano e no espaço.
2. Planos.
3. Posições relativas, interseções, distâncias e ângulos.
4. Vetores.
5. Produtos escalar, vetorial e misto.
6. Círculo e esfera.
7. Coordenadas polares, cilíndricas e esféricas.
8. Matrizes e sistemas lineares quando aparecem com interpretação geométrica.

#### Lógica Matemática

1. Lógica proposicional: equivalências, implicação, contrapositiva.
2. Lógica de predicados e primeira ordem.
3. Negação de quantificadores: “existe”, “todos”, “nenhum”.
4. Tabelas-verdade.
5. Argumentos válidos a partir de premissas.
6. Relações de consequência.
7. Decidibilidade.
8. Corretude, completude, compacidade e Löwenheim-Skolem.
9. Prova automática e lógicas não clássicas.

#### Matemática Discreta

1. Álgebra booleana e leis de De Morgan.
2. Minimização de funções booleanas, Karnaugh e mintermos.
3. Conjuntos e álgebra de conjuntos.
4. Funções e formas booleanas.
5. Iteração, indução e recursão.
6. Teoria dos códigos, especialmente Hamming e paridade.
7. Relações sobre conjuntos, equivalência e ordem.
8. Reticulados, monóides, grupos e anéis.
9. Teoria dos domínios.

#### Probabilidade e Estatística

1. Descrição estatística dos dados: média, mediana, moda, percentuais.
2. Probabilidade em espaços amostrais discretos.
3. Distribuições de variáveis aleatórias.
4. Esperança matemática e valor esperado.
5. Variância, desvio padrão e correlação.
6. Regressão e correlação.
7. Eventos e experimentos aleatórios.
8. Estimação pontual e por intervalo.
9. Testes de hipóteses, qui-quadrado e comparação de médias.

### Fundamentos da Computação

#### Análise de Algoritmos

1. Notação Big O, Theta, Omega e comparação de crescimento.
2. Medidas de complexidade e análise assintótica.
3. Relações de recorrência para algoritmos recursivos.
4. Análise de laços e algoritmos iterativos.
5. Análise de recursão simples e dupla, como Fibonacci.
6. Técnicas de prova de cotas inferiores.
7. Medidas empíricas de performance.

#### Algoritmos e Estrutura de Dados

1. Algoritmos de pesquisa e ordenação.
2. Listas, pilhas e filas.
3. Árvores binárias, árvores de busca, AVL, heap e árvores balanceadas.
4. Tabelas hash e tratamento de colisões.
5. Recursividade.
6. Dividir e conquistar.
7. Algoritmos gulosos.
8. Tipos de dados básicos e estruturados.
9. Comandos de linguagem e trace de código.
10. Backtracking, força bruta, pesquisa exaustiva e heurísticas.

#### Arquitetura e Organização de Computadores

1. Memórias e hierarquia de memória.
2. Cache, mapeamento de cache, write-back e write-through.
3. Barramento, comunicação, interfaces e periféricos.
4. Mecanismos de interrupção e exceção.
5. Pipeline e paralelismo de baixa granularidade.
6. Arquiteturas RISC e CISC.
7. Modos de endereçamento e conjunto de instruções.
8. Unidades centrais de processamento.
9. Entrada e saída.
10. Multiprocessadores, multicomputadores e arquiteturas paralelas.

#### Circuitos Digitais

1. Minimização e otimização de funções combinatórias.
2. Karnaugh, mintermos e soma de produtos.
3. Circuitos combinatórios e portas lógicas.
4. Sistemas de numeração e códigos, especialmente binário e hexadecimal.
5. Aritmética binária e somadores.
6. Componentes sequenciais, flip-flops, registradores e contadores.
7. Máquinas de estado finito, Moore e Mealy.
8. Circuitos sequenciais síncronos e assíncronos.
9. PLD e projeto de sistemas digitais.
10. Famílias lógicas e conceitos de tempo/controle.

#### Linguagens de Programação

1. Paradigmas de linguagens: imperativo, funcional, OO, lógico e declarativo.
2. Polimorfismo, sobrescrita, sobrecarga e subtipagem.
3. Teoria dos tipos e sistemas de tipos.
4. Verificação e inferência de tipos.
5. Conceitos gerais de linguagens.
6. Passagem de parâmetros e subprogramas.
7. Semântica formal.

#### Linguagens Formais, Autômatos e Computabilidade

1. Expressões regulares e linguagens regulares.
2. Autômatos finitos determinísticos e não determinísticos.
3. Gramáticas regulares e livres de contexto.
4. Lema do bombeamento e propriedades das linguagens.
5. Autômatos de pilha.
6. Máquina de Turing.
7. Classes P, NP, NP-completo e NP-difícil.
8. Problemas indecidíveis e reduções.
9. Hierarquia de Chomsky.
10. Funções recursivas, Tese de Church e incompletude de Gödel.

#### Organização de Arquivos e Dados

1. Organização, estrutura e operação de arquivos.
2. Registros, metadados e organização física/lógica.
3. Compressão de dados, imagem, áudio e vídeo.
4. RLE, Huffman, LZW e codificação/decodificação.
5. Técnicas de pesquisa, índices e full-text.
6. Diretórios e sistemas de arquivos virtuais.
7. Dados e metadados.
8. Representação digital e analógica.

#### Sistemas Operacionais

1. Gerenciamento de memória: memória virtual, paginação, swap, working set.
2. Page fault e tabela de páginas.
3. Processos, threads e `fork`.
4. Gerência de processos e escalonamento.
5. Comunicação, concorrência e sincronização.
6. Deadlock, seção crítica e exclusão mútua.
7. Gerenciamento de arquivos.
8. Gerenciamento de dispositivos de E/S e drivers.
9. Alocação de recursos.

#### Técnicas de Programação

1. Comandos de linguagem: `if`, `for`, `while`, seleção e repetição.
2. Trace de código em C/Python/Pascal.
3. Tipos de dados básicos e estruturados.
4. Modularidade e abstração.
5. Desenvolvimento de algoritmos.
6. Metodologia de desenvolvimento de programas.

#### Teoria dos Grafos

1. Grafos orientados e não orientados.
2. Caminhos, ciclos e percursos.
3. Busca em largura e busca em profundidade.
4. Ordenação topológica.
5. Conectividade.
6. Árvore geradora e árvore geradora mínima.
7. Algoritmos do menor caminho.
8. Planaridade.
9. Coloração.
10. Grafos infinitos, problemas intratáveis e tópicos menos frequentes.

### Tecnologia de Computação

#### Banco de Dados

1. Gerenciamento de transações.
2. Serializabilidade e escalonamentos.
3. Concorrência e deadlock de transações.
4. Recuperação após falha, UNDO/REDO, ARIES, steal/no-force.
5. SQL e álgebra relacional.
6. Modelo relacional, normalização e modelo de dados.
7. Integridade, chave primária e chave estrangeira.
8. Bancos de dados distribuídos.
9. Arquitetura de SGBD e segurança.
10. Mineração de dados.

#### Compiladores

1. Análise sintática, LL, LR e derivação.
2. Análise léxica, tokens e expressões regulares.
3. Esquemas de tradução e definições dirigidas pela sintaxe.
4. Representação intermediária.
5. Tabelas de símbolos.
6. Ambientes de tempo de execução e registros de ativação.
7. Geração de código e alocação de registradores.
8. Otimização de código.
9. Compiladores, interpretadores, bibliotecas e compilação separada.

#### Computação Gráfica

1. Remoção de linhas e superfícies ocultas, especialmente Z-buffer.
2. Modelos de tonalização, Phong e Gouraud.
3. Aplicação de texturas, bump mapping e mipmapping.
4. Rendering e fontes de luz.
5. Transformações geométricas 2D e 3D.
6. Coordenadas homogêneas e matrizes de transformação.
7. Projeção paralela/perspectiva e câmera virtual.
8. Modelos poliedrais, malhas e visualização.
9. Recorte, aliasing e antialiasing.

#### Engenharia de Software

1. Engenharia de requisitos, especialmente requisitos não funcionais.
2. Verificação, validação e teste.
3. Qualidade e garantia de qualidade.
4. Manutenção de software.
5. Reengenharia e engenharia reversa.
6. Ciclo de vida de desenvolvimento, incremental, cascata, espiral e prototipação.
7. Padrões de desenvolvimento e padrões de projeto.
8. Gerenciamento de configuração.
9. Planejamento, gerenciamento, risco, PERT e CPM.
10. Documentação, reuso e ambientes de desenvolvimento.

#### Inteligência Artificial

1. Aprendizado de máquina e classificadores.
2. Árvores de decisão.
3. Redes neurais e transfer learning.
4. Regra de Bayes e classificadores bayesianos.
5. Algoritmos genéticos.
6. Conjuntos e lógica fuzzy.
7. Sistemas especialistas.
8. Busca heurística, A*, hill climbing e simulated annealing.
9. Representação do conhecimento.
10. PLN, agentes inteligentes, robótica e linguagens simbólicas.

#### Processamento de Imagens

1. Filtros digitais e filtro de média.
2. Filtragem, restauração, suavização e borramento.
3. Realce, histograma e contraste.
4. Codificação de imagens, JPEG e planos de bits.
5. Transformadas de imagens, DCT, Fourier e wavelet.
6. Amostragem e quantização.
7. Análise de imagens e visão computacional.
8. Reconhecimento de padrões.
9. Reconstrução tomográfica e percepção visual humana.

#### Redes de Computadores

1. Protocolos e serviços: TCP, UDP, DNS, HTTP, SMTP, POP, IMAP.
2. Camadas, modelo OSI e arquitetura TCP/IP.
3. Internet, endereçamento IP, sub-redes, máscaras e prefixos.
4. Interconexão de redes e roteadores.
5. Tipos de enlace, modos e meios de transmissão.
6. Taxa de transmissão, baud, latência e avaliação de desempenho.
7. Segurança, autenticação e DDoS/SYN.
8. Topologias e aplicações.
9. Redes de banda larga e especificação formal de protocolos.

#### Sistemas Distribuídos

1. Transparência em sistemas distribuídos.
2. Sistemas de arquivos distribuídos, servidores de nomes e localização.
3. Exclusão mútua, token, anel e algoritmos distribuídos.
4. Coordenação e sincronização de processos.
5. Tolerância a falhas.
6. Transações distribuídas.
7. Controle de concorrência distribuído.
8. Comunicação entre processos, RPC e passagem de mensagens.
9. Difusão de mensagens, multicast e publish/subscribe.
10. Memória compartilhada distribuída e segurança.

## Sinais Recentes Fortes

Aqui “recente” significa principalmente `2022-2025`; quando o padrão aparece em `2024-2025`, ele também já pertence ao período de prova online.

| Padrão | Evidência |
|---|---|
| Sistemas lineares/Gauss | 2022, 2023, 2024 e 2025; em 2023-2025 aparece logo na questão 1 |
| Lógica proposicional/primeira ordem | Bloco recorrente nas questões de matemática, normalmente perto de 13-15 |
| Boole/Karnaugh/circuitos lógicos | Aparece continuamente no fim de Matemática ou em Circuitos Digitais |
| Linguagens formais | Regex, autômatos, bombeamento e gramáticas aparecem em praticamente todos os anos recentes |
| Grafos | 2022-2025 direto; em 2025 aparecem conceitos, topológica e BFS em sequência |
| Memória/SO/arquitetura | Cache, memória virtual, processos, interrupções, barramento, paginação |
| BD | Serialização, transações, recuperação, SQL/álgebra relacional/modelo relacional |
| Redes/distribuídos | TCP/UDP/DNS, sub-redes, transparência, exclusão mútua, falhas |

## Matemática

### Álgebra Linear

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Sistemas de equações lineares, eliminação de Gauss | Muito alto | Sequência forte em 2022-2025; provável em 2026 |
| Transformações lineares e matrizes | Muito alto | Determinante, inversa, produto de matrizes, matriz de transformação aparecem ao longo de quase todo histórico |
| Espaços vetoriais, subespaços, bases | Alto | Frequente em anos antigos e recentes com “pertence ao subespaço”, “coordenadas em base”, “base de V” |
| Autovalores, autovetores, diagonalização | Alto | Não é anual, mas voltou em 2025 e foi forte em 2013-2015/2018 |
| Espaços com produto interno e projeções ortogonais | Alto | Projeção/produto interno aparecem em 2004, 2017, 2025 e correlatos |
| Método dos mínimos quadrados | Médio | Aparece, mas menos recorrente que Gauss/matrizes |
| Teorema espectral, adjunta, formas canônicas | Baixo | Conteúdo de edital, mas raramente cobrado explicitamente |

Para estudar primeiro: Gauss, matriz inversa/determinante, transformação linear, subespaço/base, autovalor, projeção ortogonal.

### Análise Combinatória

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Combinações | Muito alto | Equipes, escolhas, bilhetes, grupos, subconjuntos |
| Permutações | Alto | Anagramas, permutações simples e com restrição |
| Permutações com posições restritas | Alto | 2024 e 2025 reforçam restrições de posição/adjacência |
| Princípio de inclusão e exclusão | Alto | Senhas com todos os caracteres, divisibilidade, restrições “pelo menos” |
| Distribuição | Médio | Distribuir convites/objetos indistinguíveis aparece, mas não todo ano |
| Funções geradoras | Médio | Mais comum em provas antigas, menos forte no recorte recente |
| Enumeração por recursão | Médio | Aparece como recorrência/contagem, mas mistura com algoritmos |

Para estudar primeiro: combinações com restrição, permutação/anagrama, inclusão-exclusão, distribuição de objetos.

### Cálculo Diferencial e Integral

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Limites de funções e sequências | Muito alto | Aparece em praticamente todo recorte histórico |
| Continuidade e diferenciabilidade | Alto | Questões de continuidade por partes e intervalo de domínio |
| Máximos e mínimos | Alto | Extremos locais e Lagrange em 2025 |
| Integração de uma variável | Alto | Área sob curva, integral definida, primitivas |
| Integração aproximada | Alto recente | Regra dos trapézios em 2025; bom candidato por ser tópico explícito do edital |
| Funções de várias variáveis | Alto | Gradiente, derivadas parciais, função real de várias variáveis |
| Gradiente | Muito alto recente | 2022, 2023 e 2025 com gradiente explícito |
| Multiplicadores de Lagrange | Médio-alto | 2025 explícito; pode voltar |
| Taylor/Newton/jacobiana/implícita | Médio | Já apareceu, mas menos constante |

Para estudar primeiro: limites, continuidade, derivadas/extremos, integral definida, gradiente, Lagrange, trapézios.

### Geometria Analítica

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Vetores | Muito alto | Vetor diretor, vetor normal, soma/projeção |
| Produtos escalar, vetorial e misto | Alto | Produto escalar/vetorial aparece em vários anos |
| Reta no plano e no espaço | Muito alto | Equações de reta, reta perpendicular, reta em 3D, interseção |
| Planos | Alto | Interseção de planos, plano `xy`, plano perpendicular |
| Posições relativas, interseções, distâncias e ângulos | Muito alto | Distância ponto-reta, ângulo entre retas, interseções, baricentro/ponto médio |
| Círculo e esfera | Alto | Circunferência/círculo/esfera aparecem com regularidade |
| Coordenadas polares, cilíndricas e esféricas | Alto | Polares aparecem em 2018, 2019, 2025; esféricas em 2018 |

Para estudar primeiro: reta/plano, distância/ângulo/interseção, vetores/produtos, círculo/esfera, coordenadas polares.

### Lógica Matemática

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Lógica proposicional e de predicados | Muito alto | Equivalências, implicação, premissas e conclusões |
| Linguagem proposicional e de primeira ordem | Muito alto | Negação de “existe/todos” aparece repetidamente |
| Tabelas-verdade e estruturas de primeira ordem | Alto | Tabela verdade, número de linhas, valores lógicos |
| Relações de consequência | Alto | Questões de premissas verdadeiras e conclusão correta |
| Corretude, completude, compacidade, Löwenheim-Skolem | Baixo | Conteúdos formais do edital, mas pouco cobrados diretamente |
| Decidibilidade | Médio | Aparece mais em Computabilidade do que em Matemática |
| Prova automática, lógicas não clássicas | Baixo | Pouca evidência direta no histórico |

Para estudar primeiro: equivalência de implicação, contrapositiva, negação de quantificadores, tabela verdade, argumentos válidos.

### Matemática Discreta

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Conjuntos e álgebra de conjuntos | Muito alto | Operações com conjuntos, inclusão, interseção, subconjuntos |
| Funções e formas booleanas | Muito alto | Expressões booleanas, circuitos e funções lógicas |
| Álgebra booleana | Muito alto | De Morgan, identidades booleanas, dualidade |
| Minimização de funções booleanas | Muito alto | Karnaugh e mintermos são recorrentes |
| Iteração, indução e recursão | Alto | Função recursiva e recorrência aparecem em matemática e algoritmos |
| Teoria dos códigos | Alto recente | Hamming/paridade aparece em 2018 e 2025 |
| Relações de equivalência e ordem | Médio | Mais forte em anos antigos |
| Reticulados, monóides, grupos, anéis, domínios | Baixo | Pouca evidência direta |

Para estudar primeiro: conjuntos, De Morgan, álgebra booleana, Karnaugh/mintermos, Hamming/paridade, recursão/indução.

### Probabilidade e Estatística

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Descrição estatística dos dados | Muito alto | Média, mediana, moda, percentuais, séries estatísticas |
| Probabilidades em espaços discretos | Alto | Sorteios, peças defeituosas, eventos discretos |
| Distribuições de variáveis aleatórias | Alto | Distribuição discreta, densidade, variável aleatória |
| Esperança matemática | Alto | Valor esperado e tempo esperado aparecem várias vezes |
| Variância e coeficientes de correlação | Alto | Desvio padrão, variância, correlação |
| Regressão e correlação | Alto recente | Correlação explícita em 2025 |
| Testes de hipóteses, qui-quadrado, comparação de médias | Médio-baixo | Aparecem menos que estatística descritiva/probabilidade discreta |

Para estudar primeiro: média/desvio/variância, probabilidade discreta, distribuição discreta, esperança, correlação/regressão.

## Fundamentos da Computação

### Análise de Algoritmos

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Medidas de complexidade | Muito alto | Perguntas diretas sobre complexidade são quase anuais |
| Análise assintótica | Muito alto | Crescimento de funções, comparação assintótica |
| Notação Big O, Little o, Omega e Theta | Muito alto | Big-O/Theta aparecem com muita frequência |
| Relações de recorrência | Muito alto | Recorrências de algoritmos recursivos e divisão de problema |
| Análise de algoritmos iterativos e recursivos | Muito alto | Laços em C/Python e recursão tipo Fibonacci |
| Técnicas de cota inferior | Médio-baixo | Menos comum que Big-O/recorrência |
| Medidas empíricas | Baixo | Pouca cobrança explícita |

Para estudar primeiro: Big-O/Theta, recorrências, código com laços, recursão, comparação de crescimento.

### Algoritmos e Estrutura de Dados

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Algoritmos de pesquisa e ordenação | Muito alto | MergeSort, QuickSort, Shellsort, busca sequencial/binária |
| Listas, pilhas e filas | Muito alto | Definições e operações aparecem repetidamente |
| Árvores binárias, busca e balanceadas | Muito alto | Árvore binária, AVL, heap, BST, B/B+ em temas correlatos |
| Tabelas hash | Alto | Função hash, colisões, transformação de chaves |
| Recursividade | Alto | Aparece em algoritmos e técnicas de programação |
| Algoritmo guloso | Alto recente | 2022 e 2025 reforçam estratégia gulosa |
| Dividir e conquistar | Alto | MergeSort e estratégias algorítmicas |
| Backtracking, força bruta, pesquisa exaustiva | Médio | Cobrança mais alternada |
| Cadeias/processamento de cadeias | Médio | Aparece em expressões, strings e código |

Para estudar primeiro: ordenação, busca, hash, pilha/fila/lista, árvores, heap, recursão, guloso/dividir e conquistar.

### Arquitetura e Organização de Computadores

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Memórias | Muito alto | Cache, RAM, Flash, EEPROM, hierarquia de memória |
| Organização de memória | Muito alto | Cache associativo/direto, write-back/write-through |
| Barramento e interfaces | Alto recente | Barramento em 2022 e 2025 |
| Mecanismos de interrupção e exceção | Alto | Interrupção aparece em SO/arquitetura |
| Pipeline/paralelismo | Alto | Pipeline, paralelismo em nível de instrução |
| RISC e CISC | Médio-alto | Recorrente em histórico antigo e 2019 |
| Conjunto de instruções/modos de endereçamento | Médio | Aparece, mas menos previsível |
| Multiprocessadores/multicomputadores | Médio-baixo | Menos frequente |

Para estudar primeiro: cache, memória, barramento, interrupção, pipeline, RISC/CISC, endereçamento.

### Circuitos Digitais

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Minimização e otimização de funções combinatórias | Muito alto | Karnaugh, mintermos, soma de produtos |
| Circuitos combinatórios | Alto | Portas lógicas, circuito de saída, multiplexador/somador |
| Sistemas de numeração e códigos | Alto | Binário, hexadecimal, conversões |
| Componentes sequenciais e memória | Alto | Contadores, flip-flops, registradores |
| Máquinas de estado finito | Alto recente | Moore/Mealy em 2025 |
| Circuitos sequenciais síncronos/assíncronos | Médio-alto | Contadores e sincronismo aparecem |
| PLD | Médio | Aparece, mas menos recorrente |

Para estudar primeiro: Karnaugh/mintermos, portas lógicas, binário/hex, contadores/flip-flops, FSM Moore/Mealy.

### Linguagens de Programação

Prioridade: médio-alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Paradigmas | Alto recente | Imperativo, funcional, OO, lógico, declarativo em 2025 |
| Teoria dos tipos | Alto | Tipos, monomorfismo, sobrecarga, verificação dinâmica/estática |
| Polimorfismo | Alto recente | Questões de POO/UML/polimorfismo aparecem muito em 2022-2025 |
| Verificação e inferência de tipos | Alto recente | Explícito em 2025 |
| Conceitos gerais | Médio-alto | Subprogramas, passagem de parâmetros, linguagem C/Pascal |
| Semântica formal | Baixo | Pouca cobrança direta |

Para estudar primeiro: paradigmas, polimorfismo, sistemas de tipos, inferência/verificação de tipos, passagem de parâmetros.

### Linguagens Formais, Autômatos e Computabilidade

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Linguagens regulares e expressões regulares | Muito alto | Quase sempre aparece no bloco de Fundamentos |
| Autômatos finitos determinísticos/não determinísticos | Muito alto | AFD/AFND e linguagem aceita são recorrentes |
| Gramáticas | Muito alto | Gramática regular, CFG, LL/LR em compiladores também |
| Linguagens livres de contexto e autômatos de pilha | Alto recente | 2022 e 2025 têm PDA/CFG |
| Propriedades das linguagens e lema do bombeamento | Muito alto recente | 2022 e 2025 explícitos |
| Máquina de Turing e problemas indecidíveis | Alto | Aparece em 2019 e 2024, menos anual que regex |
| Classes P, NP, NP-completo e NP-difícil | Alto | Frequente em complexidade/computabilidade |
| Métodos de redução | Médio | Aparece junto de NP/decidibilidade |

Para estudar primeiro: regex, AFD/AFND, gramáticas regulares/CFG, bombeamento, PDA, Turing, P/NP.

### Organização de Arquivos e Dados

Prioridade: médio-alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Organização, estrutura e operação de arquivos | Muito alto recente | Arquivos, registros, metadados e SGDA aparecem em 2023-2025 |
| Técnicas de pesquisa | Alto recente | Full-text em 2025; índices e estruturas de busca em outros anos |
| Compressão de dados, áudio, imagem e vídeo | Muito alto | Huffman, LZW, RLE, compressão de imagens |
| Diretórios e sistema de arquivos | Alto | Diretórios e sistemas de arquivo aparecem em SO/arquivos |
| Dados e metadados | Alto recente | Metadados em 2023 |
| Codificação/decodificação | Médio-alto | Huffman/codificação aparece |
| Representação digital/analógica | Baixo-médio | Menos cobrado diretamente |

Para estudar primeiro: arquivos/registros/metadados, organização de arquivos, full-text/índices, compressão RLE/Huffman/LZW.

### Sistemas Operacionais

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Gerenciamento de memória | Muito alto | Memória virtual, paginação, page fault, working set, swap |
| Conceito de processo | Muito alto | Processos, threads, fork, estados de processo |
| Gerência de processos/processador | Alto | Escalonamento, round-robin, turnaround |
| Comunicação, concorrência e sincronização | Alto | Deadlock, exclusão mútua, seção crítica |
| Gerenciamento de arquivos | Alto | Alocação de blocos, clusters, arquivos mapeados |
| Gerenciamento de dispositivos de E/S | Alto recente | Camadas de E/S, drivers, interrupção |
| Alocação de recursos | Médio | Aparece junto de deadlock e SO distribuído |

Para estudar primeiro: paginação/page fault/working set, processos/fork/threads, escalonamento, deadlock/sincronização, E/S.

### Técnicas de Programação

Prioridade: médio-alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Comandos de linguagem | Muito alto recente | `if`, `for`, `while`, seleção, laços, trace de código |
| Tipos de dados básicos e estruturados | Alto | Inteiro, real, char, boolean, registros/structs |
| Modularidade e abstração | Alto | Programação modular/top-down, abstração |
| Desenvolvimento de algoritmos | Médio-alto | Tentativa e erro, decomposição, estratégia |
| Metodologia de desenvolvimento de programas | Médio | Cobrança indireta |

Para estudar primeiro: trace de código C/Python, laços/condicionais, tipos, modularidade, decomposição.

### Teoria dos Grafos

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Grafos orientados e não-orientados | Muito alto | Definições e propriedades aparecem direto |
| Caminhos | Muito alto | Caminho, ciclo, percurso, alcançabilidade |
| Busca em largura e profundidade | Muito alto | BFS/DFS muito recorrentes; BFS voltou em 2025 |
| Ordenação topológica | Muito alto recente | 2017, 2018 e 2025; forte para DAG |
| Árvore geradora | Alto | Kruskal/árvore geradora mínima |
| Algoritmos do menor caminho | Alto | Dijkstra/Floyd/caminho mais curto |
| Conectividade | Alto | Conexo, fortemente conectado |
| Planaridade/coloração | Médio | Aparece, mas menos que busca/topológica |

Para estudar primeiro: conceitos de grafo, caminho/ciclo, BFS/DFS, topológica, árvore geradora mínima, menor caminho.

## Tecnologia de Computação

### Banco de Dados

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Gerenciamento de transações | Muito alto | Serialização, escalonamentos, estados de transação |
| Concorrência | Muito alto | Controle de concorrência, timestamp, deadlock |
| Recuperação após falha | Muito alto | ARIES, undo/redo, steal/no-force |
| Modelo de dados | Muito alto | Modelo relacional, normalização, esquema de relação |
| Linguagens de consulta | Muito alto | SQL e álgebra relacional aparecem com frequência |
| Integridade | Alto | Chave primária/estrangeira e restrições |
| Bancos de dados distribuídos | Alto | Transações e dados distribuídos aparecem |
| Mineração de dados | Médio | K-means e padrões frequentes aparecem, mas não todo ano |

Para estudar primeiro: serializabilidade, recuperação, concorrência, SQL/álgebra relacional, normalização, chaves/restrições.

### Compiladores

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Análise léxica | Alto | Tokens, expressões regulares, analisador léxico |
| Análise sintática | Muito alto recente | LR/bottom-up, LL, parsers, derivação |
| Esquemas de tradução | Alto | Esquema/definição dirigida pela sintaxe |
| Representação intermediária | Alto | Aparece em 2024 e histórico anterior |
| Tabelas de símbolos | Médio | Menos recorrente, mas clássico |
| Ambientes de tempo de execução | Médio | Registro de ativação e chamadas |
| Geração de código e otimização | Médio-alto | Alocação de registradores, blocos básicos, otimização |
| Bibliotecas/compilação separada | Baixo | Pouca evidência direta |

Para estudar primeiro: análise léxica/sintática, LL/LR, derivação, tradução dirigida pela sintaxe, representação intermediária, registradores/otimização.

### Computação Gráfica

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Transformações geométricas 2D/3D | Alto | Matrizes de rotação/translação/escala |
| Coordenadas homogêneas e matrizes | Médio-alto | Aparece junto de transformações |
| Remoção de superfícies ocultas | Muito alto | Z-buffer e back-face são recorrentes |
| Modelos de tonalização | Muito alto recente | Gouraud/Phong em 2022 e 2025 |
| Aplicação de texturas | Muito alto recente | Textura, bump mapping, mipmapping |
| Rendering/fontes de luz | Alto | Luz direcional, ray tracing, renderização |
| Projeção/câmera/visualização | Médio | Aparece, mas alterna |
| Aliasing/antialiasing | Médio-baixo | Menos recorrente |

Para estudar primeiro: Z-buffer, Phong/Gouraud, texturas/mipmapping, fontes de luz/rendering, transformações 2D/3D.

### Engenharia de Software

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Engenharia de requisitos | Muito alto | RNF/produto/organizacional/externo aparecem |
| Verificação, validação e teste | Muito alto | Testes de regressão, sistema, V&V |
| Manutenção | Alto | Manutenção corretiva/adaptativa, legado |
| Reengenharia/engenharia reversa | Alto recente | 2022 e 2025 reforçam reengenharia/refatoração |
| Ciclo de vida | Alto recente | Incremental/espiral/cascata/prototipação |
| Qualidade de software | Alto | Gestão e garantia de qualidade |
| Gerenciamento de configuração | Alto recente | 2024 |
| Padrões de desenvolvimento | Alto recente | Strategy em 2025; MVC/Broker em anos anteriores |
| Planejamento/gerenciamento | Médio-alto | PERT/CPM/risco/gerência de projeto |

Para estudar primeiro: requisitos, testes/V&V, manutenção, reengenharia, ciclo de vida, qualidade, padrões.

### Inteligência Artificial

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Aprendizado de máquina | Muito alto recente | Classificadores supervisionados, SVM, k-means, KNN |
| Árvores de decisão | Alto recente | 2023 e 2025 |
| Redes neurais | Alto recente | Redes neurais e transfer learning |
| Algoritmos genéticos | Alto recente | 2022 e 2024 |
| Regra de Bayes | Alto | Bayes/Naive Bayes aparece |
| Conjuntos e lógica fuzzy | Alto | Fuzzy em 2023 |
| Sistemas especialistas | Médio-alto | 2024 e histórico antigo |
| Busca heurística/A*/simulated annealing | Médio | Clássico, mas menos recente que ML |
| PLN | Médio | 2019 explícito, possível mas não tão forte |

Para estudar primeiro: árvore de decisão, redes neurais, classificadores, Bayes, K-means/SVM/KNN, genéticos, fuzzy.

### Processamento de Imagens

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Filtros digitais | Alto recente | Filtro de média e filtragem em 2024/2025 |
| Amostragem e quantização | Alto | Quantização aparece em 2018/2024 |
| Transformadas de imagens | Alto recente | DCT/JPEG em 2025; wavelet/Fourier no histórico |
| Realce | Alto | Histograma/equalização/contraste |
| Filtragem e restauração | Muito alto | Restauração, borramento, suavização |
| Codificação | Alto | JPEG, planos de bits, codificação de imagem |
| Análise de imagens e visão computacional | Médio-alto | Visão estéreo e mapa de disparidade |
| Reconhecimento de padrões | Médio | Aparece, mas muitas vezes em IA |

Para estudar primeiro: filtro média/suavização, restauração, histograma/realce, JPEG/DCT, quantização/amostragem, visão estéreo.

### Redes de Computadores

Prioridade: muito alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Protocolos e serviços | Muito alto | TCP, UDP, DNS, HTTP, SMTP/POP/IMAP |
| Modelos de arquitetura e camadas | Muito alto | OSI/TCP-IP, camada de enlace/transporte/aplicação |
| Interconexão de redes | Muito alto | Roteador, máscara, sub-rede, prefixo |
| Tipos de enlace/meios/transmissão | Alto recente | Baud, velocidade de sinalização em 2025 |
| Segurança e autenticação | Alto recente | DDoS/SYN em 2025 |
| Avaliação de desempenho | Médio | Taxa, latência, largura de bit, canal |
| Redes de banda larga | Baixo | Pouca evidência direta |

Para estudar primeiro: TCP/UDP/DNS/HTTP, OSI/TCP-IP, sub-redes/prefixos, roteadores, baud/taxa, DDoS/SYN.

### Sistemas Distribuídos

Prioridade: alto.

| Subtópico do edital | Prioridade | Evidência prática |
|---|---|---|
| Sistemas operacionais distribuídos | Muito alto | Transparência, arquivos distribuídos, nomes, localização |
| Exclusão mútua | Muito alto recente | Anel/token, Maekawa/servidor central em histórico recente |
| Tolerância a falhas | Alto | Tipos de falha e comportamento de servidor |
| Transações distribuídas | Alto | Transação cliente/distribuída e aninhada |
| Controle de concorrência | Alto recente | Otimista, timestamp e distribuído |
| Comunicação entre processos | Alto | RPC, cliente-servidor, mensagens |
| Difusão de mensagens | Médio | Publish/subscribe e multicast aparecem, mas alternam |
| Coordenação e sincronização | Alto | Aparece junto de exclusão mútua e relógios lógicos |

Para estudar primeiro: transparência, arquivos distribuídos, exclusão mútua por anel/token, falhas, transações distribuídas, comunicação/RPC.

## Apostas Práticas para 2026

| Chance | Assuntos |
|---|---|
| Muito alta | Gauss/sistema linear, lógica proposicional/quantificadores, Boole/Karnaugh, Big-O/recorrência, grafos, regex/autômatos, memória virtual/cache, BD transações/recuperação, TCP/UDP/DNS/sub-redes |
| Alta | Autovalor/diagonalização, gradiente/integral/trapézios, estatística descritiva/correlação, pilha/fila/hash/árvores, FSM/circuitos, compiladores LR/LL/tradução, textura/shading/JPEG/filtros, requisitos/testes/reengenharia, ML/árvores/redes/genéticos |
| Média | Taylor/Newton, mínimos quadrados, funções geradoras, testes estatísticos, semântica formal, PLD, teoria dos domínios, lógicas não clássicas, redes de banda larga |

Se o tempo de estudo for curto, a ordem recomendada é:

1. Matemática: Gauss, reta/plano/vetores, cálculo básico, lógica, Boole/Karnaugh, probabilidade/estatística.
2. Fundamentos: Big-O, ED, grafos, LFA, SO/arquitetura, circuitos.
3. Tecnologia: BD, redes/distribuídos, engenharia, compiladores, gráfica/imagens, IA.
