import os

caminho = "/opt/render/project/src/static/modelos"
print("Listando arquivos em:", caminho)
print(os.listdir(caminho) if os.path.exists(caminho) else "Caminho não existe")
