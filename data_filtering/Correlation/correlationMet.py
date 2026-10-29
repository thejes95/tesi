
import ROOT
import glob
import os
import time

# ============================================================
# 1. CONFIGURAZIONE INIZIALE
# ============================================================

# Non apriamo finestre grafiche.
ROOT.gROOT.SetBatch(True)

# Utilizziamo 4 thread per elaborare i dati.
ROOT.EnableImplicitMT(4)

# Cartella dei quattro segnali.
SIGNAL_DIR = "/home/PERSONALE/jessica.caselli4/datafiltering/Correlation"

# MODIFICA questo percorso con quello dei file Scouting ridotti.
BKG_DIR = "/mnt/bidone/data_jessica_filtered"

# Cartella in cui salvare l'immagine.
OUTPUT_DIR = "/home/PERSONALE/jessica.caselli4/datafiltering/Correlation/plot"

# Creiamo la cartella se non esiste.
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Nome dell'albero ROOT.
TREE_NAME = "Events"


# ============================================================
# 2. FILE DEI QUATTRO SEGNALI
# ============================================================

signal_files = {
    "A -> 4l":
        "Ato4l_lepFilter_13TeV_filtered_NEW.root",

    "LQ":
        "leptoquark_LOWMASS_lepFilter_13TeV_filtered_NEW.root",

    "h+ -> tau nu":
        "hChToTauNu_13TeV_PU20_filtered_NEW.root",

    "h0 -> tau tau":
        "hToTauTau_13TeV_PU20_filtered_NEW.root"
}

# Colori delle cinque distribuzioni.
colors = {
    "Background": ROOT.kGreen + 2,
    "A -> 4l": ROOT.kMagenta,
    "LQ": ROOT.kViolet,
    "h+ -> tau nu": ROOT.kCyan + 1,
    "h0 -> tau tau": ROOT.kYellow + 2
}


# ============================================================
# 3. DEFINIZIONE DEGLI ISTOGRAMMI
# ============================================================

# Per ogni variabile:
# (numero di bin, minimo, massimo, titolo asse X)
#
# Non applichiamo alcun filtro ai dati.

variables = {
    "ScoutingMET_pt": (
        100, -20, 1000,
        "MET p_{T} [GeV]"
    ),

    "ScoutingMET_phi": (
        64, -4, 4,
        "MET #phi [rad]")
}


# ============================================================
# 4. CARICAMENTO DEI FILE SCOUTING
# ============================================================

print("\nCerco i file Scouting...")

# Cerchiamo i file ROOT già ridotti.
background_files = sorted(
    glob.glob(
        os.path.join(BKG_DIR, "*_reduced.root")
    )
)

print("File Scouting trovati:", len(background_files))

if not background_files:
    raise RuntimeError(
        "Nessun file trovato. Controlla BKG_DIR."
    )

# Per una prova veloce con 10 file:
# background_files = background_files[:10]

# TChain concatena logicamente tutti i file.
chain = ROOT.TChain(TREE_NAME)

for filename in background_files:
    chain.Add(filename)

# Creiamo il DataFrame del background.
df_bkg = ROOT.RDataFrame(chain)


# ============================================================
# 5. CARICAMENTO DEI QUATTRO SEGNALI
# ============================================================

df_signals = {}

for name, filename in signal_files.items():

    full_path = os.path.join(
        SIGNAL_DIR,
        filename
    )

    # Controlliamo che il file esista.
    if not os.path.isfile(full_path):
        raise FileNotFoundError(full_path)

    df_signals[name] = ROOT.RDataFrame(
        TREE_NAME,
        full_path
    )

    print("Segnale caricato:", name)


# ============================================================
# 6. PRENOTAZIONE DEGLI ISTOGRAMMI
# ============================================================

# Prenotiamo tutti gli istogrammi prima di GetValue().
#
# Histo1D è lazy: non avvia subito il calcolo.
# ROOT può quindi riempire pt, phi ed eta
# durante un'unica scansione di ciascun campione.

print("\nPrenotazione degli istogrammi...")

# ---------------- BACKGROUND ----------------

h_bkg_results = {}

for variable, (nbins, xmin, xmax, xlabel) in variables.items():

    h_bkg_results[variable] = df_bkg.Histo1D(
        (
            f"h_bkg_{variable}",
            "",
            nbins,
            float(xmin),
            float(xmax)
        ),
        variable
    )


# ---------------- SEGNALI ----------------

h_signal_results = {}

for i, (name, df) in enumerate(df_signals.items()):

    h_signal_results[name] = {}

    for variable, (nbins, xmin, xmax, xlabel) in variables.items():

        h_signal_results[name][variable] = df.Histo1D(
            (
                f"h_signal_{i}_{variable}",
                "",
                nbins,
                float(xmin),
                float(xmax)
            ),
            variable
        )


