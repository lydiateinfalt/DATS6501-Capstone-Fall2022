import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import numpy as np
import plotly.express as px
#plt.style.use('dark_background')
import matplotlib.pyplot as plt
import circlify





explode = (.03, .03, .3, .03, .03)
label = ['PBS', 'DOU Urban', 'DOU HD Urban', 'DB Urban', 'DB Cities', 'DB Cores']
rural = [63.56, 7.18, 61.37, 32.25, 54.39, 73.06]
urban = [36.44, 92.82, 38.63, 67.75, 45.61, 26.94]


#Stacked barplot
plt.figure()
plt.bar(label, rural, label= 'Rural')
plt.bar(label, urban, label= 'Urban', bottom=rural)
plt.xlabel('Data Source', fontsize = 8)
plt.xticks(rotation=30)
plt.legend()
plt.ylabel('Classification (%)')
plt.title("Pakistan Urban/Rural Percentage DOU vs DB GHS-POP (2015) at 1 km")
#plt.show()

#Group bat plot
fig, ax = plt.subplots(1,1)
plt.figure()
width = 0.4
x = np.arange(len(label))
ax.bar(x-width/2, rural, width, label = 'Rural')
ax.bar(x+width/2, urban, width, label = 'Urban')
ax.set_xlabel('Data Source')
ax.set_xticks(x)
ax.set_xticklabels(label, rotation= 30)
ax.set_ylabel('Classification (%)')
ax.set_title("Pakistan Urban/Rural Percentage DOU vs DB GHS-POP (2015) at 1 km")
ax.legend()
#plt.show()
#########################################################################################

data = pd.read_csv('pak1k_nat.csv')
#sort values based on population size
data.sort_values('pop', inplace=True, ascending = False)
data['Y'] = [1]*len(data)
list_x = list(range(0,len(data)))
data['X'] = list_x

#create a label for each bubble
label = [i+'<br>'+str(j)+'<br>'+str(k)+'<br>'+str(l)+'%' for i,j,k,l in zip(data['method'],
                                                            data['source'],
                                                            data['pop'],
                                                            data['urbanpercent'])]

pal_ = list(sns.color_palette(palette='plasma_r',
                              n_colors=len(data)).as_hex())

fig = px.scatter(data, x='X', y='Y',
                 color='method',
                 size='pop', text=label, size_max=90, title = "Urban Percent (1 km)"

                )
fig.update_layout(width=1600, height=350,
                  margin = dict(t=50, l=0, r=0, b=0),
                  showlegend=False
                 )
fig.update_traces(textposition='top center')
fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
fig.update_layout({'plot_bgcolor': 'white',
                   'paper_bgcolor': 'white'})
fig.show()

# fig_plotly_dark = go.FigureWidget(fig)
# fig_plotly_dark.layout.template = 'plotly_dark'
# fig_plotly_dark.show()


# Plotly interactive pie chart GHS-POP
df1= data.loc[((data['source'] == 'GHS-POP') | (data['source'] == 'PBS'))]
fig = px.pie(df1, values='urbanpercent', names='method',title='Urban Percent (GHS-POP, 1 km)',
             color_discrete_sequence=pal_)
fig.update_layout(width = 800, height = 800,
                  margin = dict(t=0, l=0, r=0, b=0))
fig.update_traces(textfont_size=16)
#fig.show()

# Plotly interactive pie chart WorldPop
df2= data.loc[((data['source'] == 'WorldPop') | (data['source'] == 'PBS'))]
fig = px.pie(df2, values='urbanpercent', names='method', title='Urban Percent (WorlPop, 1 km)',
             color_discrete_sequence=pal_)
fig.update_layout(width = 800, height = 800,
                  margin = dict(t=0, l=0, r=0, b=0))
fig.update_traces(textfont_size=16)
#fig.show()



# Create circular representation of the bubbles

# compute circle positions:
data = pd.read_csv('pak1k_gpo1.csv')
data.sort_values('urbanpercent', inplace=True, ascending = False)
label = [i+'<br>'+str(j)+'<br>'+str(k)+'<br>'+str(l)+'%' for i,j,k,l in zip(data['method'], data['resolution'],data['source'],data['urbanpercent'])]
circles = circlify.circlify(data['urbanpercent'].tolist(),
                            show_enclosure=False,
                            target_enclosure=circlify.Circle(x=0, y=0)
                           )
circles.reverse()

fig, ax = plt.subplots(figsize=(20,20))
ax.axis('off')
lim = max(max(abs(circle.x)+circle.r, abs(circle.y)+circle.r,) for circle in circles)
plt.xlim(-lim, lim)
plt.ylim(-lim, lim)

