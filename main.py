# Data Extraction

import requests

url = "https://dubaievhub.ae/available-ev-chargers/available-vehicles-in-the-uae/"
response = requests.get(url)

from bs4 import BeautifulSoup

soup = BeautifulSoup(response.content, "lxml")

manufacturer = []
EVmodel = []
EVtype = []
EVrange = []

import re

for a in soup.findAll("div", attrs={"class": "col-sm-3 dis-en"}):
    name = a.find("h4")
    model = a.find("li", string=re.compile("Model :"))
    vtype = a.find("li", string=re.compile("Type :"))
    vrange = a.find("li", string=re.compile("Range :"))

    manufacturer.append(name)
    EVmodel.append(model)
    EVtype.append(vtype)
    EVrange.append(vrange)

import pandas as pd

Data = {
    "Manufacturer": manufacturer,
    "EV Model": EVmodel,
    "EV Type": EVtype,
    "Range": EVrange,
}

df = pd.DataFrame(Data)

df.to_csv("raw_data.csv", index=False)

# Data Cleansing

df2 = pd.read_csv("raw_data.csv")

for a in df2.columns:
    df2[a] = df2[a].str.split("<").str[1]
    df2[a] = df2[a].str.split(">").str[1]

for a in df2.columns[1:4]:
    df2[a] = df2[a].str.split(": ").str[1]

df2["Range"] = df2["Range"].str.split(" ").str[0]

"""
Replacements done in an effort to convert the dtype of the 'Range' column to int before performing analysis 
df2['Range'].value_counts() was used to understand the raw data of the column before replacements
"""

df2["Range"] = df2["Range"].replace("Pending", 0)
df2["Range"] = df2["Range"].replace("", 0)
df2["Range"] = df2["Range"].replace("785km", 785)

df2["Range"] = df2["Range"].astype(int)

# Trimming whitespaces

for a in df2.columns:
    if df2[a].dtype == object:
        df2[a] = df2[a].str.strip()

# Clean data obtained

df2.to_csv("clean_data.csv", index=False)

# Data Analysis

divider = "--------------------------------"

print(divider)
print("Data Analysis")
print(divider, end="\n\n")

print("Data Description")
print(divider)
print(df2.describe())
print(divider, end="\n\n")

maxValueIndex = df2["Range"].idxmax()
print("Vehicle with the greatest range")
print(divider)
print(df2.loc[[maxValueIndex]])
print(divider, end="\n\n")

print("All vehicles with a range of precisely 482")
print(divider)
print(df2[df2["Range"] == 482])
print(divider, end="\n\n")

df2_filtered = df2.groupby("EV Type")["Range"].mean().reset_index()
df2_filtered.columns = ["EV Type", "Average Range"]
print("Average Range by EV Type")
print(divider)
print(df2_filtered)
print(divider, end="\n\n")

print("Distribution of EV Types")
print(divider)
print(df2["EV Type"].value_counts().reset_index())
print(divider, end="\n\n")

print("Distribution of Manufacturers")
print(divider)
print(df2["Manufacturer"].value_counts().reset_index())
print(divider, end="\n\n")

# Data Visualization

import matplotlib.pyplot as plt

# Bar Plot for Average Range by EV Type

avg_range_evtype = df2.groupby("EV Type")["Range"].mean().reset_index()
plt.bar(avg_range_evtype["EV Type"], avg_range_evtype["Range"], color="y")
plt.title("Average Range by EV Type")
plt.xlabel("EV Type")
plt.ylabel("Average Range (km)")
plt.show()

# Bar Plot for Count of EVs by Manufacturer

count_by_manufacturer = df2["Manufacturer"].value_counts().reset_index()
count_by_manufacturer.columns = ["Manufacturer", "Count"]
plt.bar(
    count_by_manufacturer["Manufacturer"],
    count_by_manufacturer["Count"],
    color="salmon",
)
plt.title("Count of EVs by Manufacturer")
plt.xlabel("Manufacturer")
plt.ylabel("Count of EVs")
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# Histogram for Distribution of Ranges

df2_filtered = df2[df2["Range"] != 0]
plt.hist(df2_filtered["Range"], bins=10, color="blue", edgecolor="k")
plt.title("Distribution of Ranges (excluding 0 km)")
plt.xlabel("Range (km)")
plt.ylabel("Frequency")
plt.show()
