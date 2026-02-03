import pandas as pd

df = pd.read_csv(
    "Retail_sales_comp.csv",
    engine="python",
    on_bad_lines="skip"
)



# remove missing values
df = df.dropna()

# convert InvoiceDate to datetime
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# create TotalAmount column
df["TotalAmount"] = df["Quantity"] * df["Price"]

# remove negative quantities (returns)
df = df[df["Quantity"] > 0]

print(df.head())



df.to_csv("clean_retail_sales.csv", index=False)
print("ETL completed. File saved.")



