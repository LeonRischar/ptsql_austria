import time

import geopandas as gpd
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shapely

from config import *

# load gpkg
def load_isochrones(file):
    """
    Load isochrones from gpkg file and preprocess for area calculation

    Parameters
        file (str): name of file in out/isochrones_gpkg/ folder
    Returns
        isochrones (gpd.GeoDataFrame): isochrones with additional column "ptsql"
    """
    isochrones = gpd.read_file(f"{PATH_OUT_ISOCHRONES}{file}")
    isochrones = isochrones.iloc[1:]
    isochrones['ptsql'] = isochrones['color'].apply(lambda x: [key for key, value in PTSQL_COLORS_DICT.items() if value == x][0])
    isochrones = isochrones.sort_values("ptsql", ascending=True)
    isochrones = isochrones.reset_index().drop(columns=['index'])
    return isochrones

def load_population(file):
    """
    Load population from gpkg file and preprocess i.e. filter by bounds for austria and project to target crs

    Parameters
        file (str): name of file in in/population/ folder, or path to file (starting from in/population/) if in subfolder or in different folder
    """
    print(f"Loading population from {file}", end="\r")
    start_time = time.time()
    population = gpd.read_file(PATH_IN_POPULATION + file)

    coords = population["GRD_ID"].str.extract(r"N(\d+)E(\d+)").astype(int)
    coords.columns = ["N", "E"]

    mask = (
        (coords["N"].between(MIN_N, MAX_N)) &
        (coords["E"].between(MIN_E, MAX_E))
    )

    population = population[mask]

    population.to_crs(crs=TARGET_CRS, inplace=True)

    population = population[['GRD_ID', 'T', 'geometry']]

    print(f"Loaded population from {file} ... {time.time() - start_time:.3f}s")

    return population

def calculate_areas(isochrones, population=None):
    """
    Calcaulate area of each ptsql category. Starts by last category (G) and subtracts areas of all previous categories.

    Parameters
        isochrones (gpd.GeoDataFrame): isochrones with additional column "ptsql"
        population (gpd.GeoDataFrame, optional): population of each area. If not None, population is calculated for each area. (default None)
    Returns
        areas (dict): dictionary of ptsql category and area 
        populations (dict, optional): dictionary of ptsql category and population (if population is not None)
    """

    if population is not None:
        # calculating centroids of each grid cell
        # using centroids speeds up calculation of population but is not very accurate
        population["centroid"] = population.geometry.centroid

    areas = {}
    populations = {}
    prev_geom = None
    prev_pop = 0
    # starting with inner most isochrones the area is calculated, after that the next ischrone "ring" is added, the result is subtracted from the previous full area
    for row in isochrones.itertuples():
        if prev_geom is None:
            full_area = row.geometry
            prev_geom = shapely.Polygon(((0,0), (0,0), (0,0)))
        else:
            full_area = shapely.unary_union([prev_geom, row.geometry])

        areas[row.ptsql] = (full_area.area - prev_geom.area)  / 1000000
        prev_geom = full_area

        if population is not None:
            # checks which centriods are inside iscochrone, then sums up population of each centroid
            # and subtracts the population of previous isochrone to get the population of the current isochrone "ring"
            mask = population["centroid"].within(full_area)
            populations[row.ptsql] = round(population.loc[mask, "T"].sum()) - prev_pop
            prev_pop += populations[row.ptsql]


    if population is not None:
        return areas, populations

    return areas

def create_area_df(days, population = None):
    """
    Create dataframe of areas for each ptsql category for each day

    Parameters
        days (list): list of days to read gpkg and calculate areas for
        population (gpd.GeoDataFrame, optional): population of each area. If not None, population is calculated for each area. (default None)
    Returns
        dfs (pd.DataFrame): dataframe of areas for each ptsql category for each day
    """
    area_dicts = []
    population_dicts = []

    print(f"Calculating areas (and population) for {len(days)} days", end="\r")
    start_time = time.time()

    for day in days:
        f = f"all_regions_{day}.gpkg"
        iso = load_isochrones(f)
        dfs = calculate_areas(iso, population)
        if population is not None:
            area_dicts.append(dfs[0])
            population_dicts.append(dfs[1])
        else:
            area_dicts.append(dfs)

    print(f"Calculated areas (and population) for {len(days)} days ... {time.time() - start_time:.3f}s")
    
    if population is not None:
        df_areas = pd.DataFrame(area_dicts)
        df_populations = pd.DataFrame(population_dicts)

        df_areas.insert(0, "date", days)
        df_populations.insert(0, "date", days)

        return df_areas, df_populations
    else:
        df_areas = pd.DataFrame(area_dicts)
        df_areas.insert(0, "date", days)
        return df_areas
    
