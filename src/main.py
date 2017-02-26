import csv
import sys

#For html graphs
import plotly.plotly as ply
from plotly.graph_objs import Scatter, Figure, Layout
from plotly.offline import plot
import squarify
import rpy2

#For radar chart
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from sklearn.preprocessing import normalize
import pylab as pl


"""
Graphs military expenditure per country from 2000-2015.
Data value legend available in spreadsheet.
"""
def graph_military_spending_over_time():
	#Generate scatter plots for each country
	data = []
	with open('data/SIPRI-Milex-data-1988-2015-cleaned-current-usd.csv') as current_usd:
		reader = csv.reader(current_usd)
		headers = next(reader, None)
		for row in reader:
			#Data unavailable, or country didn't exist at the time
			if('. .' in row[13:]  or 'xxx' in row[13:]):
				continue
			trace = Scatter(
				x = headers[13:],
				y = row[13:],
				name = row[0],
				fill = 'tonexty',
				line = dict(width=.5),
				mode = 'lines',
				textfont=dict(
					family='sans serif',
					size=30,
					color='#ff7f0e'
				)
			)
			data.append(trace)

	#Sort scatter plots by countries with highest expenditures in 2015
	data = sorted(data, key=lambda trace: float(trace.y[-1]))

	#Layout taken from https://plot.ly/python/figure-labels/
	layout = Layout(
	    title='Discretionary Military Spending 2000-2015',
	    xaxis=dict(
	        title='Year',
	        titlefont=dict(
	            family='Courier New, monospace',
	            size=26,
	            color='#7f7f7f'
	        )
	    ),
	    yaxis=dict(
	        title='Millions of 2015 US dollars',
	        titlefont=dict(
	            family='Courier New, monospace',
	            size=26,
	            color='#7f7f7f'
	        )
	    ),
	    annotations=[
		    dict(
	            x=2009,
	            y=668567,
	            xref='x',
	            yref='y',
	            text='Obama Takes Office; deployments in Iraq winding down',
	            showarrow=True,
	            arrowhead=7,
	            ax=-120,
	            ay=-40
	        ),
	        dict(
	            x=2003,
	            y=415223,
	            xref='x',
	            yref='y',
	            text='Beginning of Iraq War',
	            showarrow=True,
	            arrowhead=7,
	            ax=-20,
	            ay=-40
	        ),
			dict(
	            x=2011,
	            y=711338,
	            xref='x',
	            yref='y',
	            text='Official end of Iraq War',
	            showarrow=True,
	            arrowhead=7,
	            ax=0,
	            ay=-25
	        ),
			dict(
	            x=2001,
	            y=312743,
	            xref='x',
	            yref='y',
	            text='9/11; Beginning of War in Afghanistan',
	            showarrow=True,
	            arrowhead=7,
	            ax=-20,
	            ay=-40
	        ),
			dict(
	            x=2014,
	            y=609914,
	            xref='x',
	            yref='y',
	            text='Official End of War in Afghanistan',
	            showarrow=True,
	            arrowhead=7,
	            ax=20,
	            ay=-40
	        )
    	]
	)
	fig = Figure(data=data[len(data)-15:], layout=layout)
	plot(fig, filename="images/military-spending-over-time")



"""
Plots treemap of military expenditure in 2015.
Derived from https://plot.ly/python/treemaps/ .
"""

