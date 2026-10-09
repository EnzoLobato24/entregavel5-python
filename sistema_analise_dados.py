
import csv
import re
from datetime import datetime
from pathlib import Path


class FormatoInvalidoError(Exception):
    """Erro personalizado para problemas específicos dos dados."""


PADROES = {
    "email": re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$", re.IGNORECASE),
    "cpf": re.compile(r"^(?:\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$"),
    "telefone": re.compile(r"^(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9?\d{4})-?\d{4}$"),
    "data": re.compile(r"^(?:\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})$"),
}
COLUNAS = {"email", "cpf", "telefone", "data"}


def validar_email(valor):
    return bool(PADROES["email"].fullmatch(valor.strip()))


def validar_cpf(valor):
   
    return bool(PADROES["cpf"].fullmatch(valor.strip()))


def validar_telefone(valor):
    return bool(PADROES["telefone"].fullmatch(valor.strip()))


def validar_data(valor):
    valor = valor.strip()
    if not PADROES["data"].fullmatch(valor):
        return False
    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            datetime.strptime(valor, formato)
            return True
        except ValueError:
            pass
    return False


def validar_registro(registro, numero_linha):
    problemas = []
    validadores = {
        "email": validar_email,
        "cpf": validar_cpf,
        "telefone": validar_telefone,
        "data": validar_data,
    }
    for campo, validador in validadores.items():
        try:
            valor = registro[campo].strip()
        except KeyError as erro:
            raise KeyError(f"Coluna obrigatória ausente: {erro.args[0]}") from erro
        except AttributeError as erro:
            raise FormatoInvalidoError(
                f"Linha {numero_linha}: campo '{campo}' vazio ou ausente."
            ) from erro
        if not valor:
            problemas.append(f"{campo}: campo vazio")
        elif not validador(valor):
            problemas.append(f"{campo}: formato inválido")
    return problemas


def analisar_csv(caminho):
    validos, invalidos = [], []
    total = 0
    arquivo = None
    try:
        arquivo = open(caminho, "r", encoding="utf-8-sig", newline="")
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames is None:
            raise FormatoInvalidoError("CSV vazio ou sem cabeçalho.")

        leitor.fieldnames = [nome.strip().lower() for nome in leitor.fieldnames]
        ausentes = COLUNAS - set(leitor.fieldnames)
        if ausentes:
            raise KeyError("Colunas obrigatórias ausentes: " + ", ".join(sorted(ausentes)))

        for numero_linha, registro in enumerate(leitor, start=2):
            total += 1
            try:
                problemas = validar_registro(registro, numero_linha)
                if problemas:
                    invalidos.append({
                        "linha": numero_linha, "dados": registro,
                        "problemas": problemas
                    })
                else:
                    validos.append({"linha": numero_linha, "dados": registro})
            except FormatoInvalidoError as erro:
                invalidos.append({
                    "linha": numero_linha, "dados": registro,
                    "problemas": [str(erro)]
                })
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado: {caminho}")
        raise
    except (UnicodeDecodeError, csv.Error) as erro:
        print(f"Erro ao ler o CSV: {erro}")
        raise
    except KeyError as erro:
        print(f"Erro na estrutura do CSV: {erro}")
        raise
    except ValueError as erro:
        print(f"Erro de valor: {erro}")
        raise
    else:
        return {"total": total, "validos": validos, "invalidos": invalidos}
    finally:
        if arquivo is not None:
            arquivo.close()


def gerar_relatorio(resultado, caminho_saida="relatorio.txt"):
    total = resultado["total"]
    validos = resultado["validos"]
    invalidos = resultado["invalidos"]
    percentual = len(validos) / total * 100 if total else 0.0

    linhas = [
        "=" * 72,
        "RELATÓRIO — SISTEMA DE ANÁLISE DE DADOS",
        "=" * 72,
        f"Total de registros: {total}",
        f"Registros válidos: {len(validos)}",
        f"Registros inválidos: {len(invalidos)}",
        f"Taxa de aprovação: {percentual:.2f}%",
        "", "REGISTROS VÁLIDOS", "-" * 72,
    ]
    if validos:
        for item in validos:
            d = item["dados"]
            linhas.append(
                f"Linha {item['linha']}: email={d['email']}, CPF={d['cpf']}, "
                f"telefone={d['telefone']}, data={d['data']}"
            )
    else:
        linhas.append("Nenhum registro válido.")

    linhas.extend(["", "REGISTROS INVÁLIDOS", "-" * 72])
    if invalidos:
        for item in invalidos:
            d = item["dados"]
            linhas.append(
                f"Linha {item['linha']}: email={d.get('email', '')}, "
                f"CPF={d.get('cpf', '')}, telefone={d.get('telefone', '')}, "
                f"data={d.get('data', '')}"
            )
            for problema in item["problemas"]:
                linhas.append(f"  - {problema}")
    else:
        linhas.append("Nenhum registro inválido.")
    linhas.append("=" * 72)

    conteudo = "\n".join(linhas)
    print("\n" + conteudo)
    try:
        with open(caminho_saida, "w", encoding="utf-8") as saida:
            saida.write(conteudo + "\n")
    except OSError as erro:
        print(f"Não foi possível salvar o relatório: {erro}")
        raise
    else:
        print(f"\nRelatório salvo em: {Path(caminho_saida).resolve()}")


def main():
    caminho = input("Caminho do CSV [dados.csv]: ").strip() or "dados.csv"
    try:
        resultado = analisar_csv(caminho)
    except FileNotFoundError:
        print("Confira o nome e a pasta do arquivo e tente novamente.")
    except (KeyError, ValueError, UnicodeDecodeError, csv.Error,
            FormatoInvalidoError) as erro:
        print(f"Análise interrompida: {erro}")
    else:
        gerar_relatorio(resultado)
    finally:
        print("Execução da análise finalizada.")


if __name__ == "__main__":
    main()