def create_evaluation_plot(df, day1, day2, type='area', matrix=False, note_text=False, percent=False):
    """
    Create a heatmap of the differences between the two days.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the area sizes for each ptsql category as columns and the days as rows. Cols: "date, A, B, C, D, E, F, G".
        day1 (int): The first day for which the areas should be compared. Must match an entry in the "date" column in the DataFrame.
        day2 (int): The second day for which the areas should be compared. Must match an entry in the "date" column in the DataFrame.
        type (str, optional): The type of the data. Can be "area" or "population". Defaults to "area".
        matrix (bool, optional): Whether to return a matrix of differences (squared heatmap) instead of a one-dimensional heatmap. Defaults to False.
        note_text (bool, optional): Whether to add a note to the plot indicating the direction of the differences. Defaults to False.
        percent (bool, optional): Whether to display the differences as percentages instead of absolute values. Defaults to False.
    """
    # TODO: add percentages to matrix plot
    d1 = pd.to_datetime(str(day1))
    d2 = pd.to_datetime(str(day2))

    row_day1 = df[df["date"] == day1].drop(columns=["date"])
    row_day2 = df[df["date"] == day2].drop(columns=["date"])
    labels = row_day1.columns.tolist()

    if matrix:
        # a bit complicated to use and understand, 1d heatmap is better (matrix=False)
        pair_wise_diff = np.subtract.outer(row_day1.values.flatten(), row_day2.values.flatten())
        
        plot = sns.heatmap(pair_wise_diff, annot=True, xticklabels=labels, yticklabels=labels, cmap="coolwarm", center=0, fmt=".1f")
        plt.xlabel(f"PTSQL {d2.date()}")
        plt.ylabel(f"PTSQL {d1.date()}")
    else:
        if percent:
            diff = row_day1.values / row_day2.values * 100
        else:
            diff = row_day1.values - row_day2.values

        unit = "km²" if type == "area" else "#"
        yticklabels = ["Difference [%]" if percent else f"Difference [{unit}]"]

        plot = sns.heatmap(diff, annot=True, xticklabels=labels, yticklabels=yticklabels, 
                           cmap="coolwarm", fmt=".0f" if type == 'population' and not percent else ".1f",)

        for text in plot.texts:
            text.set_rotation(45)

        plt.xlabel("PTSQL")

    plt.title(f"Difference of {type} between {d1.date()} and {d2.date()}")
    if note_text:
        if percent:
            text = f"Values greater than 100% indicate a larger {type} for {d1.date()}."
        else:
            text = f"Positive values indicate a larger {type} for {d1.date()}."

        plt.figtext(x=0.5, y=-0.02, s=text, ha="center", fontsize=10)

    return plot