def treemap_military_spending_2015():

	def format_spending_text(tup):
		return str(tup[0] + '<br>${:,.2f}B.'.format(tup[1]/1000))

	#Colors taken from colorbrewer2.org
	colors = ['rgb(165,0,38)','rgb(215,48,39)','rgb(244,109,67)',
			  'rgb(253,174,97)','rgb(254,224,144)','rgb(255,255,191)',
			  'rgb(224,243,248)','rgb(171,217,233)','rgb(116,173,209)',
			  'rgb(69,117,180)','rgb(49,54,149)']

	#Read in data
	data = []
	with open('data/SIPRI-Milex-data-1988-2015-cleaned-current-usd.csv') as current_usd:
		reader = csv.reader(current_usd)
		headers = next(reader, None)[1:]
		for row in reader:
			#Data unavailable, or country didn't exist at the time
			if('. .' in row[12:]  or 'xxx' in row[12:]):
				continue
			data.append((row[0],float(row[-1])))

	#Sort data by amount spent in 2015, select top 15 spenders
	data = sorted(data, key=lambda tup: tup[1])[len(data)-15:]

	#Squarify data
	x = 0
	y = 0
	width = 100
	height = 100
	normed = squarify.normalize_sizes([tup[1] for tup in data], width, height)
	rects = squarify.squarify(normed, x, y, width, height)

	#Generate treemap (taken directly from https://plot.ly/python/treemaps/)
	shapes = []
	annotations = []
	color_counter = 5
	country_counter = 0
	for r in rects:
	    shapes.append( 
	        dict(
	            type = 'rect', 
	            x0 = r['x'], 
	            y0 = r['y'], 
	            x1 = r['x']+r['dx'], 
	            y1 = r['y']+r['dy'],
	            line = dict( width = 2 ),
	            fillcolor = colors[color_counter]
	        ) 
	    )
	    annotations.append(
	        dict(
	            x = r['x']+(r['dx']/2),
	            y = r['y']+(r['dy']/2),
	            text = format_spending_text(data[country_counter]),
	            font=dict(family='Courier New, monospace', size=15, color='#000000'),
	            showarrow = False
	        )
	    )
	    color_counter += 1
	    country_counter += 1
	    if color_counter >= len(colors):
	        color_counter = 0


	# For hover text
	trace = Scatter(
	    x = [ r['x']+(r['dx']/2) for r in rects ], 
	    y = [ r['y']+(r['dy']/2) for r in rects ],
	    text = [ '${:,.2f}'.format(tup[1]*1000) for tup in data ], 
	    mode = 'text',
	)
	        
	layout = dict(
	    height=900, 
	    width=900,
	    shapes=shapes,
	    annotations=annotations,
	    hovermode='closest',
		title='Top 15 National Expenditures on Military 2015',
		font=dict(family='Courier New, monospace', size=21, color='#000000')
	)

	#Plot treemap
	fig = Figure(data=[trace], layout=layout)
	plot(fig, filename="images/military-spending-2015-treemap")

"""
Defined using example at 
http://stackoverflow.com/questions/24659005/radar-chart-with-multiple-scales-on-multiple-axes .
"""
def military_equipment_radar_chart():
	#Labels for markings in radar chart
	labels = [
		[3200, 6400, 9600, 12800, 16000],
		[2, 4, 6, 8, 10],
		[7, 14, 21, 28, 35],
		[5, 10, 15, 20, 25],
		[15, 30, 45, 60, 75],
		[10, 20, 30, 40, 50],
		[10, 20, 30, 40, 50],
		[15, 30, 45, 60, 75],
		[15, 30, 45, 60, 75],
		[800, 1600, 2400, 3200, 4000],
		[400, 800, 1200, 1600, 2000],
		[2000, 4000, 6000, 8000, 10000],
		[25, 50, 75, 100, 125]
	]

	#Pull in data
	data = []
	titles = list()
	with open('data/military-equipment-2015-top-five.csv') as equipment:
		reader = csv.reader(equipment)
		titles = list(next(reader, None))
		data = list(reader)
	print(data)

	#Read data into features array, normalize values according to highest value on axis
	features = [(title,[]) for title in titles]
	for row in data:
		row_index = 0
		for val in row:
			features[row_index][1].append(val)
			row_index += 1

	label_index = 0
	normalized_features = []
	for tup in features[1:]:
		normalized_features.append((tup[0], [5*int(value)/labels[label_index][-1] for value in tup[1]]))
		label_index += 1
	print(normalized_features)

	#Transpose and drop normalized values into normalized data array (super inefficient, sue me)
	normalized_data = [ [], [], [], [], [] ]
	for label, feature in normalized_features:
		x = 0
		for val in feature:
			normalized_data[x].append(val)
			x += 1


	class Radar(object):

	    def __init__(self, fig, titles, labels, rect=None):
	        if rect is None:
	            rect = [0.1, 0.1, .8, .8]

	        self.n = len(titles)
	        self.angles = np.arange(90, 90+360, 360.0/self.n)
	        self.axes = [fig.add_axes(rect, projection="polar", label="axes%d" % i) 
	                         for i in range(self.n)]

	        self.ax = self.axes[0]
	        self.ax.set_thetagrids(self.angles, labels=titles, fontsize=28)

	        for ax in self.axes[1:]:
	            ax.patch.set_visible(False)
	            ax.patch.set_fill(True)
	            #ax.grid("off")
	            ax.xaxis.set_visible(False)

	        for ax, angle, label in zip(self.axes, self.angles, labels):
	            ax.set_rgrids(range(1, 6), angle=angle, labels=label, fontsize=22)
	            ax.spines["polar"].set_visible(True)
	            ax.set_ylim(0, 5)

	    def plot(self, values, *args, **kw):
	        angle = np.deg2rad(np.r_[self.angles, self.angles[0]])
	        values = np.r_[values, values[0]]
	        self.ax.plot(angle, values, *args, **kw)



	fig = pl.figure(figsize=(40, 20))

	print(titles)
	radar = Radar(fig, titles[1:], labels)
	index = 0
	colors = ['#a6cee3','#1f78b4','#c51b8a','#33a02c','#fb9a99']
	for row in normalized_data:
		radar.plot(row, "-", lw=7, color=colors[index], alpha=1, label=features[0][1][index])
		index += 1
		print(index)
	radar.ax.legend()

	fig.savefig("images/radar-chart")


