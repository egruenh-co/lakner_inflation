#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse der Bio-Umsatzdaten und Berechnung der impliziten Inflationsrate
bezogen auf das Basisjahr 2020.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_data():
    """Lädt die CSV-Dateien mit den Umsatzdaten."""
    # Nominal-Umsätze laden
    df_nominal = pd.read_csv('bio_umsatz_nominal.csv', sep=';', skipinitialspace=True)
    df_nominal.columns = df_nominal.columns.str.strip()  # Leerzeichen entfernen
    
    # Real-Umsätze laden
    df_real = pd.read_csv('bio_umsatz_real.csv', sep=';', skipinitialspace=True)
    df_real.columns = df_real.columns.str.strip()  # Leerzeichen entfernen
    
    # Daten zusammenführen
    df = pd.merge(df_nominal, df_real, on='jahr')
    
    return df

def load_destatis_inflation():
    """Lädt die Destatis-Inflationsdaten für Lebensmittel."""
    df_destatis = pd.read_csv('destatis_inflation_lebensmittel.csv', sep=';', skipinitialspace=True)
    df_destatis.columns = df_destatis.columns.str.strip()
    return df_destatis

def calculate_real_umsatz_with_destatis(df_nominal, df_destatis, base_year=2020):
    """
    Berechnet Realumsätze basierend auf Destatis-Inflationsraten.
    """
    # Basis-Nominalumsatz für 2020
    base_nominal = df_nominal[df_nominal['jahr'] == base_year]['umsatz_nominal'].iloc[0]
    
    # DataFrame für Ergebnisse
    result_df = df_nominal.copy()
    result_df['umsatz_real_destatis'] = result_df['umsatz_nominal']
    result_df['preisindex_destatis'] = 1.0
    result_df['inflation_kumulativ_destatis'] = 0.0
    
    # 2020 als Basis
    result_df.loc[result_df['jahr'] == base_year, 'umsatz_real_destatis'] = base_nominal
    
    # Für Jahre nach 2020: Realumsatz mit Destatis-Inflationsraten berechnen
    preisindex = 1.0
    for _, row in df_destatis.iterrows():
        jahr = row['jahr']
        inflation_rate = row['inflation_rate_jahr']
        
        # Preisindex kumulativ berechnen
        preisindex *= (1 + inflation_rate)
        
        # Realumsatz berechnen: Nominal / Preisindex
        nominal_umsatz = df_nominal[df_nominal['jahr'] == jahr]['umsatz_nominal'].iloc[0]
        real_umsatz = nominal_umsatz / preisindex
        
        # In Ergebnis-DataFrame eintragen
        mask = result_df['jahr'] == jahr
        result_df.loc[mask, 'umsatz_real_destatis'] = real_umsatz
        result_df.loc[mask, 'preisindex_destatis'] = preisindex
        result_df.loc[mask, 'inflation_kumulativ_destatis'] = (preisindex - 1) * 100
    
    return result_df

def calculate_inflation_rates(df, base_year=2020):
    """
    Berechnet die implizite Inflationsrate basierend auf dem Verhältnis
    von Nominal- zu Realumsatz, bezogen auf ein Basisjahr.
    
    Die Formel ist:
    Preisindex_t = (Nominal_t / Real_t) / (Nominal_base / Real_base)
    Inflationsrate_t = (Preisindex_t - 1) * 100
    """
    # Basiswerte für 2020
    base_row = df[df['jahr'] == base_year].iloc[0]
    base_ratio = base_row['umsatz_nominal'] / base_row['umsatz_real']
    
    # Preisindex für jedes Jahr berechnen
    df['preis_ratio'] = df['umsatz_nominal'] / df['umsatz_real']
    df['preisindex'] = df['preis_ratio'] / base_ratio
    
    # Inflationsrate berechnen (bezogen auf Basisjahr)
    df['inflation_kumulativ'] = (df['preisindex'] - 1) * 100
    
    # Jährliche Inflationsrate berechnen
    df['inflation_jaehrlich'] = df['preisindex'].pct_change() * 100
    
    return df

def print_results(df):
    """Gibt die Ergebnisse formatiert aus."""
    print("=" * 70)
    print(" Bio-Umsatz Analyse: Implizite Inflationsraten bezogen auf 2020")
    print("=" * 70)
    print()
    
    print("Rohdaten:")
    print("-" * 50)
    for _, row in df.iterrows():
        print(f"{int(row['jahr'])}: Nominal {row['umsatz_nominal']:6.2f} Mrd €, "
              f"Real {row['umsatz_real']:6.2f} Mrd €")
    print()
    
    print("Berechnete Inflationsraten:")
    print("-" * 50)
    print(f"{'Jahr':<6} {'Preisindex':<12} {'Kumulativ':<12} {'Jährlich':<12}")
    print(f"{'':^6} {'(Basis=1.0)':<12} {'(%)':<12} {'(%)':<12}")
    print("-" * 50)
    
    for _, row in df.iterrows():
        jahr = int(row['jahr'])
        preisindex = row['preisindex']
        kumulativ = row['inflation_kumulativ']
        jaehrlich = row['inflation_jaehrlich']
        
        if np.isnan(jaehrlich):
            jaehrlich_str = "Basis"
        else:
            jaehrlich_str = f"{jaehrlich:+6.2f}"
        
        print(f"{jahr:<6} {preisindex:8.4f}    {kumulativ:+7.2f}      {jaehrlich_str}")
    
    print()
    print("Erläuterung:")
    print("- Preisindex: Verhältnis der Preise zum Basisjahr 2020")
    print("- Kumulativ: Gesamte Preissteigerung seit 2020 in %")
    print("- Jährlich: Preissteigerung gegenüber dem Vorjahr in %")