# ============================================================
# 7. CALCOLO DEGLI ISTOGRAMMI
# ============================================================


print("\nCalcolo degli istogrammi del background...")

# La prima GetValue() avvia l'elaborazione.
# Gli altri istogrammi sono già stati prenotati.

h_bkg = {}

for variable, result in h_bkg_results.items():

    h_bkg[variable] = result.GetValue()

print("Background completato!")


# Calcolo dei quattro segnali.
h_signals = {}

for name, results in h_signal_results.items():

    print("Elaborazione:", name)

    h_signals[name] = {}

    for variable, result in results.items():

        h_signals[name][variable] = result.GetValue()

    print("Completato:", name)





# ============================================================
# 8. CREAZIONE DEL CANVAS
# ============================================================

# Creiamo un'immagine larga 1800 x 600 pixel.
canvas = ROOT.TCanvas(
    "canvas_MET",
    "MET distributions",
    1800,
    600
)

# Dividiamo il canvas in tre pannelli orizzontali.


canvas.Divide(2, 1)

# Manteniamo i riferimenti alle legende.
legends = []


# ============================================================
# 9. DISEGNO DEI TRE ISTOGRAMMI
# ============================================================

for i, (variable, config) in enumerate(variables.items()):

    nbins, xmin, xmax, xlabel = config

    # Selezioniamo il pannello corrente.
    canvas.cd(i + 1)

    pad = ROOT.gPad

    # Scala logaritmica sull'asse Y.
    pad.SetLogy()

    # Margini del pannello.
    pad.SetLeftMargin(0.13)
    pad.SetRightMargin(0.05)
    pad.SetBottomMargin(0.13)
    pad.SetTopMargin(0.08)

    # Recuperiamo l'istogramma del background.
    hb = h_bkg[variable]

    # Recuperiamo i quattro istogrammi dei segnali.
    signal_hists = {
        name: h_signals[name][variable]
        for name in signal_files
    }

    # ========================================================
    # 10. COLORI DELLE DISTRIBUZIONI
    # ========================================================

    hb.SetLineColor(colors["Background"])
    hb.SetLineWidth(2)

    for name, hist in signal_hists.items():

        hist.SetLineColor(colors[name])
        hist.SetLineWidth(2)


    # ========================================================
    # 11. CONFIGURAZIONE DEGLI ASSI
    # ========================================================

    all_hists = [hb] + list(signal_hists.values())

    # Troviamo il massimo tra tutte le distribuzioni.
    ymax = max(
        hist.GetMaximum()
        for hist in all_hists
    )

    # La scala logaritmica richiede un minimo positivo.
    hb.SetMinimum(0.1)

    # Impostiamo un massimo sufficiente a contenere le curve.
    hb.SetMaximum(max(ymax * 10, 1.0))

    # Eliminiamo il titolo automatico.
    hb.SetTitle("")

    # Titolo asse X.
    hb.GetXaxis().SetTitle(xlabel)

    # Larghezza dei bin.
    bin_width = (xmax - xmin) / nbins

    # Titolo asse Y.
    hb.GetYaxis().SetTitle(
        f"Counts"
    )

    # Dimensioni dei titoli.
    hb.GetXaxis().SetTitleSize(0.045)
    hb.GetYaxis().SetTitleSize(0.045)

    # Dimensioni dei numeri sugli assi.
    hb.GetXaxis().SetLabelSize(0.04)
    hb.GetYaxis().SetLabelSize(0.04)

    # Distanza del titolo dell'asse Y.
    hb.GetYaxis().SetTitleOffset(1.35)


    # ========================================================
    # 12. DISEGNO DELLE CINQUE CURVE
    # ========================================================

    # Disegniamo prima il background.
    hb.Draw("HIST")

    # Sovrapponiamo i quattro segnali.
    for name, hist in signal_hists.items():

        hist.Draw("HIST SAME")


    # ========================================================
    # 13. LEGENDA
    # ========================================================

    # Mostriamo la legenda soltanto nel primo pannello.
    if i == 0:

        legend = ROOT.TLegend(
            0.52, 0.67,
            0.94, 0.91
        )

        legend.SetBorderSize(0)
        legend.SetFillStyle(0)
        legend.SetTextSize(0.030)

        legend.AddEntry(
            hb,
            "Scouting",
            "l"
        )

        for name, hist in signal_hists.items():

            legend.AddEntry(
                hist,
                name,
                "l"
            )

        legend.Draw()

        # Manteniamo la legenda in memoria.
        legends.append(legend)

    pad.Modified()
    pad.Update()


# ============================================================
# 14. SALVATAGGIO DELL'IMMAGINE PNG
# ============================================================

canvas.cd()
canvas.Modified()
canvas.Update()

output_png = os.path.join(
    OUTPUT_DIR,
    "MET_comparison.png"
)

canvas.SaveAs(output_png)

print("\nImmagine salvata:", output_png)

canvas.Close()


