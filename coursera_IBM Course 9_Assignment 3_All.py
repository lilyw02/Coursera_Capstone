#!/usr/bin/env python
# coding: utf-8

# # Data obtaining

# In[1]:


import numpy as np 
import pandas as pd 
import requests
from bs4 import BeautifulSoup


# In[2]:


response = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup = BeautifulSoup(response, 'lxml')


# # Data transforming

# In[3]:


def parse_html_table(table):
        n_columns = 0
        n_rows=0
        column_names = []
        for row in table.find_all('tr'):
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows+=1
                if n_columns == 0:
                    n_columns = len(td_tags)
                        
            th_tags = row.find_all('th') 
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())
    
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")
    
        columns = column_names if len(column_names) > 0 else range(0,n_columns)
        df = pd.DataFrame(columns = columns,
                              index= range(0,n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1
                    
        for col in df:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass
            
        return df


# In[4]:


for table in soup.find_all('table', class_="wikitable sortable"):
    df = parse_html_table(table)                      


# In[5]:


df.head()


# # Data cleaning 

# In[6]:


df = df[df.Borough != 'Not assigned']
df = df.replace('\n',' ', regex=True)
df= df[df['Neighbourhood\n'] != 'Not assigned']
df = df.groupby(['Postcode','Borough'])['Neighbourhood\n'].apply(lambda x: ", ".join(x.astype(str))).reset_index()
df = df.sample(frac=1).reset_index(drop=True)
df.head(10)


# In[7]:


df.shape


# # Geo info. obtaining

# In[8]:


geo_data=pd.read_csv("http://cocl.us/Geospatial_data")
geo_data.head(10)


# # Data combining

# In[9]:


geo_data.rename(columns={'Postal Code':'Postcode'}, inplace=True)
geo_data.head()


# In[10]:


full_table =df.merge(geo_data, on="Postcode", how='left')
full_table.head(10)


# # visualize my neighborhoods in New York City

# In[11]:


from geopy.geocoders import Nominatim 
import matplotlib.cm as cm
import matplotlib.colors as colors
from sklearn.cluster import KMeans
import folium


# In[12]:


address = 'New York City'
geolocator = Nominatim()
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of New York City are {}, {}.'.format(latitude, longitude))


# In[13]:


map_geo = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(full_table['Latitude'], full_table['Longitude'], full_table['Neighbourhood\n']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=3,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_geo)  
    
map_geo


# In[ ]:




