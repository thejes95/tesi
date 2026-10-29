import ROOT
import multiprocessing as mp
import os
from glob import glob

#definisco i path delle CARTELLE
input_dir = "/mnt/bidone/data_jessica"
output_dir= "/mnt/bidone/data_jessica_filtered_v2"




#definisco una funzione che faccia i tagli richiesti
def reduce_file(input_file):

    #costruzione nome output aggiungendo _reduced.root

    output_file = os.path.join(output_dir,os.path.basename(input_file.replace(".root","_reduced.root")))
  
    print(f"\nProcessing: {input_file}")

    df=ROOT.RDataFrame("Events",input_file)

    print("numero eventi", df.Count().GetValue())

    condition1=("Any(ScoutingElectron_pt>23) || " 
            "Any(ScoutingMuon_pt > 23)")

    df_cut=(df
        .Filter(condition1)
    
         #Filtro sui Jet
        .Define("jetmask", "(ScoutingPFJetRecluster_pt>15) && (abs(ScoutingPFJetRecluster_eta)<2.4)")
        .Define("Jet_pt_ok", "ScoutingPFJetRecluster_pt[jetmask]")
        .Define("Jet_eta_ok", "ScoutingPFJetRecluster_eta[jetmask]")
        .Define("Jet_phi_ok","ScoutingPFJetRecluster_phi[jetmask]")
        .Define("idxjet", "Reverse(Argsort(Jet_pt_ok))")
        .Define("Jet_pt_sorted", "Take(Jet_pt_ok, idxjet)")
        .Define("Jet_eta_sorted", "Take(Jet_eta_ok, idxjet)")
        .Define("Jet_phi_sorted", "Take(Jet_phi_ok, idxjet)")
        .Define("Jet_pt", "Jet_pt_sorted.size()>=10? Take(Jet_pt_sorted, 10) : Jet_pt_sorted")
        .Define("Jet_eta", "Jet_eta_sorted.size()>=10? Take(Jet_eta_sorted, 10) : Jet_eta_sorted")
        .Define("Jet_phi", "Jet_phi_sorted.size()>=10? Take(Jet_phi_sorted, 10) : Jet_phi_sorted")

         #Filtro sui muoni
        .Define("muonmask", "(ScoutingMuon_pt>3) && (abs(ScoutingMuon_eta)<2.4)")
        .Define("Muon_pt_ok", "ScoutingMuon_pt[muonmask]")
        .Define("Muon_eta_ok","ScoutingMuon_eta[muonmask]")
        .Define("Muon_phi_ok", "ScoutingMuon_phi[muonmask]")
        .Define("idxmuon","Reverse(Argsort(Muon_pt_ok))")
        .Define("Muon_pt_sorted","Take(Muon_pt_ok,idxmuon)")
        .Define("Muon_eta_sorted", "Take(Muon_eta_ok, idxmuon)")
        .Define("Muon_phi_sorted","Take(Muon_phi_ok, idxmuon)")
        .Define("Muon_pt", "Muon_pt_sorted.size()>=4? Take(Muon_pt_sorted,4) : Muon_pt_sorted")
        .Define("Muon_eta", "Muon_eta_sorted.size()>=4? Take(Muon_eta_sorted,4) : Muon_eta_sorted")
        .Define("Muon_phi", "Muon_phi_sorted.size()>=4? Take(Muon_phi_sorted, 4) : Muon_phi_sorted")

        #filtro su elettroni
        .Define("elemask","(ScoutingElectron_pt>3) && (abs(ScoutingElectron_eta)<2.4)")
        .Define("Ele_pt_ok","ScoutingElectron_pt[elemask]")
        .Define("Ele_eta_ok", "ScoutingElectron_eta[elemask]")
        .Define("Ele_phi_ok", "ScoutingElectron_phi[elemask]")
        .Define("idxele","Reverse(Argsort(Ele_pt_ok))")
        .Define("Ele_pt_sorted", "Take(Ele_pt_ok, idxele)")
        .Define("Ele_eta_sorted", "Take(Ele_eta_ok, idxele)")
        .Define("Ele_phi_sorted", "Take(Ele_phi_ok, idxele)")
        .Define("Ele_pt", "Ele_pt_sorted.size()>=4? Take(Ele_pt_sorted,4) : Ele_pt_sorted")
        .Define("Ele_eta", "Ele_eta_sorted.size()>=4? Take(Ele_eta_sorted,4) : Ele_eta_sorted")
        .Define("Ele_phi","Ele_phi_sorted.size()>=4? Take(Ele_phi_sorted,4) : Ele_phi_sorted")
            )

    #salvo le nuove colonne create e filtrate su un altro file root
    
    cols=ROOT.std.vector("string")()

    for c in [
            "Jet_pt",
            "Jet_eta",
            "Jet_phi",
            "Muon_pt",
            "Muon_eta",
            "Muon_phi",
            "Ele_pt",
            "Ele_eta",
            "Ele_phi",
            "ScoutingMET_pt",
            "ScoutingMET_phi",
            "event"]:
        cols.push_back(c)

    df_cut.Snapshot("Events",output_file, cols)

    n_before=df.Count().GetValue()
    n_after=df_cut.Count().GetValue()

    return input_file, output_file, n_before, n_after


#lavoro in multiprocessing utilizzando quella funzione sui file che voglio filtrare e printo alcune cose

if __name__ == "__main__":

    files = glob(os.path.join(input_dir, "*root"))
    
        
    n_processes=12

    with mp.Pool(processes=n_processes) as pool:
        results = pool.map(reduce_file, files)


    print("\n==== SUMMARY =====")

    total_before=0
    total_after=0

    for input_file, output_file, n_before, n_after in results:

        reduction = 100 * (1- n_after / n_before)
                    
                    

        print(f"\nInput : {input_file}")


        print(f"Events before cut: {n_before}")
        print(f"Events after cut: {n_after}")
        print(f"Reduction : {reduction:.2f}%")
   
        total_before += n_before
        total_after += n_after


   #totale di tutto il dataset

    if total_before>0:
        tot_reduction=(100*(1-total_after /total_before))
       
    print("=========TOTALE DATASET============")
    print(f"Eventi iniziali: {total_before}")
    print(f"Eventi finali: {total_after}")
    print(f"Eventi rimossi:" f"{total_before -total_after}")
    print(f"Riduzione totale:" f"{tot_reduction:.2f}%")


