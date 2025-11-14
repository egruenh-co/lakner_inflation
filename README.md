# Lakner Inflation Analysis

Analyse der Bio-Umsatzdaten und Berechnung der impliziten Inflationsrate bezogen auf das Basisjahr 2020.

## Beschreibung

Dieses Python-Programm analysiert Bio-Umsatzdaten und berechnet implizite Inflationsraten durch den Vergleich von Nominal- und Realumsätzen. Zusätzlich werden die Ergebnisse mit offiziellen Destatis-Inflationsraten für Lebensmittel verglichen.

## Features

- Berechnung impliziter Inflationsraten aus Lakner-Daten
- Vergleich mit Destatis-Lebensmittelinflation
- Visualisierung der Ergebnisse
- Export der Analyseergebnisse als CSV

## Installation

```bash
pip install pandas numpy matplotlib
```

## Verwendung

```bash
python inflation_analysis.py
```

## Ausgabedateien

- `bio_inflation_results.csv` - Lakner-Analyseergebnisse
- `bio_destatis_comparison.csv` - Vergleichsanalyse
- `bio_inflation_analysis.png` - Lakner-Diagramme
- `bio_destatis_comparison.png` - Vergleichsdiagramme

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) Datei für Details.

## Autor

Eckart Grünhagen