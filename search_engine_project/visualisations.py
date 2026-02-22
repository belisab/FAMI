from data_loader import load_documents
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter
import os

# all musicals with metadata like year_released and venue_type
musicals = load_documents()
#print(type(musicals[0]))
#print(musicals[:10])

venues = [m.venue_type for m in musicals]

# some of the publication dates are not simply 4-digit numbers but year ranges
# or multiple years. This makes sure only the first year mentioned is used so
# that it can be treated as int and displayed in the diagram
four_digit_years = [m.year_released[:4] for m in musicals]

def venue_pie(venues, filename="piechart.png"):
    counted_venues = Counter(venues)
    labels = list(counted_venues.keys())
    sizes = list(counted_venues.values())

    plt.figure()
    plt.pie(sizes, labels = labels)
    plt.title("Distribution of venue types")

<<<<<<< HEAD

    filepath = os.path.join("static", filename).replace("\\", "/")
=======
    filepath = os.path.join("static", filename)
>>>>>>> adbc3050a2e92084a62ed966bd1fa3a391b990e1

    plt.savefig(filepath)
    plt.close()

    return filename


def get_decades(four_digit_years):
    # print(years[0], print(type(int(years[0]))))
    decades = [(int(year) // 10) * 10 for year in four_digit_years]
    counted_decades = Counter(decades)

    return counted_decades


def years_bar(years, filename="barplot.png"):
    if not years:
        return None
    counted_decades = get_decades(years)

    x = sorted(counted_decades.keys())
    y = [counted_decades[d] for d in x]
    decade_labels = [f"{d}s" for d in x]

    
    filepath = os.path.join("static", filename).replace("\\", "/")
    print(filepath)

    #plt.figure(figsize=(8,4))
    plt.bar(decade_labels, y)
    plt.title("Musicals according to their release year")
    plt.xlabel("Year released")
    plt.ylabel("Number of musicals")
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filename






    