def create_time_series_plot(df, days=[], type='area', day_names=True, plot_size: str|tuple = 'auto', bar_labels=False, groupby=None, custom_labels=None, custom_title=None, rotate_bar_labels=False):
    """
    Creates a time series plot from a dataframe for the given days.

    Parameters:
        df (pandas.DataFrame): Dataframe containing the data to plot.
        days (list): List of days to plot. If empty, all days are plotted. Default is [].
        type (str, optional): The type of the data. Can be "area" or "population". Defaults to "area".
        day_names (bool): Whether to show day names on the x-axis.
        plot_size (tuple or str): Size of the plot. If 'auto', the plot size is automatically adjusted. Else provide a tuple of (width, height). Default is 'auto'.
        bar_labels (bool): Whether to show labels in the bar segments. Default is False.
        groupby (str): Place closer to each other bars by this criterea. Either 'month' or 'day'. Default is None.
        custom_labels (list): Custom labels added to the date tick labels. If provided, must match the number of x ticks. Default is None.
        custom_title (str): Custom title for the plot. Default is None.
        rotate_bar_labels (bool): Whether to rotate the bar labels. Default is False.

    Returns:
        matplotlib.axes.Axes: Axes object containing the plot.
    """
    if len(days) == 0:
        days = list(df.date.values)

    if plot_size == 'auto':
        x_size = max(len(days) - 2, 6)
        y_size = x_size*0.6
    else:
        x_size = plot_size[0]
        y_size = plot_size[1]

    df_filtered = df[df.date.isin(days)].sort_values(by='date')
    dates = list(pd.to_datetime(df_filtered.date, format='ISO8601'))

    x = []
    pos = 0
    prev = None
    for d in dates:
        current = None
        if groupby == 'month':
            current = d.month
        elif groupby == 'day':
            current = d.day
        else:
            pos += 1
            x.append(pos)
            continue

        if prev is not None and current != prev :
            pos += 1.2   # month gap
        else:
            pos += 0.7   # normal gap
        x.append(pos)
        prev = current

    df_filtered['x_pos'] = x

    value_cols = [c for c in df_filtered.columns if c not in ['date', 'month', 'x_pos']]

    #ax = df_filtered.plot(kind='bar', x='x_pos', y=value_cols, stacked=True, color=PTSQL_COLORS, figsize=(x_size, y_size))

    fig, ax = plt.subplots(figsize=(x_size, y_size))

    bottom = np.zeros(len(df_filtered))

    for col, color in zip(value_cols, PTSQL_COLORS_DICT.values()):
        values = df_filtered[col].values

        # print(value_cols)
        # print(values)
        # print(bottom)

        # print("values contains None:", any(v is None for v in values))
        # print("bottom contains None:", any(b is None for b in bottom))

        ax.bar(df_filtered['x_pos'], values, bottom=bottom, width=0.6, color=color, label=col)
        bottom += values

    if day_names:
        #dates = list(pd.to_datetime(df_filtered.date, format='ISO8601'))
        day_names = [d.strftime("%A") for d in dates]
        x_ticks = [str(d.date()) + "\n" + n for d, n in zip(dates, day_names)]
        if custom_labels is not None:
            x_ticks = [l + "\n" + x for x, l in zip(x_ticks, custom_labels)]
        ax.set_xticks(x, x_ticks, rotation=45)
    else:
        x_ticks = [str(d.date()) for d in dates]
        if custom_labels is not None:
            x_ticks = [l + "\n" + x for x, l in zip(x_ticks, custom_labels)]
        ax.set_xticks(x, x_ticks, rotation=45)

    if bar_labels:
        fig.canvas.draw()
        offset_text = ax.yaxis.get_offset_text().get_text()

        for c in ax.containers:
            # Optional: if the segment is small or 0, customize the labels
            labels_texts = [int(v.get_height()) if v.get_height() > 500 else '' for v in c]

            if offset_text.startswith('1e'):
                labels_texts = ["{:.2e}".format(v).replace('+0','') if v != '' else '' for v in labels_texts]  
            
            # remove the labels parameter if it's not needed for customized labels
            ax.bar_label(c, labels=labels_texts, label_type='center', rotation=45 if rotate_bar_labels else 0)

    ax.set_axisbelow(True)
    ax.grid(axis='y', color='gray', linestyle='--')
    plt.ylabel('Area [km²]' if type == 'area' else 'Population [#]')
    plt.legend(loc="center left", bbox_to_anchor=(1,0.6), title="PTSQL")

    if custom_title is not None:
        plt.title(custom_title)
    else:
        plt.title(f'Time Series plot for {type}')

    return fig