# print circles
for circle, note, color in zip(circles, label, pal_):
    x, y, r = circle
    ax.add_patch(plt.Circle((x, y), r, alpha=1, color = color))
    plt.annotate(note.replace('<br>','\n'), (x,y), size=24, va='center', ha='center')
plt.xticks([])
plt.yticks([])
plt.savefig('GHSPOP.jpg')
plt.show()

data = pd.read_csv('pak_nat.csv')
data.head()
fig = go.FigureWidget()
for method, source_df in data.groupby('method'):
    fig.add_scatter(x=source_df.source,
                    y=source_df.urbanpercent,
                    marker={'size': source_df['pop'].tolist(), 'sizemode': 'area', 'sizeref': 200000},
                    mode='markers',
                    text=source_df.source,
                    name=method)
fig.layout.xaxis.title = 'Source'
fig.layout.yaxis.title = 'Urban Percent'
fig.layout.title = 'Pakistan Urban % GHS-POP vs WorldPop'
fig.layout.width = 500
fig.layout.height = 500

##########################################
# 250 m resolution
##########################################

data = pd.read_csv('pak_nat.csv')
#sort values based on population size
data.sort_values('pop', inplace=True, ascending = False)
data['Y'] = [1]*len(data)
list_x = list(range(0,len(data)))
data['X'] = list_x


#create a label for each bubble
label = [i+'<br>'+str(j)+'<br>'+str(k)+'<br>'+str(l)+'%' for i,j,k,l in zip(data['method'],
                                                            data['source'],
                                                            data['pop'],
                                                            data['urbanpercent'])]

pal_ = list(sns.color_palette(palette='plasma_r',
                              n_colors=len(data)).as_hex())

fig = px.scatter(data, x='X', y='Y',
                 color='method',
                 size='pop', text=label, size_max=90, title = "Urban Percent (250 m)"

                )
fig.update_layout(width=1500, height=350,
                  margin = dict(t=50, l=0, r=0, b=0),
                  showlegend=False
                 )
fig.update_traces(textposition='top center')
fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
fig.update_layout({'plot_bgcolor': 'white',
                   'paper_bgcolor': 'white'})
fig.show()

# fig_plotly_dark = go.FigureWidget(fig)
# fig_plotly_dark.layout.template = 'plotly_dark'
# fig_plotly_dark.show()

#Plotly Pie Carts

# Plotly interactive pie chart GHS-POP
df1= data.loc[((data['source'] == 'GHS-POP') | (data['source'] == 'PBS'))]
fig = px.pie(df1, values='urbanpercent', names='method',title='Urban Percent (GHS-POP, 250 m²)',
             color_discrete_sequence=pal_)
fig.update_layout(width = 800, height = 800,
                  margin = dict(t=0, l=0, r=0, b=0))
fig.update_traces(textfont_size=16)
#fig.show()

# Plotly interactive pie chart WorldPop
df2= data.loc[((data['source'] == 'WorldPop') | (data['source'] == 'PBS'))]
fig = px.pie(df2, values='urbanpercent', names='method', title='Urban Percent (WorlPop, 250 m²)',
             color_discrete_sequence=pal_)
fig.update_layout(width = 800, height = 800,
                  margin = dict(t=0, l=0, r=0, b=0))
fig.update_traces(textfont_size=16)
#fig.show()


# Create circular representation of the bubbles

# compute circle positions:
data = pd.read_csv('pak1k_upo15.csv')
label = [i+'<br>'+str(j)+'<br>'+str(k)+'<br>'+str(l)+'%' for i,j,k,l in zip(data['method'],
                                                            data['resolution'],
                                                            data['pop'],
                                                            data['urbanpercent'])]
circles = circlify.circlify(data['pop'].tolist(),
                            show_enclosure=False,
                            target_enclosure=circlify.Circle(x=0, y=0)
                           )
circles.reverse()

fig, ax = plt.subplots(figsize=(20,20))
ax.axis('off')
lim = max(max(abs(circle.x)+circle.r, abs(circle.y)+circle.r,) for circle in circles)
plt.xlim(-lim, lim)
plt.ylim(-lim, lim)

# print circles
for circle, note, color in zip(circles, label, pal_):
    x, y, r = circle
    ax.add_patch(plt.Circle((x, y), r, alpha=1, color = color))
    plt.annotate(note.replace('<br>','\n'), (x,y), size=16, va='center', ha='center')
plt.xticks([])
plt.yticks([])
plt.title('WorldPop (1 km² and 250 m²)')
plt.savefig('WorldPop.jpg')
plt.show()