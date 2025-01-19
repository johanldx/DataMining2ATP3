import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
from datetime import datetime

class Visualizer:
    def __init__(self, df):
        self.df = df
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.pdf.add_page()
        self.pdf.add_font('NotoSans', '', 'fonts/NotoSans-Medium.ttf', uni=True)
        self.pdf.add_font('NotoSans', 'B', 'fonts/NotoSans-Bold.ttf', uni=True)
        self.pdf.set_font("NotoSans", size=12)
        self.graph_count = 1
        
    def add_main_title(self, title):
        """Ajoute un titre principal centré au début du document."""
        self.pdf.set_font("NotoSans", size=16, style="B")
        self.pdf.set_y(20)
        self.pdf.cell(0, 10, title, ln=True, align="C")
        self.pdf.ln(10)
        return self
    
    def add_paragraph(self, text):
        """Ajoute un paragraphe au PDF."""
        self.pdf.set_font("NotoSans", size=8)
        self.pdf.multi_cell(0, 10, text)
        self.pdf.ln(5)
        return self

    def add_title(self, title):
        """Ajoute un titre pour chaque graphique."""
        self.pdf.set_font("NotoSans", size=14, style="B")
        self.pdf.cell(0, 10, title, ln=True, align="C")
        self.pdf.ln(5)

    def save_plot_to_pdf(self, plt_figure, title):
        """Ajoute une figure matplotlib dans le PDF avec gestion des proportions, du centrage et des sauts de page."""
        if self.pdf.get_y() + 120 > 270:
            self.pdf.add_page()
        self.add_title(title)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            plt_figure.savefig(tmp_file.name, format="PNG", bbox_inches='tight', dpi=300)
            from PIL import Image
            img = Image.open(tmp_file.name)
            img_width, img_height = img.size
            img.close()
            pdf_height = 90
            aspect_ratio = img_width / img_height
            pdf_width = pdf_height * aspect_ratio
            x_position = (self.pdf.w - pdf_width) / 2
            self.pdf.image(tmp_file.name, x=x_position, y=self.pdf.get_y(), w=pdf_width, h=pdf_height)
            tmp_file.close()
        os.remove(tmp_file.name)
        self.pdf.ln(100)

    def graph_available_fuel_distribution(self):
        """Répartition des types de carburants disponibles."""
        print("Création du graphique : Répartition des types de carburants disponibles...")
        if "carburants_disponibles" not in self.df.columns:
            raise Exception("La colonne 'carburants_disponibles' est absente du DataFrame.")
        fuel_counts = (
            self.df["carburants_disponibles"]
            .dropna()
            .explode()
            .value_counts()
        )
        plt.figure(figsize=(8, 6))
        fuel_counts.plot(
            kind="pie", 
            autopct='%1.1f%%', 
            startangle=90, 
            cmap='tab10'
        )
        plt.title("Répartition des types de carburants")
        plt.ylabel("")
        plt.tight_layout()
        self.save_plot_to_pdf(plt.gcf(), "Répartition des types de carburants disponibles")
        plt.close()
        return self
    
    def graph_fuel_prices_by_region(self):
        """Graphique des prix des carburants pour chaque région."""
        print("Création du graphique : Prix des carburants par région...")

        fuel_cols = ["Gazole", "E10", "SP98", "SP95", "GPLc", "E85"]
        if "code_region" not in self.df.columns or "region" not in self.df.columns:
            raise Exception("Les colonnes nécessaires ('code_region', 'region') sont absentes du DataFrame.")
        if not all(col in self.df.columns for col in fuel_cols):
            raise Exception("Les colonnes de carburants sont absentes du DataFrame.")

        self.df[fuel_cols] = self.df[fuel_cols].replace(0, pd.NA).dropna(how='all', subset=fuel_cols)

        median_prices = self.df.groupby("region")[fuel_cols].median()

        median_prices = median_prices.sort_index()

        median_prices.plot(
            kind="bar", 
            figsize=(12, 8),
            width=0.8,
            colormap="tab20"
        )
        plt.title("Prix médians des carburants par région")
        plt.ylabel("Prix (€)")
        plt.xlabel("Régions")
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Carburants", bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()
        self.save_plot_to_pdf(plt.gcf(), "Prix médians des carburants par région")
        plt.close()
        return self

    def graph_fuel_popularity(self):
        """Graphique : Nombre de stations offrant chaque carburant."""
        print("Création du graphique : Nombre de stations offrant chaque carburant...")
        fuel_cols = ["Gazole", "SP95", "SP98", "E10", "GPLc", "E85"]
        fuel_availability = self.df[fuel_cols].notna().sum()
        fuel_availability.plot(kind="bar", figsize=(10, 6), color="skyblue", edgecolor="black")
        plt.title("Nombre de stations offrant chaque carburant")
        plt.ylabel("Nombre de stations")
        plt.xlabel("Carburants")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self.save_plot_to_pdf(plt.gcf(), "Nombre de stations offrant chaque carburant")
        plt.close()
        return self

    def graph_fuel_price_boxplot(self):
        """Graphique : Comparaison des prix par type de carburant (Boxplots)."""
        print("Création du graphique : Comparaison des prix par type de carburant (Boxplots)...")
        fuel_cols = ["Gazole", "SP95", "SP98", "E10", "GPLc", "E85"]
        df_cleaned = self.df[fuel_cols].dropna(how="all")
        df_cleaned = df_cleaned.apply(lambda x: pd.to_numeric(x, errors='coerce')).dropna(how='all')
        df_cleaned.boxplot(figsize=(10, 6))
        plt.title("Distribution des prix par type de carburant")
        plt.ylabel("Prix (€)")
        plt.xlabel("Carburants")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self.save_plot_to_pdf(plt.gcf(), "Distribution des prix par type de carburant")
        plt.close()
        return self

    def graph_top_departments_highest_price(self, fuel_type):
        """Graphique : Top départements par prix le plus élevé pour un carburant spécifique."""
        print(f"Création du graphique : Top départements par prix le plus élevé pour le carburant {fuel_type}...")
        if fuel_type not in self.df.columns or "code_departement" not in self.df.columns:
            raise Exception(f"Les colonnes nécessaires ('{fuel_type}', 'code_departement') sont absentes.")
        
        top_departments = (
            self.df.groupby("code_departement")[fuel_type]
            .max()
            .sort_values(ascending=False)
            .head(10)
        )
        top_departments.plot(kind="barh", figsize=(10, 6), color="coral", edgecolor="black")
        plt.title(f"Top départements par prix le plus élevé ({fuel_type})")
        plt.xlabel("Prix (€)")
        plt.ylabel("Départements")
        plt.tight_layout()
        self.save_plot_to_pdf(plt.gcf(), f"Top départements par prix élevé ({fuel_type})")
        plt.close()
        return self

    def graph_fossil_vs_alternative_fuel_prices(self):
        """Graphique : Comparaison des prix médians entre carburants fossiles et alternatifs."""
        print("Création du graphique : Comparaison des prix médians entre carburants fossiles et alternatifs...")
        fuels = ["Gazole", "SP95", "SP98", "GPLc", "E85"]
        
        df_cleaned = self.df[fuels].replace(0, pd.NA).dropna(how='all', subset=fuels)
        median_prices = df_cleaned.median()

        median_prices.plot(kind="bar", figsize=(10, 6), color="skyblue", edgecolor="black")
        plt.title("Comparaison des prix médians entre carburants fossiles et alternatifs")
        plt.ylabel("Prix médian (€)")
        plt.xlabel("Carburants")
        plt.xticks(rotation=45)
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Comparaison des prix médians entre carburants fossiles et alternatifs")
        plt.close()
        return self
    
    def graph_service_distribution(self):
        """Graphique : Répartition des services disponibles."""
        print("Création du graphique : Répartition des services disponibles...")

        if "services_service" not in self.df.columns:
            raise Exception("La colonne 'services_service' est absente du DataFrame.")
        
        services_counts = (
            self.df["services_service"]
            .dropna()
            .explode()
            .value_counts()
        )

        plt.figure(figsize=(10, 8))
        services_counts.plot(kind="bar", color="skyblue", edgecolor="black")
        plt.title("Répartition des services disponibles")
        plt.ylabel("Nombre de stations")
        plt.xlabel("Services")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Répartition des services disponibles")
        plt.close()
        return self
    
    def graph_automate_24_24_distribution(self):
        """Graphique : Disponibilité des automates 24/24."""
        print("Création du graphique : Disponibilité des automates 24/24...")

        if "horaires_automate_24_24" not in self.df.columns:
            raise Exception("La colonne 'horaires_automate_24_24' est absente du DataFrame.")
        
        automate_counts = self.df["horaires_automate_24_24"].value_counts()

        plt.figure(figsize=(6, 6))
        automate_counts.plot(
            kind="pie", 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=["lightgreen", "lightcoral"], 
            labels=["Oui", "Non"]
        )
        plt.title("Disponibilité des automates 24/24")
        plt.ylabel("")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Disponibilité des automates 24/24")
        plt.close()
        return self

    def graph_average_fuel_outage_duration(self):
        """Graphique : Durée moyenne des ruptures temporaires de carburants."""
        print("Création du graphique : Durée moyenne des ruptures temporaires de carburants...")

        fuels = ["Gazole", "E10", "SP98", "SP95", "GPLc", "E85"]
        durations = {}

        for fuel in fuels:
            start_col = f"{fuel.lower()}_rupture_debut"
            type_col = f"{fuel.lower()}_rupture_type"

            if start_col not in self.df.columns or type_col not in self.df.columns:
                print(f"Colonnes manquantes pour le carburant {fuel}: {start_col} ou {type_col}. Ignoré.")
                continue

            self.df[start_col] = pd.to_datetime(self.df[start_col], errors="coerce")
            self.df[start_col] = self.df[start_col].dt.tz_localize(None)

            temp_outages = self.df[self.df[type_col] == "temporaire"].copy()

            temp_outages.loc[:, f"{fuel}_rupture_duree"] = (
                datetime.now() - temp_outages[start_col]
            ).dt.days

            active_durations = temp_outages[f"{fuel}_rupture_duree"].dropna()
            if len(active_durations) > 0:
                durations[fuel] = active_durations.mean()
            else:
                durations[fuel] = 0

        if not durations:
            raise Exception("Aucune donnée de rupture temporaire disponible pour les carburants.")

        durations_df = pd.DataFrame(
            list(durations.items()), columns=["Carburant", "Durée moyenne (jours)"]
        ).sort_values(by="Durée moyenne (jours)", ascending=False)

        plt.figure(figsize=(10, 6))
        plt.bar(
            durations_df["Carburant"],
            durations_df["Durée moyenne (jours)"],
            color="salmon",
            edgecolor="black"
        )
        plt.title("Durée moyenne des ruptures temporaires de carburants")
        plt.ylabel("Durée moyenne (jours)")
        plt.xlabel("Carburants")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Durée moyenne des ruptures temporaires de carburants")
        plt.close()
        return self
    
    def graph_fuel_availability_by_day(self):
        """Graphique : Disponibilité des carburants par jour de la semaine."""
        print("Création du graphique : Disponibilité des carburants par jour de la semaine...")

        rupture_cols = [col for col in self.df.columns if "rupture_debut" in col]
        if not rupture_cols:
            raise Exception("Aucune colonne de rupture trouvée dans le DataFrame.")

        days_of_week = []
        for col in rupture_cols:
            days_of_week.extend(
                pd.to_datetime(self.df[col], errors="coerce").dropna().dt.day_name()
            )

        day_counts = pd.Series(days_of_week).value_counts().reindex(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )

        day_counts.plot(kind="bar", figsize=(10, 6), color="skyblue", edgecolor="black")
        plt.title("Disponibilité des carburants par jour de la semaine")
        plt.ylabel("Nombre d'indisponibilités")
        plt.xlabel("Jour de la semaine")
        plt.xticks(rotation=45)
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Disponibilité des carburants par jour de la semaine")
        plt.close()
        return self
    
    def graph_station_distribution_by_population_density(self):
        """Graphique : Répartition des stations par densité de population."""
        print("Création du graphique : Répartition des stations par densité de population...")

        if "pop" not in self.df.columns:
            raise Exception("La colonne 'pop' (rurale ou urbaine) est absente du DataFrame.")

        density_counts = self.df["pop"].value_counts()

        plt.figure(figsize=(8, 6))
        density_counts.plot(
            kind="pie",
            autopct='%1.1f%%',
            startangle=90,
            colors=["#ff9999", "#66b3ff"],
            labels=["Rural (R)", "Urbain (U)"]
        )
        plt.title("Répartition des stations par densité de population")
        plt.ylabel("")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Répartition des stations par densité de population")
        plt.close()
        return self

    def graph_services_per_station(self):
        """Graphique : Nombre de services disponibles par station."""
        print("Création du graphique : Nombre de services disponibles par station...")

        if "services" not in self.df.columns:
            raise Exception("La colonne 'services' est absente du DataFrame.")

        self.df["num_services"] = self.df["services"].apply(lambda x: len(x.split(", ")) if pd.notna(x) else 0)

        bins = [0, 1, 5, 10, 15, 20, 25, 30]
        self.df["num_services"].plot(
            kind="hist", bins=bins, figsize=(10, 6), color="purple", edgecolor="black"
        )
        plt.title("Nombre de services disponibles par station")
        plt.ylabel("Nombre de stations")
        plt.xlabel("Nombre de services")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Nombre de services disponibles par station")
        plt.close()
        return self
    
    def graph_station_distance_distribution(self):
        """Graphique : Distribution des distances entre stations en kilomètres."""
        print("Création du graphique : Distribution des distances entre stations...")

        if "latitude" not in self.df.columns or "longitude" not in self.df.columns:
            raise Exception("Les colonnes 'latitude' et 'longitude' sont absentes du DataFrame.")

        coords = self.df[["latitude", "longitude"]].dropna().to_numpy()

        distances_km = [
            geodesic(coords[i], coords[j]).km
            for i in range(len(coords))
            for j in range(i + 1, len(coords))
        ]

        plt.figure(figsize=(10, 6))
        plt.hist(distances_km, bins=30, color="green", edgecolor="black")
        plt.title("Distribution des distances entre stations")
        plt.ylabel("Fréquence")
        plt.xlabel("Distance (km)")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Distribution des distances entre stations (en km)")
        plt.close()
        return self
    
    def graph_median_prices_by_city_92(self):
        """Graphique : Prix médian des carburants par ville dans le département 92 (Hauts-de-Seine)."""
        print("Création du graphique : Prix médian des carburants par ville (Département 92)...")

        df_92 = self.df[self.df["code_departement"] == "92"].copy()

        if df_92.empty:
            raise Exception("Aucune donnée trouvée pour le département 92.")

        fuel_cols = ["Gazole", "E10", "SP98", "SP95", "GPLc", "E85"]
        df_92[fuel_cols] = df_92[fuel_cols].replace(0, pd.NA).dropna(how='all', subset=fuel_cols)

        median_prices = df_92.groupby("ville")[fuel_cols].median()

        median_prices.plot(kind="bar", figsize=(12, 8), colormap="tab10")
        plt.title("Prix médian des carburants par ville (Département 92)")
        plt.ylabel("Prix médian (€)")
        plt.xlabel("Villes")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Prix médian des carburants par ville (Département 92)")
        plt.close()
        return self

    def graph_cheapest_vs_expensive_station(self):
        """Graphique : Comparaison des stations les moins chères et les plus chères."""
        print("Création du graphique : Comparaison des stations les moins chères et les plus chères...")

        fuel_cols = ["Gazole", "E10", "SP98", "SP95", "GPLc", "E85"]
        self.df["prix_median"] = self.df[fuel_cols].apply(pd.to_numeric, errors='coerce').median(axis=1, skipna=True)

        valid_stations = self.df.dropna(subset=["prix_median"])

        cheapest_station = valid_stations.loc[valid_stations["prix_median"].idxmin()]
        most_expensive_station = valid_stations.loc[valid_stations["prix_median"].idxmax()]

        comparison = pd.DataFrame({
            "Station": ["Moins chère", "Plus chère"],
            "Prix médian (€)": [cheapest_station["prix_median"], most_expensive_station["prix_median"]]
        })

        comparison.plot(kind="bar", x="Station", y="Prix médian (€)", color=["green", "red"], legend=False)
        plt.title("Comparaison des prix médians (Moins chère vs Plus chère)")
        plt.ylabel("Prix médian (€)")
        plt.xlabel("Station")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Comparaison des prix médians (Moins chère vs Plus chère)")
        plt.close()
        return self
    
    def graph_avg_prices_highway_vs_others(self):
        """Graphique : Comparaison des prix médians entre stations sur autoroutes et autres."""
        print("Création du graphique : Prix médians (Autoroutes vs Autres)...")

        highway_stations = self.df[self.df["adresse"].str.contains("autoroute", case=False, na=False)]
        other_stations = self.df[~self.df["adresse"].str.contains("autoroute", case=False, na=False)]

        highway_median = highway_stations[["Gazole", "E10", "SP98", "SP95", "GPLc", "E85"]].median().median()
        others_median = other_stations[["Gazole", "E10", "SP98", "SP95", "GPLc", "E85"]].median().median()

        comparison = pd.DataFrame({"Type": ["Autoroute", "Autres"], "Prix médian (€)": [highway_median, others_median]})

        comparison.plot(kind="bar", x="Type", y="Prix médian (€)", color=["orange", "gray"], legend=False)
        plt.title("Prix médians : Autoroutes vs Autres")
        plt.ylabel("Prix médian (€)")
        plt.xlabel("Type de station")
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Prix médians : Autoroutes vs Autres")
        plt.close()
        return self

    def graph_avg_price_full_tank_sp98(self):
        """Graphique : Prix moyen d'un plein de 50L de SP98 par région."""
        print("Création du graphique : Prix moyen d'un plein de 50L de SP98 par région...")

        if "SP98" not in self.df.columns or "region" not in self.df.columns:
            raise Exception("Les colonnes 'SP98' et 'region' sont nécessaires.")

        avg_full_tank = self.df.groupby("region")["SP98"].mean() * 50

        avg_full_tank.sort_values(ascending=False).plot(kind="bar", figsize=(12, 8), color="purple", edgecolor="black")
        plt.title("Prix moyen d'un plein de 50L de SP98 par région")
        plt.ylabel("Prix moyen (€)")
        plt.xlabel("Régions")
        plt.xticks(rotation=45)
        plt.tight_layout()

        self.save_plot_to_pdf(plt.gcf(), "Prix moyen d'un plein de 50L de SP98 par région")
        plt.close()
        return self


    def export(self, filename="visualizations.pdf"):
        """Exporte tous les graphiques dans un fichier PDF."""
        self.pdf.output(filename)
        print(f"Rapport exporté dans le fichier : {filename}")

if __name__ == '__main__':
    df = pd.read_json("TP3/data/clear_dataset.json")
    visualizer = Visualizer(df)
    visualizer.add_main_title("TP3 - Johan Ledoux")
    visualizer.add_paragraph("Paragaphe d'exemple")
    visualizer.graph_avg_prices_by_city_92() \
              .graph_cheapest_vs_expensive_station() \
              .graph_avg_prices_highway_vs_others() \
              .graph_avg_price_full_tank_sp98() \
              .export("rapport_visualisations.pdf")
