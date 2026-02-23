from data_loader import load_documents
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter
import os
import matplotlib.ticker as mticker

# all musicals with metadata like year_released and venue_type
musicals = load_documents()
#print(type(musicals[0]))
#print(musicals[:10])

venues = [m.venue_type for m in musicals]

# some of the publication dates are not simply 4-digit numbers but year ranges
# or multiple years. This makes sure only the first year mentioned is used so
# that it can be treated as int and displayed in the diagram
four_digit_years = [m.year_released[:4] for m in musicals]


def venue_pie_topn(venues, filename="piechart.png", top_n=6, other_label="Other"):
    # aggregate small slices into a single “Other” category;
    # only display the top 6 venues and group others as "Other"


    counted_venues = Counter(venues)
    total = sum(counted_venues.values())
    if total == 0:
        return None

    # Sort categories by count descending
    items = sorted(counted_venues.items(), key=lambda kv: kv[1], reverse=True)
    top = items[:top_n]
    rest = items[top_n:]

    labels = [k for k, v in top]
    sizes  = [v for k, v in top]

    other_sum = sum(v for _, v in rest)
    if other_sum > 0:
        labels.append(other_label)
        sizes.append(other_sum)

    plt.figure()
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 2 else "",  # show labels >= 2%
        startangle=90,
        pctdistance=0.75,
        labeldistance=1.05
    )
    plt.axis('equal')

    filepath = os.path.join("static", filename).replace("\\", "/")
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()

    return filename


def get_decades(four_digit_years):
    # print(years[0], print(type(int(years[0]))))
    if (len(four_digit_years)) < 20:
        decades = [(int(year) // 10) * 10 for year in four_digit_years]
    else:
        # if there is many hits, the decades on the diagram get cluttered
        # so show quarters of a century instead
        decades = [(int(year) // 25) * 25 for year in four_digit_years]

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
    #print(filepath)

    #plt.figure(figsize=(8,4))
    plt.bar(decade_labels, y)
    #print(len(years))

    #plt.title("Musicals according to their release year")
    plt.xlabel("Year released")
    plt.ylabel("Number of musicals")

    #we do not need decimals so show integers only on y-axis
    ax = plt.gca()
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))  # no decimals

    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()

    return filename






    
