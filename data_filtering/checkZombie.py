
import ROOT
import os
from glob import glob

output_dir = "/mnt/bidone/data_jessica_filtered_v2"

files = sorted(glob(os.path.join(output_dir, "*_reduced.root")))

valid_files = []
invalid_files = []

for i, file in enumerate(files, 1):

    f = None

    try:
        f = ROOT.TFile.Open(file, "READ")

        if not f or f.IsZombie():
            raise RuntimeError("File Zombie")

        if f.TestBit(ROOT.TFile.kRecovered):
            raise RuntimeError("File recuperato da ROOT")

        tree = f.Get("Events")

        if not tree or not tree.InheritsFrom("TTree"):
            raise RuntimeError("TTree Events mancante")

        n_entries = tree.GetEntries()

        if n_entries > 0:
            result = tree.GetEntry(n_entries - 1)

            if result <= 0:
                raise RuntimeError("Errore lettura eventi")

        valid_files.append(file)

    except (OSError, RuntimeError) as e:
        print(f"FILE NON VALIDO: {file}")
        print(f"Motivo: {e}")
        invalid_files.append(file)

    finally:
        if f:
            f.Close()

    if i % 100 == 0:
        print(f"Controllati {i}/{len(files)} file")

print("\n===== RISULTATI =====")
print("File controllati:", len(files))
print("File validi:", len(valid_files))
print("File non validi:", len(invalid_files))

# Salva elenco dei file danneggiati
with open("invalid_files.txt", "w") as out:
    for file in invalid_files:
        out.write(file + "\n")

