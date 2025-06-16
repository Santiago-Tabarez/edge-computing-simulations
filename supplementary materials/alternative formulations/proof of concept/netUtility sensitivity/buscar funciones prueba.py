import os
import sys

# 1. Agregamos manualmente el path a las DLLs de Julia
julia_bin = r"C:\Users\santi\AppData\Local\Programs\Julia-1.11.5\bin"
os.environ["JULIA_BINDIR"] = julia_bin
os.environ["PATH"] = julia_bin + os.pathsep + os.environ["PATH"]

# 2. Verificamos que la ruta está bien
if not os.path.exists(os.path.join(julia_bin, "libpcre2-8.dll")):
    print("ERROR: No se encuentra libpcre2-8.dll en la ruta especificada.")
    sys.exit(1)

# 3. Importamos Julia para probar si funciona
from julia import Julia
jl = Julia(compiled_modules=False)

print("✅ Julia cargada correctamente desde Python.")
