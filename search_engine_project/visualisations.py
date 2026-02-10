from data_loader import load_documents
import matplotlib.pyplot as plt
#from app import results
from collections import Counter
import os

# musicals with information like year_released and venue_type
musicals = load_documents()
#print(type(musicals[0]))
#print(musicals[:10])

#venue_types = [m.venue_type for m in musicals]
#years = [m.year_released[:4] for m in musicals]
#years.sort()
#print(venue_types)
#print(years)

#search_results = results

#print(type(search_results))

def venue_pie():
    plt.ion()
    plt.figure()


def get_years(years):
   # years = search_results_years
    print(years[0], print(type(int(years[0]))))
    decades = [(int(year) // 10) * 10 for year in years]
    counted_decades = Counter(decades)

    return counted_decades

    #counted_years = Counter(years)
    #years_sorted = sorted(counted_years.keys())
    #count_sorted = [counted_years[y] for y in counted_years]
    #print(count_sorted)
    #print(years_sorted)
    #print(len(years_sorted))
    #return years_sorted, count_sorted

def years_bar(years, filename="barplot.png"):
    if not years:
        return None
    counted_decades = get_years(years)

    x = sorted(counted_decades.keys())
    y = [counted_decades[d] for d in x]
    decade_labels = [f"{d}s" for d in x]

    # Ensure static folder exists
    os.makedirs("static", exist_ok=True)
    filepath = os.path.join("static", filename)

    plt.figure()
    plt.bar(decade_labels, y)
    plt.title("Musical according to their release year")
    plt.xlabel("Year released")
    plt.ylabel("Number of musicals")
    plt.savefig(filepath)
    plt.close()

    return filename




def main():
    years_bar()
main()



    
