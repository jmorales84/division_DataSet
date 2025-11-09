import pandas as pd
import arff
from sklearn.model_selection import train_test_split
import tempfile
import codecs

def load_arff_loose(file_obj):
    """
    Carga archivos ARFF incluso si tienen errores de formato o tipos no válidos.
    Convierte todos los atributos a STRING para evitar errores como:
    'Bad @ATTRIBUTE type'.
    """

    # Guardar archivo subido temporalmente
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".arff")

    for chunk in file_obj.chunks():
        temp.write(chunk)
    temp.close()

    # Leer línea por línea, corrigiendo atributos problemáticos
    cleaned_lines = []
    with codecs.open(temp.name, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "@ATTRIBUTE" in line.upper():
                parts = line.strip().split()

                # Si el atributo tiene tipo inválido, forzamos a STRING
                if len(parts) >= 3:
                    line = f"{parts[0]} {parts[1]} STRING\n"
            
            cleaned_lines.append(line)

    # Guardar archivo ARFF corregido
    clean_file = tempfile.NamedTemporaryFile(delete=False, suffix=".arff")
    with open(clean_file.name, "w") as f:
        f.writelines(cleaned_lines)

    # Cargar con liac-arff
    dataset = arff.load(open(clean_file.name, "r"))

    attributes = [a[0] for a in dataset["attributes"]]
    df = pd.DataFrame(dataset["data"], columns=attributes)

    return df


def process_arff(file_obj):
    """
    Procesa un archivo ARFF:
    - Carga robusta (corrigiendo tipos inválidos)
    - División del dataset 60/40 → luego 50/50
    - Obtiene preview (primeras 5 filas)
    """

    df = load_arff_loose(file_obj)

    # División 60% train / 40% test
    train_set, test_set = train_test_split(df, test_size=0.4, random_state=42)

    # División 40% test → 20% validation + 20% test final
    val_set, test_set = train_test_split(test_set, test_size=0.5, random_state=42)

    # Devolver resultados para el frontend
    return {
        "total": len(df),
        "train": len(train_set),
        "validation": len(val_set),
        "test": len(test_set),
        "columns": df.columns.tolist(),
        "preview": df.head(5).values.tolist()  #  Primera fila para la tabla
    }
