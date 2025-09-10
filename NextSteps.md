# Desafio TADS \- Próximos Passos

# Iterator

# Singleton \[Terminar\]

**Use the Singleton pattern when a class in your program should have just a single instance available to all clients; for example, a single database object shared by different parts of the program.**

# Padrão Strategy (Estratégia)

O padrão Strategy será aprimorado para tornar a política de enfileiramento flexível. Atualmente, a fila opera com a política FIFO (First-In, First-Out). O objetivo é permitir que essa política seja alterada de forma dinâmica, sem a necessidade de reescrever a lógica do process\_requests\_from\_queue.

Justificativa: O problema menciona que o "ambiente interno é ruidoso" e que "múltiplos clientes internos podem disparar múltiplas requisições simultâneas". Em cenários mais complexos, o FIFO pode não ser o ideal. Por exemplo, pode ser necessário priorizar requisições de clientes críticos ou descartar requisições que já expiraram. O padrão Strategy permitirá a criação e a substituição de políticas de fila como:

* FIFO: A política atual.

* Prioridade: Reorganiza a fila com base em um campo de prioridade na requisição.

* Descarte com TTL (Time-to-Live): Remove requisições da fila que excederam um tempo limite, evitando o processamento de dados desatualizados.

# Padrão Circuit Breaker (Disjuntor)

O Circuit Breaker será adicionado para aumentar a resiliência do sistema frente a falhas da API externa. Se a API parceira começar a apresentar alta latência ou responder com erros repetidamente, o circuito se "abrirá", impedindo novas chamadas por um período.

Justificativa: O disjuntor evita que o proxy sobrecarregue uma API que já está com problemas, o que poderia agravar a situação. Em vez de continuar tentando, o proxy falhará rapidamente, retornando um erro para o cliente interno ou uma resposta de fallback (se aplicável), protegendo o sistema como um todo.

* Fases do Circuit Breaker:

  1. Closed (Fechado): Operação normal. As chamadas são permitidas.

  2. Open (Aberto): Quando o número de falhas atinge um limite, o circuito se abre. Todas as chamadas subsequentes falham imediatamente, sem tentar se conectar à API externa.

  3. Half-Open (Meio-Aberto): Após um tempo de espera, uma única chamada de "teste" é permitida. Se ela for bem-sucedida, o circuito volta para o estado Closed. Caso contrário, ele retorna para o estado Open.
