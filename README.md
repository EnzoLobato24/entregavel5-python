

## Objetivo
Ler um CSV e validar e-mail, CPF, telefone e data com regex (`re`), tratar exceções e produzir um relatório de dados válidos, inválidos e estatísticas

## Arquivos
- `sistema_analise_dados.py`: script principal.
- `dados.csv`: dados de exemplo.
- `relatorio.txt`: criado automaticamente após a análise.
- `README.md`: documentação.


## Exemplo de entrada
```csv
email,cpf,telefone,data
ana.silva@example.com,123.456.789-09,(11) 91234-5678,15/03/2025
bruno@example.com,12345678901,11987654321,2025-04-20
email-invalido,111,telefone,31/02/2025
carla.mendes@example.org,987.654.321-00,+55 21 99876-5432,2024-12-01
```
## Justificativa das validações
- E-mail: `^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$` valida uma estrutura comum de endereço eletrônico.
- CPF: `^(?:\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$` aceita 11 dígitos com ou sem pontuação. A atividade verifica o formato; não calcula os dígitos verificadores do CPF.
- Telefone: aceita formatos comuns com DDD e prefixo opcional `+55`.
- Data: aceita `DD/MM/AAAA` ou `AAAA-MM-DD`; depois da regex, `datetime.strptime` confirma se a data existe no calendário.
- `^` e `$` delimitam o campo inteiro; `\d` representa dígitos; `\w` representa caracteres de palavra.

## Exceções
- `FileNotFoundError`: arquivo inexistente.
- `ValueError`: valor ou data que não pode ser convertido.
- `KeyError`: coluna obrigatória ausente no CSV.
- `UnicodeDecodeError` e `csv.Error`: problemas de codificação ou leitura.
- `FormatoInvalidoError`: exceção personalizada para regra específica do projeto.
- `try/except/else/finally`: trata erros, separa o caminho de sucesso e fecha o arquivo mesmo quando há falha.

## Exemplo de saída
O relatório informa total de registros, quantidade de válidos e inválidos, taxa de aprovação, dados válidos e problemas encontrados por linha. Com os dados de exemplo, o registro com e-mail inválido e data `31/02/2025` será classificado como inválido.

