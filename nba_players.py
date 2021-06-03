#!/usr/bin/env python
# coding: utf-8

# # <u>Data Scraping and Analysis : Build your NBA Dream Team</u>

# <b>
# You want to create the perfect 5 Major ? You want to know who players will be the next NBA stars ? You want to predict what will be the american olympic team at the next Olympic Games ?
# </b>
# <br>
# <br>
# - In this project, I will use NBA players datas in order to create a function that may turn out to be very useful in your team making decision process. 
# <br>
# <br>
# - A Five Major is the five players of a team that start games, oftentimes the best players of the team.

# <b>In this notebook I will use :</b>
# <br>
# - Web scraping for collecting data on a website.
# - Object oriented programming.
# - SQL commands.
# - Data cleaning for making the datas standardized and usable.
# - Data analysis for checking data quality and getting insights.

# ### Packages and librairies

# In[1]:


from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties

import warnings;
warnings.filterwarnings('ignore')

get_ipython().run_line_magic('matplotlib', 'inline')


# ### 2) Web Scraping

# We will scrape each season datas from 1980 to 2020. A season table contain the players average statistics per game.

# In[5]:


### 1) Create the framework of the dataframe

page = requests.get('https://www.basketball-reference.com/leagues/NBA_2020_per_game.html')
soup = BeautifulSoup(page.content,'html.parser')
tableau = soup.find_all(class_="full_table")

head = soup.find(class_='thead')
column_name = [head.text for item in head][0]
column_name = column_name.split('\n')
del(column_name[:2])
del(column_name[-1])
df = pd.DataFrame(columns=column_name)


# In[3]:


df


# In[5]:


### 2) Fill the dataframe

for season in range(1980,2021):
    
    url_players = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'.format(season)
    
    page = requests.get(url_players)
    soup = BeautifulSoup(page.content,'html.parser')
    tableau = soup.find_all(class_="full_table")

    players = []


    for i in range(len(tableau)):
        
        player = []
        for j in tableau[i].find_all('td'):
            player.append(j.text)
        players.append(player)



    head2 = soup.find(class_='thead')
    column_name2 = [head2.text for item in head][0]
    column_name2 = column_name2.split('\n')
    del(column_name2[:2])
    del(column_name2[-1])
    df2 = pd.DataFrame(players, columns=column_name2)
    df2['Season'] = season
    df = df.append(df2,ignore_index=True,sort=False)


# ### 3) Data quality check & data cleaning

# In[14]:


df.head()


# In[21]:


for col in  df.columns[4:30]:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    
df['Age'] = df['Age'].astype(int)
df['Season'] = df['Season'].astype(int)
 


# In[22]:


df.head()


# <b>Check the NaN values percentage in each column. Fortunately columns with NaN will not be use in our case.</b>

# In[29]:


df.isna().sum()/df.shape[0]


# <b>Visualize the composition of non numeric columns</b>

# - A '*' after a player's name means that the players is not in the NBA anymore
# - A basketball team is composed of five players. Each of them has a position : 'C' means 'Center, 'PF' means 'Power Forward', 'PG' means 'Point Guard', 'SG' means 'Shooting Guard', 'SF' means 'Small Forward'. There are also players that get play at two different positions.
# - NBA teams are often reported by their acronym, for instance 'LAL' means 'Los Angeles Lakers'.

# In[37]:


for col in df.select_dtypes('object'):
    print(f'{col :-<40} {df[col].unique()}')


# In[31]:


df.describe().transpose()


# ### 4) Database Storage

# In[103]:


import sqlite3

conn = sqlite3.connect("projects.db")
df.to_sql("nba_players_stats", conn, if_exists="replace")
conn.commit()
conn.close()


# In[63]:


import sqlite3

conn = sqlite3.connect("projects.db")
df = pd.read_sql("SELECT * FROM nba_players_stats", conn)
conn.close()


# In[64]:


df.head()


# ### 5) Data analysis

# <b>Best scorer per season</b>

# In[65]:


df_pts = pd.DataFrame(columns=column_name)

for season in range(1980,2021):
    df2 = df.loc[df['Season']==season].nlargest(1, ['PTS'])
    df_pts = df_pts.append(df2)
    
df_pts[['Player','PTS','Season']].sort_values(by='PTS',ascending=False)


# In[66]:


best_scorers = {}

for i in range(len(df_pts)):
    
    if df_pts.iat[i,0] not in best_scorers:
        best_scorers.update({df_pts.iat[i,0] : 1 })
    else:
        best_scorers[df_pts.iat[i,0]] += 1
        
print(best_scorers)    


# In[67]:


plt.figure(figsize=(10,4.5))
plt.grid(axis = 'x', linestyle = '--', linewidth = 0.4)
plt.xticks(list(range(max(best_scorers.values())+1)))
plt.xlabel('Frequency')
plt.barh(*zip(*best_scorers.items()))
plt.title('Season Best Scorer Frequency')


# <b>Check the evolution of these players</b>

# In[68]:


df2 = df[['Player','Age','PTS']].loc[df['Player'].isin(['Michael Jordan*','Kevin Durant','Kobe Bryant*'])]
df2 = df2.groupby(['Age','Player']).mean()


fontP = FontProperties()



df2.unstack(1).plot(figsize=(10,6),linewidth=4, marker='o')
plt.xticks(list(range(18,40)))
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', prop=fontP)
plt.grid(linestyle = ':')
plt.title('All Times Best NBA Scorers Evolution')


# In[69]:


df_pts.describe().transpose()


# ### 6) Application : Create the perfect Five Major

# In[70]:


df.columns


# In[71]:


df3 = df.copy()


# <b>'TRB' means 'Total Rebounds', 'AST' means Assistances, 'STL' means 'Steals', 'BLK' means 'Blocks', 'PF' means Personal Faults, 'PTS' means 'Points'.
# <br>
# We create a KPI 'all' that synthesizes the players perfomances. </b>

# In[72]:


df3['all'] = df3['TRB']+df3['AST']+df3['STL']+df3['BLK']-df3['PF']+df3['PTS']


# In[73]:


df3[['all']].head()


# In[74]:


df3['Pos'].unique()


# In[75]:


pos_list = list(df3['Pos'].unique())[:5]


# In[76]:


pos_list


# In[77]:


pos_list
L = []

for pos in pos_list:
    
    l = [pos]
    
    for pos2 in list(df3['Pos'].unique())[5:]:
        
        if pos in pos2:
            l.append(pos2)
            
    L.append(l)


# <b>Thanks to this list we can make selections per position category</b>

# In[78]:


L


# <b>Application : We are in 2011 and I want to have an idea of what will the NBA Oympic Team be in 2012.</b>

# In[123]:


df_all = pd.DataFrame(columns=column_name)

players_range = 4
year = 2013
age_max = 40
age_min = 18

for item in L:
    
    df4 = df3.loc[df3['Season'] == year]
    df4 = df4.loc[df4['Pos'].isin(item)]
    df4 = df4.loc[df4['Age'] <= age_max]
    df4 = df4.loc[df4['Age'] >= age_min]
    df4 = df4.nlargest(players_range, ['all'])
    df4['index'] = list(range(players_range))
    df4 = df4.loc[df4['index']==np.random.randint(low=min(df4['index']), high=max(df4['index'])+1)]
    df_all = df_all.append(df4)

print(df_all)    
    
df5 = df3[['Player','Age','all']].loc[df['Player'].isin(list(df_all['Player']))]
df5 = df5.groupby(['Age','Player']).mean()


fontP = FontProperties()



df5.unstack(1).plot(figsize=(10,6),linewidth=5, marker='o',ylabel='General Performance KPI')
plt.xticks(list(range(18,40)))
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', prop=fontP)
plt.grid(linestyle = ':')
plt.title('Potential Players Evolution')
  


# <b>Official 2012 Olympic Team :</b>
# - Chris Paul
# - Deron Williams
# - Russell Westbrook
# - Kobe Bryant
# - James Harden
# - LeBron James
# - Andre Iguodala
# - Kevin Durant
# - Carmelo Anthony
# - Blake Griffin
# - Kevin Love
# - Tyson Chandler