def create_visualization(df):
    """Erstellt Visualisierungen der Daten."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Nominal vs Real Umsatz
    ax1.plot(df['jahr'], df['umsatz_nominal'], 'b-o', label='Nominal', linewidth=2)
    ax1.plot(df['jahr'], df['umsatz_real'], 'r-s', label='Real (Basis: 2020)', linewidth=2)
    ax1.set_title('Bio-Umsatz nach Lakner: Nominal vs. Real')
    ax1.set_xlabel('Jahr')
    ax1.set_ylabel('Umsatz (Mrd €)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Preisindex
    ax2.plot(df['jahr'], df['preisindex'], 'g-o', linewidth=2, markersize=8)
    ax2.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Basisjahr 2020')
    ax2.set_title('Preisindex (Basis: 2020 = 1.0)')
    ax2.set_xlabel('Jahr')
    ax2.set_ylabel('Preisindex')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Kumulative Inflation
    ax3.bar(df['jahr'], df['inflation_kumulativ'], color='orange', alpha=0.7)
    ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax3.set_title('Kumulative Inflation seit 2020')
    ax3.set_xlabel('Jahr')
    ax3.set_ylabel('Inflation (%)')
    ax3.grid(True, alpha=0.3)
    
    # 4. Jährliche Inflation
    jahre_ohne_basis = df[df['jahr'] != 2020]['jahr']
    inflation_ohne_basis = df[df['jahr'] != 2020]['inflation_jaehrlich']
    ax4.bar(jahre_ohne_basis, inflation_ohne_basis, color='red', alpha=0.7)
    ax4.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax4.set_title('Jährliche Inflationsrate')
    ax4.set_xlabel('Jahr')
    ax4.set_ylabel('Inflation (%)')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bio_inflation_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_destatis_comparison(df_combined, df_destatis):
    """Erstellt Vergleichsgrafik mit Destatis-Inflationsraten."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Vergleich der Realumsätze
    ax1.plot(df_combined['jahr'], df_combined['umsatz_nominal'], 'b-o', 
             label='Nominal', linewidth=2, markersize=6)
    ax1.plot(df_combined['jahr'], df_combined['umsatz_real'], 'r-s', 
             label='Real (Lakner)', linewidth=2, markersize=6)
    ax1.plot(df_combined['jahr'], df_combined['umsatz_real_destatis'], 'g-^', 
             label='Real (Destatis)', linewidth=2, markersize=6)
    ax1.set_title('Vergleich: Nominal- und Realumsätze')
    ax1.set_xlabel('Jahr')
    ax1.set_ylabel('Umsatz (Mrd €)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Vergleich der Preisindizes
    ax2.plot(df_combined['jahr'], df_combined['preisindex'], 'r-s', 
             label='Preisindex (Lakner)', linewidth=2, markersize=6)
    ax2.plot(df_combined['jahr'], df_combined['preisindex_destatis'], 'g-^', 
             label='Preisindex (Destatis)', linewidth=2, markersize=6)
    ax2.axhline(y=1.0, color='k', linestyle='--', alpha=0.5, label='Basisjahr 2020')
    ax2.set_title('Vergleich der Preisindizes (Basis: 2020 = 1.0)')
    ax2.set_xlabel('Jahr')
    ax2.set_ylabel('Preisindex')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Jährliche Inflationsraten aus Destatis-Daten
    ax3.bar(df_destatis['jahr'], df_destatis['inflation_rate_jahr'] * 100, 
            color='green', alpha=0.7, label='Destatis Jahresraten')
    ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax3.set_title('Destatis: Jährliche Inflationsraten Lebensmittel')
    ax3.set_xlabel('Jahr')
    ax3.set_ylabel('Inflation (%)')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Kumulative Inflation im Vergleich
    ax4.bar(df_combined['jahr'], df_combined['inflation_kumulativ'], 
            color='red', alpha=0.7, width=0.4, label='Lakner (implizit)')
    ax4.bar(df_combined['jahr'] + 0.4, df_combined['inflation_kumulativ_destatis'], 
            color='green', alpha=0.7, width=0.4, label='Destatis')
    ax4.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax4.set_title('Vergleich: Kumulative Inflation seit 2020')
    ax4.set_xlabel('Jahr')
    ax4.set_ylabel('Inflation (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bio_destatis_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

def print_destatis_comparison(df_combined, df_destatis):
    """Gibt den Vergleich mit Destatis-Daten aus."""
    print("\n" + "=" * 80)
    print(" Vergleich: Lakner vs. Destatis Inflationsraten")
    print("=" * 80)
    print()
    
    print("Destatis Lebensmittel-Inflationsraten (jährlich):")
    print("-" * 50)
    for _, row in df_destatis.iterrows():
        print(f"{int(row['jahr'])}: {row['inflation_rate_jahr']*100:+6.1f}%")
    
    print("\nVergleich der berechneten Realumsätze:")
    print("-" * 70)
    print(f"{'Jahr':<6} {'Nominal':<10} {'Real (Lakner)':<15} {'Real (Destatis)':<15} {'Differenz':<10}")
    print("-" * 70)
    
    for _, row in df_combined.iterrows():
        jahr = int(row['jahr'])
        nominal = row['umsatz_nominal']
        real_lakner = row['umsatz_real']
        real_destatis = row['umsatz_real_destatis']
        differenz = real_destatis - real_lakner
        
        print(f"{jahr:<6} {nominal:8.2f}   {real_lakner:10.2f}      {real_destatis:10.2f}       {differenz:+7.2f}")
    
    print("\nVergleich der kumulativen Inflation seit 2020:")
    print("-" * 60)
    print(f"{'Jahr':<6} {'Lakner (%)':<12} {'Destatis (%)':<12} {'Differenz':<10}")
    print("-" * 60)
    
    for _, row in df_combined.iterrows():
        jahr = int(row['jahr'])
        lakner_kumul = row['inflation_kumulativ']
        destatis_kumul = row['inflation_kumulativ_destatis']
        diff_kumul = destatis_kumul - lakner_kumul
        
        print(f"{jahr:<6} {lakner_kumul:8.2f}     {destatis_kumul:8.2f}       {diff_kumul:+7.2f}")

def main():
    """Hauptfunktion."""
    try:
        # Ursprüngliche Daten laden und analysieren
        df = load_data()
        df = calculate_inflation_rates(df, base_year=2020)
        print_results(df)
        create_visualization(df)
        
        # Destatis-Daten laden
        df_destatis = load_destatis_inflation()
        
        # Nominal-Umsätze mit Destatis-Inflationsraten verarbeiten
        df_nominal = df[['jahr', 'umsatz_nominal']].copy()
        df_combined = calculate_real_umsatz_with_destatis(df_nominal, df_destatis)
        
        # Lakner-Daten zu Combined-DataFrame hinzufügen
        df_combined = pd.merge(df_combined, df[['jahr', 'umsatz_real', 'preisindex', 'inflation_kumulativ']], 
                              on='jahr', how='left')
        
        # Vergleichsanalyse ausgeben
        print_destatis_comparison(df_combined, df_destatis)
        
        # Neue Vergleichsgrafik erstellen
        create_destatis_comparison(df_combined, df_destatis)
        
        # Zusätzliche Analyse
        print("\nZusätzliche Erkenntnisse:")
        print("-" * 30)
        
        inflation_2025_lakner = df[df['jahr'] == 2025]['inflation_kumulativ'].iloc[0]
        inflation_2025_destatis = df_combined[df_combined['jahr'] == 2025]['inflation_kumulativ_destatis'].iloc[0]
        print(f"• Gesamte Inflation 2020-2025 (Lakner): {inflation_2025_lakner:+.2f}%")
        print(f"• Gesamte Inflation 2020-2025 (Destatis): {inflation_2025_destatis:+.2f}%")
        print(f"• Differenz: {inflation_2025_destatis - inflation_2025_lakner:+.2f} Prozentpunkte")
        
        avg_destatis = df_destatis['inflation_rate_jahr'].mean() * 100
        print(f"• Durchschnittliche jährliche Inflation (Destatis): {avg_destatis:+.2f}%")
        
        # Ergebnisse speichern
        df.to_csv('bio_inflation_results.csv', index=False, sep=';')
        df_combined.to_csv('bio_destatis_comparison.csv', index=False, sep=';')
        
        print(f"\n✓ Lakner-Analyse gespeichert in 'bio_inflation_results.csv'")
        print(f"✓ Vergleichsanalyse gespeichert in 'bio_destatis_comparison.csv'")
        print(f"✓ Lakner-Diagramm gespeichert als 'bio_inflation_analysis.png'")
        print(f"✓ Vergleichsdiagramm gespeichert als 'bio_destatis_comparison.png'")
        
    except FileNotFoundError as e:
        print(f"Fehler: Datei nicht gefunden - {e}")
        print("Stellen Sie sicher, dass alle CSV-Dateien im aktuellen Verzeichnis sind.")
    except Exception as e:
        print(f"Fehler bei der Analyse: {e}")

if __name__ == "__main__":
    main()