"""
Creates graphic depicting the area of effect that all deployed nuclear weapons
from the United States could conceivably have.
"""
def nuclear_stockpile_area_of_effect():
	pass

"""
Generate treemap of estimates for different civilian policy agendas
(universal health care, free education, etc.) vs. our military budget.
Sources: 
	Est. Cost of Free Education: https://www.theatlantic.com/business/archive/2014/01/heres-exactly-how-much-the-government-would-have-to-spend-to-make-public-college-tuition-free/282803/
	DoE Clean Energy R&D: https://energy.gov/fy-2017-department-energy-budget-request-fact-sheet
	Est. Cost of the Boarder Wall: http://www.reuters.com/article/us-usa-trump-immigration-wall-exclusive-idUSKBN15O2ZN
	NASA Budget: https://www.nasa.gov/sites/default/files/atoms/files/fy_2017_nasa_agency_fact_sheet.pdf
	ACA Cost Estimate: http://time.com/money/4271224/obamacare-cost-taxpayers-2016/
	Foreign Aid Estimate: https://www.washingtonpost.com/news/worldviews/wp/2016/09/26/the-u-s-foreign-aid-budget-visualized/?utm_term=.f7ab9ca36dd5

All dollar amounts have been adjusted to reflect 2017 dollars.
"""
def civilian_agenda_item_costs():
	#Data for policies and associated costs;
	#data is in absolute number of dollars
	data = [
		("Discretionary Military Spending FY 2000", 301700000000),
		("Difference from FY'00 to FY'15", 312700000000),
		("Est. Cost of<br>Free Education<br> circa 2014", 65130000000),
		("Annualized Cost of<br>Affordable<br>Care Act<br>FY'16", 112500000000),
		("DoE<br>Clean<br>Energy<br>R&D<br>FY'17", 12600000000),
		("US Foreign Aid<br>Allocation<br>FY'17", 50100000000),
		("Est. Cost of<br>the Boarder<br>Wall", 21600000000),
		("NASA's<br>FY'16<br>Budget", 19730000000)
	]

	for x in range(len(data)):
		data[x] = (data[x][0] + '<br>${:,}B.'.format(int(data[x][1]/1000000000)), data[x][1])

	#colors taken from colorbrewer2.org
	colors = ['rgb(213,62,79)','rgb(252,141,89)','rgb(254,224,139)','rgb(255,255,191)','rgb(230,245,152)','rgb(153,213,148)','rgb(50,136,189)']

	#Squarify data
	x = 0
	y = 0
	width = 100
	height = 100
	normed = squarify.normalize_sizes([tup[1] for tup in data], width, height)
	rects = squarify.squarify(normed, x, y, width, height)

	#Generate treemap (taken directly from https://plot.ly/python/treemaps/)
	shapes = []
	annotations = []
	color_counter = 6
	policy_counter = 0
	for r in rects:
	    shapes.append( 
	        dict(
	            type = 'rect', 
	            x0 = r['x'], 
	            y0 = r['y'], 
	            x1 = r['x']+r['dx'], 
	            y1 = r['y']+r['dy'],
	            line = dict( width = 2 ),
	            fillcolor = colors[color_counter]
	        ) 
	    )
	    annotations.append(
	        dict(
	            x = r['x']+(r['dx']/2),
	            y = r['y']+(r['dy']/2),
	            text = data[policy_counter][0],
	            font=dict(family='Courier New, monospace', size=15, color='#000000'),
	            showarrow = False
	        )
	    )
	    color_counter += 1
	    policy_counter += 1
	    if color_counter >= len(colors):
	        color_counter = 0


	# For hover text
	trace = Scatter(
	    x = [ r['x']+(r['dx']/2) for r in rects ], 
	    y = [ r['y']+(r['dy']/2) for r in rects ],
	    text = [ '${:,.2f}'.format(tup[1]) for tup in data ], 
	    mode = 'text',
	)
	        
	layout = dict(
	    height=950, 
	    width=950,
	    shapes=shapes,
	    annotations=annotations,
	    hovermode='closest',
		title='Policy Costs vs. Military Spending',
		font=dict(family='Courier New, monospace', size=24, color='#000000')
	)

	#Plot treemap
	fig = Figure(data=[trace], layout=layout)
	plot(fig, filename="images/policy-spending-treemap")

def main():
	graph_military_spending_over_time()
	treemap_military_spending_2015()
	military_equipment_radar_chart()
	nuclear_stockpile_area_of_effect()
	civilian_agenda_item_costs()
	return 0

if __name__ == '__main__':
	sys.exit(main())
