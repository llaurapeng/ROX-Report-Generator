#IMPORT PACKAGES -----------------------------------------------------------------
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio
import openpyxl
import streamlit as st
from PIL import Image
import os



class Viz:
    def __init__(self, data, weight_benchmarks, names_ref):
        self.text_color_rox = ''
        self.rox_output = 0
        #READ IN DATA----------------------------------------------------------------
        
        if True:
            self.data = data
            self.weight_benchmarks = weight_benchmarks 
            self.names_ref = names_ref

            #CREATE DF TO USE ---------------------------------------------------------------

            #date structure
            self.timestamp1 = str (self.data ['Event Start Date'].values [0])
            self.timestamp1 =self.timestamp1 [:10]

            self.timestamp2 = str (self.data ['Event End Date'].values [0])
            self.timestamp2 =self.timestamp2 [:10]

            self.date_range = 'From ' + self.timestamp1+ ' To ' + self.timestamp2

            #makes a dictionary with all the KPIs

            self.values = {'KPI ID':[],
                    'Values':[],
                    'Benchmark':[],
                    'Weight':[],
                    'Index':[],
                    'Input':[]}

            for x in self.data.columns:
                if 'KPI' in x:
                    self.values['KPI ID'].append (x)
                    self.id_val = self.data[x].values[0]
                    self.values ['Values'].append (self.id_val)


            #add benchmark, weight, index, input, output


            for key in self.values['KPI ID']:
                #put the benchmark in-------------------------
                self.benchmark = self.weight_benchmarks.loc[self.weight_benchmarks['KPI ID'] == key, 'Benchmark']
                self.benchmark = self.benchmark.values[0]
                self.values['Benchmark'].append (self.benchmark)
                
                #put the weight in-----------------------------
                self.weight = self.weight_benchmarks.loc[self.weight_benchmarks['KPI ID'] == key, 'Weight']
                self.weight = self.weight.values[0]
                self.values['Weight'].append (self.weight)

                
                #calculate the index---------------------------

                #find the KPI ID index so can index values

                self.ind = self.values['KPI ID'].index (key)
                
                self.index = (1+ ((self.values['Values'][self.ind] - self.benchmark)/self.benchmark)) * 100
                self.values['Index'].append (round (self.index,2))

                #calculate the rox input---------------------------

                self.input = round (self.index * self.weight)
                self.values['Input'].append (self.input)
                self.rox_output+=self.input
                
                

            self.rox_output = round (self.rox_output)



            #FINAL DATA FRAME CREATION ---------------------------------

            self.df = pd.DataFrame (self.values)

            #merge dataframes

            self.include_col = ['KPI ID','KPI Name', 'Bucket','Bucket Name']

            self.names_ref = self.names_ref [self.include_col]


            self.df = pd.merge (self.df, self.names_ref, on = 'KPI ID', how = 'left')


            #sort by buckets
            self.sorted_df = self.df.sort_values (by = 'Bucket', ascending = True)
            self.sorted_df.head (10)

            #PUT VALUES INTO A LIST ---------------------------------

            self.KPI_name = self.sorted_df ['KPI Name'].values 
            self.Weights = self.sorted_df ['Weight'].values
            self.KPI_comb = []
            self.Input = self.sorted_df ['Input'].values
            for i in range (len (self.Weights)):
                self.KPI_comb.append (f'<b> {self.KPI_name[i]}</b>' + ' (' + str (self.Weights[i] * 100) + '%' + ')')

            self.Buckets = self.sorted_df ['Bucket Name'].values

            self.Values = self.sorted_df ['Values'].values
            self.Benchmark = self.sorted_df ['Benchmark'].values
            self.Index = self.sorted_df ['Index'].values

            #TABLE COLORING ---------------------------------

            self.colors = []
            self.text_color = []
            for i, row in self.sorted_df.iterrows ():
                self.bucketNum = row['Bucket'].split () [1]
                if int (self.bucketNum) % 2 != 0:
                    #if odd number then white
                    self.colors.append ('white')
                else:
                    self.colors.append ('#E1EEF2')

                if row ['Index'] > 120:
                    self.text_color.append ('#416243')
                elif row['Index'] <=80:
                    self.text_color.append ('#EC2B39')
                else:
                    self.text_color.append ('black')

            self.colors_text = [
                ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'],
                ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'],
                ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black']
            ]
            self.colors_text = self.colors_text + [self.text_color]


            if self.rox_output > 120: 
                self.text_color_rox = '#416243'
          

            elif self.rox_output < 80: 
                self.text_color_rox = '#EC2B39'
  
            else: 
                self.text_color_rox = 'gray'
                
            


    #TABLE 1  ------------------------------------------------------------------

    #table 1 specific coloring

    def table1(self,prim, textColor): 
        colors = []
        text_color = []
        for i, row in self.sorted_df.iterrows ():
            bucketNum = row['Bucket'].split () [1]
            if int (bucketNum) % 2 != 0:
                #if odd number then white
                colors.append ('white')
            else:
                colors.append ('#E1EEF2')

            if row ['Index'] > 120:
                text_color.append ('#416243')
            elif row['Index'] <=80:
                text_color.append ('#416243')
            else:
                text_color.append ('black')

        colors_text = [
            ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'],
            ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'],
            ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black']
        ]
        colors_text = colors_text + [text_color]
        header_color = 'white'
        header_fill_color = 'white'


        fig = go.Figure(data=[go.Table(
            header=dict(values=['<b>KPI(Weight)</b>', 
                                '<b>Result</b>', 
                                '<b>Benchmark</b>',
                                '<b>Index</b>'],
                    line=dict(width=0),
                    font=dict(color=textColor, size = 13,family='Poppins'),
                        fill_color = prim
                    ),
            cells=dict(values=[self.KPI_comb, self.Values, self.Benchmark,self.Index],
                    align=['left', 'center', 'center', 'center'], 
                    font=dict(color=colors_text,family='Poppins'),
                    fill = dict (color = [colors]),
                    line=dict(width=0)
                    )
            
        )])

        fig.update_layout(
            height=700,  # Specify the height in pixels
            margin=dict(l=0, r=0, t=20, b=0)  # Optional: Adjust margins if needed
        )

        return fig

    #TABLE 2  ------------------------------------------------------------------

    #format + color specifics for table 2

    #modify brand name so that any duplicates would have a blank space

    def table2(self,prim, textColor):
        start = ''
        Buckets_3 = []


        for i in range (len (self.Buckets)):
            if self.Buckets[i] is not start:
                Buckets_3.append (f'<b> {self.Buckets[i]}</b>')
                start = self.Buckets[i]
            else:
                Buckets_3.append(' ')

        #bold the KPI values

        for i in range (len (self.Weights)):
            self.KPI_name [i] = f'<b> {self.KPI_name[i]}</b>'

        #change font sizes

        cell_font_size = [16, 12, 12, 12, 12, 12]  




        #add colors
        colors_text = [
            ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'],
            ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'],
            ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'],
            ['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black']
        ]

        colors_text.append (self.text_color)
        colors_text.append (['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'])
        colors_text.append (['black', 'black', 'black', 'black','black', 'black', 'black', 'black','black'])


        fig2 = go.Figure(data=[go.Table(
            header=dict(values=['',
                                '<b>KPI Name</b>', 
                                '<b>Result</b>', 
                                '<b>Benchmark</b>',
                                '<b>Index</b>',
                                '<b>Weight</b>',
                                '<b>ROX Input</b>'
                            ],
                    line=dict(width=0),
                    font=dict(color=textColor, size = 13,family='Poppins'),
                    fill_color = prim
                    ),
            cells=dict(values=[Buckets_3,self.KPI_name, self.Values, self.Benchmark, self.Index, self.Weights, self.Input],
                    align=['left', 'center', 'center', 'center'], 
                    font=dict(color=colors_text, size = cell_font_size,family='Poppins'),
                    fill = dict (color = [self.colors]),
                    line=dict(width=0)
                    )
            
        )])


        border_color = st.session_state ['primaryColor']
        # Add annotation outside the table
        fig2.add_annotation(
            xref='paper', yref='paper',
            x=.96, y=-.15,  # Coordinates relative to the entire plot
            text='ROX: ' + str (self.rox_output),
            showarrow=False,
            font=dict(size=25, color=self.text_color_rox),
            borderpad=4,  # Padding around the annotation box
            borderwidth=5,  # Border width
            bordercolor=border_color  # Border color

        )

        fig2.update_layout (margin=dict(t=20))
        return fig2

    #THIRD VIZ (histogram) ------------------------------------------------------------------

    def fig3 (self,prim, textColor):
        pio.templates.default = "plotly_white"
        # Assuming sorted_df contains your data and variables are defined (KPI_name, Index, Buckets)

        fig3 = px.histogram(self.sorted_df, x=self.KPI_name, y=self.Index,
                        color=self.Buckets, barmode='group',
                        height=400, text_auto=True)
        '''fig3.update_layout(xaxis_title="<b>KPI Names<b>",
                        xaxis_title_font_color=textColor,
                        xaxis_tickfont_color=textColor,
                        yaxis_title = '<b>Index<b>',
                        yaxis_title_font_color=textColor, 
                        yaxis_tickfont_color=textColor,
                        title = 'Distribution of Index for KPIs',
                        title_font_color=textColor, 
                        legend_title_text="<b>Type",
                        legend_title_font_color=textColor,
                        legend_font_color=textColor  #change legend items color

        )
        '''

        #change color, title, and text  
        fig3.update_layout(
        xaxis_title="<b>KPI Names</b>",
        xaxis_title_font=dict(size=14, family="Poppins", color=textColor),
        xaxis_tickfont=dict(size=12, family="Poppins", color=textColor),
        yaxis_title="",
        yaxis_title_font=dict(size=14, family="Poppins", color = textColor),
        yaxis_tickfont=dict(size=12, family="Poppins", color=textColor),
        title="",
        title_font=dict(size=20, family="Poppins", color= textColor),
        legend_title_text="<b>Type</b>",
        legend_title_font=dict(size=14, family="Poppins", color=textColor),
        legend_font=dict(size=12, family="Poppins", color=textColor)  # Change legend items color
    )
        
        # Update traces to change text size
        fig3.update_traces(
        texttemplate='%{y}',  # Ensure text displays the y-values
        textfont=dict(size=20, family="Poppins", color=textColor),  # Adjust size as needed
        textposition='outside'  # Position text outside the bars
        )

       
        return fig3



    #FOURTH VIZ (gauge plot) ------------------------------------------------------------------

    def fig4(self, prim, textColor): 

        fig4_textcolor = textColor
        fig4 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=self.rox_output,
            number = {'font': {'color': self.text_color_rox}}, 
            domain={'x': [0, 1], 'y': [0, 1]},
            #title={'text': "ROX Score"},
            gauge={
                'axis': {'range': [0, 200], 'tickwidth': 1, 'tickcolor': "black"},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 80], 'color': 'red'},
                    {'range': [80, 120], 'color': 'yellow'},
                    {'range': [120, 200], 'color': '#26ff26'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 100}
            }
        ))

        fig4.add_annotation (
            x = 0.5,
            y = 0, 
            text = '<br> (Weighted) </br>',
            showarrow = False
        )

        fig4.add_annotation (
            x = 1,
            y = 0, 
            text = '<b> Above Threshold </b>',
            showarrow = False
        )

        fig4.add_annotation (
            x = 0,
            y = 0, 
            text = '<b> Below Threshold </b>',
            showarrow = False
        )

        fig4.update_layout (font=dict(family="Poppins",size=18,color=fig4_textcolor),
                            margin=dict(t=0))
        
        return fig4

