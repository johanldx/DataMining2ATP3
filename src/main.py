from api_client import APIClient
from data_processor import DataProcessor
from visualizer import Visualizer

if __name__ == '__main__':
    api = APIClient()
    api.get_dataset("prix-des-carburants-en-france-flux-instantane-v2@opendatamef")
    
    processor = DataProcessor()
    processor.load(api.data) \
        .clean_missing_and_outliers() \
        .prepare_data() \
        .summarize_data() \
        .save()
        
    visualizer = Visualizer(processor.df)
    visualizer.add_main_title("TP3 - Prix des carburants (Johan Ledoux)")
    visualizer.add_paragraph("Le jeu de données est intéressant car il touche un sujet qui concerne de nombreuses personnes : le coût du carburant. Il permet d’identifier les stations proposant les carburants les moins chers, de comprendre les différences de prix selon les régions, et d’analyser les services associés, comme la disponibilité de bornes de recharge ou de boutiques. Ce jeu de données peut aussi révéler les disparités géographiques, notamment dans les zones rurales où l’accès aux carburants peut être plus limité, et ainsi aider à mieux comprendre les difficultés d'accès ou les zones où l’offre est moins compétitive.")
    visualizer.graph_available_fuel_distribution() \
              .graph_fuel_prices_by_region() \
              .graph_median_prices_by_city_92() \
              .graph_fuel_popularity() \
              .graph_fuel_price_boxplot() \
              .graph_top_departments_highest_price("Gazole") \
              .graph_top_departments_highest_price("SP98") \
              .graph_top_departments_highest_price("E10") \
              .graph_fossil_vs_alternative_fuel_prices() \
              .graph_service_distribution() \
              .graph_automate_24_24_distribution() \
              .graph_average_fuel_outage_duration() \
              .graph_fuel_availability_by_day() \
              .graph_station_distribution_by_population_density() \
              .graph_services_per_station() \
              .graph_cheapest_vs_expensive_station() \
              .graph_avg_prices_highway_vs_others() \
              .graph_avg_price_full_tank_sp98() \
              .export("./out/rapport_johanledoux.pdf")