def prepare_oerok_data(day1, day2, population=None):
    """
    Load and prepare data from oerok for evaluation

    Parameters:
        day1 (str): Name of Shapefile for day 1 in oerok folder
        day2 (str): Name of Shapefile for day 2 in oerok folder
        population (str, optional): 

    """

    print(f"Loading and calculated oerok data for {day1} and {day2}", end="\r")
    start_time = time.time()

    oerok_populations_day1 = None
    oerok_populations_day2 = None

    oerok_isochrones_day1 = gpd.read_file(PATH_IN_OEROK + day1)
    oerok_isochrones_day2 = gpd.read_file(PATH_IN_OEROK + day2)

    oerok_isochrones_day1.rename(columns={'gueteklass': 'ptsql'}, inplace=True)
    oerok_isochrones_day2.rename(columns={'gueteklass': 'ptsql'}, inplace=True)

    oerok_isochrones_day1.to_crs(crs=TARGET_CRS, inplace=True)
    oerok_isochrones_day2.to_crs(crs=TARGET_CRS, inplace=True)

    if population is None:
        oerok_areas_day1 = calculate_areas(oerok_isochrones_day1)
        oerok_areas_day2 = calculate_areas(oerok_isochrones_day2)
    else:
        oerok_areas_day1, oerok_populations_day1 = calculate_areas(oerok_isochrones_day1, population=population)
        oerok_areas_day2, oerok_populations_day2 = calculate_areas(oerok_isochrones_day2, population=population)

    df_existing_areas = pd.DataFrame([oerok_areas_day1, oerok_areas_day2])
    df_existing_areas.insert(0, "date", OEROK_DAYS)
    if population is not None:
        df_existing_populations = pd.DataFrame([oerok_populations_day1, oerok_populations_day2])
        df_existing_populations.insert(0, "date", OEROK_DAYS)

    print(f"Loaded and calculated oerok data for {day1} and {day2} ... {time.time() - start_time:.3f}s")

    if population is not None:
        return df_existing_areas, df_existing_populations
    else:
        return df_existing_areas


def statistics(df_area, df_population, week_days=WEEKDAYS, weekends=WEEKENDS):

    print(f"Calculating simple statistics for {len(WEEKDAYS + WEEKENDS)} days", end="\r")
    start_time = time.time()

    dfs = []

    for i, df in enumerate([df_area, df_population]):

        avg_weekday = df[df.date.isin(week_days)].mean()
        min_weekday = df[df.date.isin(week_days)].min()
        max_weekday = df[df.date.isin(week_days)].max()
        std_weekday = df[df.date.isin(week_days)].std()

        avg_weekend = df[df.date.isin(weekends)].mean()
        min_weekend = df[df.date.isin(weekends)].min()
        max_weekend = df[df.date.isin(weekends)].max()
        std_weekend = df[df.date.isin(weekends)].std()

        df_new = pd.DataFrame({'avg_weekday': avg_weekday, 'min_weekday': min_weekday, 'max_weekday': max_weekday, 'std_weekday': std_weekday,
                            'avg_weekend': avg_weekend, 'min_weekend': min_weekend, 'max_weekend': max_weekend, 'std_weekend': std_weekend})

        df_new = (
            df_new
            .reset_index(names="group")
            .melt(id_vars="group")
            .assign(
                statistic=lambda x: x["variable"].str.split("_").str[0],
                day=lambda x: x["variable"].str.split("_").str[1]
            )
            .pivot(index=["statistic", "day"], columns="group", values="value")
            .reset_index()
            .drop(columns=["date"])
            .rename_axis(None, axis=1)
        )

        if i == 0:
            df_new.insert(0, "type", "area")
        else:
            df_new.insert(0, "type", "population")

        dfs.append(df_new)

    df_final = pd.concat(dfs)

    print(f"Calculated simple statistics for {len(WEEKDAYS + WEEKENDS)} days ... {time.time() - start_time:.3f}s")

    return df_final

