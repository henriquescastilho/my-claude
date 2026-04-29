---
name: Banner ASCII em .start.sh
description: Regras para criar .start.sh com banner ASCII art do nome do projeto em cores ANSI magenta, template e convenções
type: reference
originSessionId: 437f0ec3-415d-4bfc-92b2-f6241d61cb1b
---
## Banner ASCII em .start.sh

Todo projeto DEVE ter um `.start.sh`. Se ao entrar num projeto ele não existir, Claude DEVE criar automaticamente.
Ao criar qualquer arquivo `.start.sh`, SEMPRE incluir um banner ASCII art do nome do projeto no topo do script, exibido com cores ANSI magenta/roxo antes de iniciar o servidor.

### Como gerar o banner
- Usar `figlet` com a fonte "ANSI Shadow" ou equivalente blocky/pixel para gerar o texto
- Se `figlet` não estiver disponível, gerar manualmente o ASCII art em estilo blocky semelhante
- Envolver com códigos ANSI para cor magenta: `\033[35m` (magenta) e `\033[0m` (reset)
- O banner deve ser o NOME DO PROJETO em letras grandes

### Se for projeto novo criado pela DME
- Adicionar linha `by DME TECHNOLOGY` abaixo do banner, em cor cyan (`\033[36m`)

### Template padrão
```bash
#!/bin/bash

echo -e "\033[35m"
# ASCII art do nome do projeto aqui (gerado com figlet ou manual)
echo -e "\033[0m"
echo -e "\033[36m                            by DME TECHNOLOGY\033[0m"
echo ""

# resto do script de start...
```

### Regras
- O banner SEMPRE aparece antes de qualquer outro output do script
- Usar `echo -e` para interpretar os códigos ANSI
- O nome no banner deve corresponder ao nome real do projeto
- Se o projeto já existir e NÃO for criado pela DME, omitir a linha "by DME TECHNOLOGY"
