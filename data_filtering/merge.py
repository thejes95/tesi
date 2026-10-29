
import os
import glob
import subprocess



INPUT_DIR = "/mnt/bidone/data_jessica_filtered_v2"

OUTPUT_DIR = "/mnt/bidone/data_jessica_merged"

os.makedirs(OUTPUT_DIR, exist_ok=True)

FILES_PER_GROUP = 94

EXPECTED_FILES = 2796


# ============================================================
# 2. RICERCA DEI FILE ROOT
# os.path.join(..) --> costruisce il percorso e cerca file con estestione root
# glob.glob() --> restituisce una lista contenente tutti i file trovati
# sorted -> ordina alfabeticamente
# ============================================================

files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.root")))


# ============================================================
# 3. SUDDIVISIONE IN GRUPPI DA 94
# usiamo una list comprehnsion (modo compatto per costruire una lista)
# range (..) -->genera indici 0,94,188,... e files[i:i + ..] per ciscun indice i seleziona un gruppo di massimo 94 files files[0:94], files[94:188]....
# ============================================================

groups = [
    files[i:i + FILES_PER_GROUP]
    for i in range(0, len(files), FILES_PER_GROUP)]

# ============================================================
# 4. UNIONE DEI FILE CON HADD
# funzione enumerate restituisce i = numero del gruppo, group=lista dei file root appartenenti a quel gruppo
# ============================================================



for i, group in enumerate(groups, start=1):

    output_name = f"Scouting_merged_{i:02d}.root"

    output_path = os.path.join(
        OUTPUT_DIR,
        output_name
    )

    # Non sovrascriviamo file già presenti
    if os.path.exists(output_path):
        raise FileExistsError(
            f"File già esistente: {output_path}"
        )

    # Comando hadd con 4 processi 
    command = [
        "hadd",
        "-j", "4",
        output_path
    ] + group

    subprocess.run(
        command,
        check=True
    )

    # Dimensione del file finale --> dividendo per 1024^3 convertiamo la dimensione in gb
    size_gb = os.path.getsize(output_path) / (1024 ** 3)

    print("\nFile creato:", output_name)
    print(f"Dimensione: {size_gb:.2f} GiB")


# ============================================================
# 5. RIEPILOGO FINALE
# ============================================================


print("\n====================================")
print("UNIONE COMPLETATA!")
print("====================================")

print("File originali:", len(files))
print("File finali:", len(groups))
print("File utilizzati:", sum(len(g) for g in groups))


