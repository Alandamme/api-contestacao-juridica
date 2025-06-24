import os

def listar_tudo(raiz):
    for root, dirs, files in os.walk(raiz):
        nivel = root.replace(raiz, '').count(os.sep)
        indent = ' ' * 4 * nivel
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (nivel + 1)
        for f in files:
            print(f"{subindent}{f}")

if __name__ == "__main__":
    # Caminho raiz do projeto dentro do container Render
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(f"Listando arquivos a partir de: {raiz}")
    listar_tudo(raiz)
