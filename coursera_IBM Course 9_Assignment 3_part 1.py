#!/usr/bin/env python
# coding: utf-8

# # Data obtaining

# In[1]:


import numpy as np 
import pandas as pd 
import requests
from bs4 import BeautifulSoup


# In[3]:


response = requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
soup = BeautifulSoup(response, 'lxml')


# # Data transforming

# In[4]:


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


# In[5]:


for table in soup.find_all('table', class_="wikitable sortable"):
    df = parse_html_table(table)                      


# In[6]:


df.head()


# # Data cleaning 

# In[7]:


df = df[df.Borough != 'Not assigned']
df = df.replace('\n',' ', regex=True)
df= df[df['Neighbourhood\n'] != 'Not assigned']
df = df.groupby(['Postcode','Borough'])['Neighbourhood\n'].apply(lambda x: ", ".join(x.astype(str))).reset_index()
df = df.sample(frac=1).reset_index(drop=True)
df.head(10)


# In[8]:


df.shape