def run_evaluation():
    # run evaluation pipeline

    print("Running evaluation pipeline")
    population = load_population(POPULATION_FILE)

    # calculate areas and population for all days
    df_areas, df_populations = create_area_df(ALL_DAYS, population)

    # calculate areas and population for existing solution from oerok
    df_areas_oerok, df_populations_oerok = prepare_oerok_data(day1=OEROK_NAME_SCHEME.format(OEROK_DAYS[0]),
                                                             day2=OEROK_NAME_SCHEME.format(OEROK_DAYS[1]), population=population)

    df_stats = statistics(df_areas, df_populations)

    # save created dataframes
    df_areas.to_csv(f"{PATH_OUT_EVALUATION}area.csv", index=False)
    df_populations.to_csv(f"{PATH_OUT_EVALUATION}population.csv", index=False)
    df_areas_oerok.to_csv(f"{PATH_OUT_EVALUATION}oerok_area.csv", index=False)
    df_populations_oerok.to_csv(f"{PATH_OUT_EVALUATION}oerok_population.csv", index=False)

    df_stats.to_csv(f"{PATH_OUT_EVALUATION}statistics.csv", index=False)

    print("Creating evaluation plots", end="\r")
    start_time = time.time()

    # loading of existing solutions for debugging
    # df_areas = pd.read_csv(f"{PATH_OUT_EVALUATION}area.csv")
    # df_populations = pd.read_csv(f"{PATH_OUT_EVALUATION}population.csv")
    # df_areas_oerok = pd.read_csv(f"{PATH_OUT_EVALUATION}oerok_area.csv")
    # df_populations_oerok = pd.read_csv(f"{PATH_OUT_EVALUATION}oerok_population.csv")

    # create evaluation plots
    p3 = create_time_series_plot(df_areas, days=WEEKDAYS + WEEKENDS, type="area", day_names=True, 
                             plot_size='auto', bar_labels=True, groupby='month', rotate_bar_labels=True, 
                             custom_title="Areas of PTSQLs for several days in 2024")

    p4 = create_time_series_plot(df_populations, days=WEEKDAYS + WEEKENDS, type="population", day_names=True, 
                                plot_size='auto', bar_labels=True, groupby='month', rotate_bar_labels=True,
                                custom_title="Population of PTSQLs for several days in 2024")
    
    df_a = pd.concat([df_areas_oerok, df_areas], axis=0)
    df_p = pd.concat([df_populations_oerok, df_populations], axis=0)

    custom_labels = ["OEROK", "own", "OEROK", "own"]

    p5 = create_time_series_plot(df_a, days=OEROK_DAYS, type="area", day_names=True, plot_size='auto',
                                bar_labels=True, groupby='day', custom_labels=custom_labels,
                                custom_title="Comparison of OEROK area solution to own solution")  
 
    p6 = create_time_series_plot(df_p, days=OEROK_DAYS, type="population", day_names=True, plot_size='auto',
                                bar_labels=True, groupby='day', custom_labels=custom_labels,
                                custom_title="Comparison of OEROK population solution to own solution")

    custom_labels = ["", "", "OEROK", "", "OEROK", ""]

    p7 = create_time_series_plot(df_a, days=OEROK_DAYS + OTHER_DAYS, type="area", day_names=True, plot_size='auto',
                                bar_labels=True, groupby='day', custom_labels=custom_labels,
                                custom_title="Comparison of OEROK area solution to other days")  

    p8 = create_time_series_plot(df_p, days=OEROK_DAYS + OTHER_DAYS, type="population", day_names=True, plot_size='auto',
                                bar_labels=True, groupby='day', custom_labels=custom_labels,
                                custom_title="Comparison of OEROK population solution to other days")

    # save plots
    p3.savefig(f"{PATH_OUT_FIGS}area.png", bbox_inches='tight')
    p4.savefig(f"{PATH_OUT_FIGS}population.png", bbox_inches='tight')
    p5.savefig(f"{PATH_OUT_FIGS}oerok_area.png", bbox_inches='tight')
    p6.savefig(f"{PATH_OUT_FIGS}oerok_population.png", bbox_inches='tight')
    p7.savefig(f"{PATH_OUT_FIGS}oerok_area_other_days.png", bbox_inches='tight')
    p8.savefig(f"{PATH_OUT_FIGS}oerok_population_other_days.png", bbox_inches='tight')

    print(f"Created and saved evaluation plots to {PATH_OUT_FIGS} ... {time.time() - start_time:.3f}s")


if __name__ == "__main__":
    run_evaluation()