# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

import csv
import gzip
import io
import json
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen
from urllib import request, parse
from io import StringIO




class BrasilIO:

    base_url = "https://api.brasil.io/v1/"

    def __init__(self, auth_token):
        self.__auth_token = auth_token

    @property
    def headers(self):
        return {
            "User-Agent": "python-urllib/brasilio-client-0.1.0",
        }
        
    @property
    def api_headers(self):
        data = self.headers
        data.update({"Authorization": f"Token {self.__auth_token}"})
        return data

    def api_request(self, path, query_string=None):
        url = urljoin(self.base_url, path)
        if query_string:
            url += "?" + urlencode(query_string)
        request = Request(url, headers=self.api_headers)
        response = urlopen(request)
        return json.load(response)

    def data(self, dataset_slug, table_name, filters=None):
        url = f"dataset/{dataset_slug}/{table_name}/data/"
        filters = filters or {}
        filters["page"] = 1

        finished = False
        while not finished:
            response = self.api_request(url, filters)
            next_page = response.get("next", None)
            for row in response["results"]:
                yield row
            filters = {}
            url = next_page
            finished = next_page is None

    def download(self, dataset, table_name):
        url = f"https://data.brasil.io/dataset/{dataset}/{table_name}.csv.gz"
        request = Request(url, headers=self.headers)
        response = urlopen(request)
        return response



# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# external CSS stylesheets
external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css'
    #{
    #    'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
    #    'rel': 'stylesheet',
    #    'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
    #    'crossorigin': 'anonymous'
    #}
]

# casosbrstates = pd.read_csv("cases-brazil-states.csv")

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
meta_tags=[
    # A description of the app, used by e.g.
    # search engines when displaying search results.
    {
        'name': 'description',
        'content': 'My description'
    },
    # A tag that tells Internet Explorer (IE)
    # to use the latest renderer version available
    # to that browser (e.g. Edge)
    {
        'http-equiv': 'X-UA-Compatible',
        'content': 'IE=edge'
    },
    # A tag that tells the browser not to scale
    # desktop widths to fit mobile screens.
    # Sets the width of the viewport (browser)
    # to the width of the device, and the zoom level
    # (initial scale) to 1.
    #
    # Necessary for "true" mobile support.
    {
      'name': 'viewport',
      'content': 'width=device-width, initial-scale=1, shrink-to-fit=no'
    },
]

)

app.title='Monitoramento COVID19 na Bahia'

server = app.server


# df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')
df = pd.read_csv(
    'https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-states.csv')
# date,country,state,city,newDeaths,deaths,newCases,totalCases,deathsMS,totalCasesMS,deaths_per_100k_inhabitants,totalCases_per_100k_inhabitants,deaths_by_totalCases,recovered

dfLeitosBahia = pd.read_csv(
    #'leitos-exclusivos-covid-ba.csv')
    'https://raw.githubusercontent.com/galdir/covid19python/master/leitos-exclusivos-covid-ba.csv')





try:
    urlSecretariaSaudeSalvador='http://www.saude.salvador.ba.gov.br/wp-content/graficos/graficosjson.php'
    dataRequest={"tipo": "leitosUTIDisponiveisOcupadosAdulto"}
    dataRequest = parse.urlencode(dataRequest).encode()
    req =  request.Request(urlSecretariaSaudeSalvador, data=dataRequest) # this will make the method "POST"
    resp=request.urlopen(req)
    with resp as f:
        texto=f.read().decode('utf-8')
        csv=StringIO(texto)
        dfLeitosSalvador = pd.read_csv(csv) 

    dfLeitosSalvador.columns=['data','utis totais','utis ocupadas']


    for indexA in dfLeitosSalvador.index:
        texto=dfLeitosSalvador.loc[indexA,'data']
        texto=texto.replace('/','-')
        dfLeitosSalvador.loc[indexA,'data']=datetime.datetime.strptime(texto, '%d-%m-%Y').strftime('%Y-%m-%d')
        if dfLeitosSalvador.loc[indexA,'utis ocupadas']==0:
            print("removendo linha de utis zeradas")
            dfLeitosSalvador.drop([dfLeitosSalvador.index[indexA]],inplace = True)
        #if dfLeitosSalvador.loc[indexA,'data']==dfLeitosSalvador.loc[indexA-1,'data']:
        #    print("data duplicada nas utis de salvador")
        #    if (dfLeitosSalvador.loc[indexA,'utis ocupadas']==0):
        #        dfLeitosSalvador.drop(dfLeitosSalvador.index[indexA])
        #    else:
        #        dfLeitosSalvador.drop(dfLeitosSalvador.index[indexA-1])
            #dfLeitosSalvador.loc[index,'utis totais']=dfLeitosSalvador.loc[index-1,'utis totais']
            #dfLeitosSalvador.loc[index,'utis ocupadas']=dfLeitosSalvador.loc[index-1,'utis ocupadas']

except Exception as e:
    print("ocorreu um erro ao acessar Secretaria de Saude Salvador")
    print(e)
    dfLeitosSalvador = pd.read_csv(
    #'leitos-exclusivos-covid-ba.csv')
    'https://raw.githubusercontent.com/galdir/covid19python/master/leitos-exclusivos-covid-ssa.csv')
    dfLeitosSalvador.columns=['data','leitos ocupados (uti+geral)','leitos totais (uti+geral)','utis ocupadas','utis totais','','']


dfLeitosSalvador.head()

#dfCities=pd.read_csv('https://raw.githubusercontent.com/wcota/covid19br/master/cases-brazil-cities-time.csv')
#dfCities=pd.read_csv('https://data.brasil.io/dataset/covid19/caso_full.csv.gz')

api = BrasilIO("8b21074271c5a273bfd1a82e2eda45198827c1a8")
dataset_slug = "covid19"
table_name = "caso_full"
filters = {"state": "BA", "city": "Salvador"}
data = api.data(dataset_slug, table_name, filters)
dfCities=pd.DataFrame()
for row in data:
    rowdf=pd.DataFrame.from_dict(row, orient='index')
    dfCities=pd.concat([dfCities,rowdf.transpose()], ignore_index=True)



# df=df.drop(df[df.date=='2020-04-29'].index)

states = df.state.unique()
statesClean = []
for s in states:
    if s != 'TOTAL':
        statesClean.append(s)








# df.drop


# def getCasesRate(cases,column):
#    casesRate = df.dataFrame()
#    for i in range(0,cases[column].shape[0]-2):
#        casesRate.loc[df.index[i+2],'SMA_3'] = np.round(((cases[column].iloc[i,1]+ cases[column].iloc[i+1,1] +cases[column].iloc[i+2,1])/3),1)
#    return casesRate

# casosBahia=df.query("state=='BA'")
# taxaNCbahia=(casosBahia.newCases/casosBahia.totalCases)*100
# dfTaxaNCBahia=pd.DataFrame({'date':  casosBahia.date,
#        'taxaNovosCasos': taxaNCbahia})
# dfTaxaNCBahia.date=pd.to_datetime(dfTaxaNCBahia.date,format='%Y-%m-%d')

updatemenus = list([
    dict(active=1,
         buttons=list([
            dict(label='Log Scale',
                 method='update',
                 args=[{'visible': [True, True]},
                       {'title': 'Log scale',
                        'yaxis': {'type': 'log'}}]),
            dict(label='Linear Scale',
                 method='update',
                 args=[{'visible': [True, False]},
                       {'title': 'Linear scale',
                        'yaxis': {'type': 'linear'}}])
            ]),
        )
    ])


#citiesBahia = dfCities[dfCities['state'] == 'BA'].city.unique()
#citiesBahiaWithouSalvador=citiesBahia[citiesBahia!='Salvador/BA']

#print(citiesBahiaWithouSalvador)

df["rateNewDeaths"] = (df.newDeaths/df.deaths)*100
df["rateNewCases"] = (df.newCases/df.totalCases)*100

#dfCities["rateNewCases"]=(dfCities.newCases/dfCities.totalCases)*100
#dfCities["rateNewDeaths"]=(dfCities.newDeaths/dfCities.deaths)*100

# rateNewCasesBa=[]
# for i in range(len(citiesBahia)):
#     #rateNewCasesBa.append(dfCities[dfCities['city'] == citiesBahia[i]]['rateNewCases'].rolling(window=5).mean().tail(1).tolist()[0])
#     rateNewCasesBa.append(dfCities[dfCities['city'] == citiesBahia[i]]['rateNewCases'].tail().mean().tolist()[0])

# #rateNewCasesBa=list((dfCities[dfCities['city'] == i]['rateNewCases'].rolling(
# #    window=5).mean().tail(1)
# #    ) for i in citiesBahia)

# dfRateNewCasesBa=pd.DataFrame(rateNewCasesBa)

# #rateNewCasesBa=sum(rateNewCasesBa)/len(rateNewCasesBa)

# print('velocidade de novos casos na bahia')
# print(dfRateNewCasesBa.mean())


# rateNewCasesBaWithoutSalvador=[]
# for i in range(len(citiesBahiaWithouSalvador)):
#     rateNewCasesBaWithoutSalvador.append(dfCities[dfCities['city'] == citiesBahiaWithouSalvador[i]]['rateNewCases'].rolling(window=5).mean().tail(1).tolist()[0])


# dfRateNewCasesBaWithoutSalvador=pd.DataFrame(rateNewCasesBaWithoutSalvador)
# print('velocidade de novos casos na bahia sem salvador')
# print(dfRateNewCasesBaWithoutSalvador.mean())

# rateNewCasesSalvador=[]
# rateNewCasesSalvador.append(dfCities[dfCities['city'] == 'Salvador/BA']['rateNewCases'].rolling(window=5).mean().tail(1).tolist()[0])


# dfrateNewCasesSalvador=pd.DataFrame(rateNewCasesSalvador)
# print('velocidade de novos casos em salvador')
# print(dfrateNewCasesSalvador.mean())


#print(rateNewCasesBaWithoutSalvador)

today = datetime.datetime.now()
dayMesAtras=today.day
if(dayMesAtras>28):
    dayMesAtras=28
if(today.month==1):
    mesAtras=12
    anoMesAtras=today.year-1
else:
    mesAtras=today.month-1
    anoMesAtras=today.year
    
umMesAtras = datetime.datetime(anoMesAtras, mesAtras, dayMesAtras)
#doisMesesAtras = datetime.datetime(today.year, today.month-2, dayMesAtras)


#x=statesClean,
#y=[
#    (
#        df[df['state'] == i]['rateNewCases'].rolling(
#            window=7).mean().tail(1).tolist()[0]
#    ) for i in statesClean
#]

#fig = px.bar(x=statesClean, 
#y=[(
#        df[df['state'] == i]['rateNewCases'].rolling(
#            window=7).mean().tail(1).tolist()[0]
#    ) for i in statesClean
#], 
#color=y)

app.layout = html.Div(className='container', children=[
    html.H1('Monitoramento de COVID19', className='text-center display-1'),
    html.Div(className='container', children=[
        html.H2('Casos na Bahia', className='text-center bg-secondary text-white display-3'),
        html.Div(className='row', children=[
            html.Div(className='col-sm', children=[
                html.H3('UTIs Adulto exclusivas para COVID19 na Bahia',
                        className='text-center'),
                html.P(
                    '''
                    Números divulgados Secretaria de Saúde da Bahia (SESAB). 
                    Segundo a SESAB o número de leitos é flutuante, representando o quantitativo exato de vagas disponíveis no dia. Intercorrências com equipamentos, rede de gases ou equipes incompletas, por exemplo, inviabilizam a disponibilidade do leito.
                '''
                ),
                
                dcc.Graph(
                    id='leitosUTIBahia',
                    figure={
                        'data': [
                            dict(
                                x=dfLeitosBahia['data'],
                                y=dfLeitosBahia['utis totais'],
                                name='UTIs totais'
                            ),
                            dict(
                                x=dfLeitosBahia['data'],
                                y=dfLeitosBahia['uti ocupadas'],
                                name='UTIs ocupadas'
                            )
                            
                        ],
                        'layout': dict(
                            xaxis={
                                'type': 'line',
                                'title': 'data'
                                # 'range':[umMesAtras,today]
                            },
                            yaxis={
                                'title': 'UTIs',
                                # 'range': [0, df.query("state=='BA'")['deaths'].max()],
                            },
                            #margin={'t': 20},
                            #legend={'x': 0, 'y': 1},
                            legend={'x': 0.5, 'xanchor': 'center', 'yanchor':'center','y': 0.5},
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            #title='UTIs exclusivas para COVID19 na Bahia',

                            hovermode='closest'
                        )
                    }
                )
            ]),

        ]),



    ]),
        html.Div(className='row', children=[
            html.Div(className='col-sm', children=[
                html.H3('Total de Casos na Bahia',className='text-center'),
                dcc.Graph(
                    id='casosBahia',
                    figure={
                        'data': [
                            dict(
                                x=df[df['state'] == 'BA']['date'],
                                y=df[df['state'] == 'BA']['totalCases'],
                                name='BA',
                                
                            )
                        ],
                        'layout': dict(
                            xaxis={'type': 'line', 'title': 'data'},
                            yaxis={
                                'title': 'casos',
                                #'range': [0, df.query("state=='BA'")['totalCases'].max()],
                                #'type':'log'
                            },
                            #title='Total de Casos na Bahia',
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            hovermode='closest',
                            updatemenus=updatemenus
                            

                        )
                    }
                )
            ]),
            html.Div(className='col-sm', children=[
                html.H3('Novos Casos na Bahia',className='text-center'),
                dcc.Graph(
                    id='novosCasosBahia',
                    figure={
                        'data': [
                            dict(
                                x=df[df['state'] == 'BA']['date'],
                                # newCases is collumn 6

                                y=df[df['state'] == 'BA']['newCases'],
                                name='Novos casos',
                                type='bar'
                            ),
                            dict(
                                x=df[df['state'] == 'BA']['date'],
                                # newCases is collumn 6

                                y=df[df['state'] == 'BA']['newCases'].rolling(
                                    window=7).mean(),
                                name='Média Movel de 7 Dias',
                                type='line'
                            )
                        ],
                        'layout': dict(
                            xaxis={'type': 'line', 'title': 'data'
                                   #'range': [umMesAtras, today]
                                   },
                            yaxis={
                                'title': 'Quantidade'
                                # 'range':[0,df.query("state=='BA'")['rateNewDeaths'].tail(31).max()]
                                #'range': [0, 50]
                            },
                            #title='Taxa de Crescimento de Novos Casos na Bahia',
                            legend={'x': 0.5, 'xanchor': 'right', 'y': 1},
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            hovermode='closest'
                        )
                    }
                )
            ])
        ]),


        # html.Div(className='row', children=[
        #     html.Div(className='col-sm', children=[
        #         html.H3('Taxa de Crescimento de Novos Casos na Bahia',className='text-center'),
        #         dcc.Graph(
        #             id='taxaNovosCasosBahia',
        #             figure={
        #                 'data': [
        #                     dict(
        #                         x=df[df['state'] == 'BA']['date'],
        #                         # newCases is collumn 6

        #                         y=df[df['state'] == 'BA']['rateNewCases'],
        #                         name='Novos Casos',
        #                         type='bar'
        #                     ),
        #                     dict(
        #                         x=df[df['state'] == 'BA']['date'],
        #                         # newCases is collumn 6

        #                         y=df[df['state'] == 'BA']['rateNewCases'].rolling(
        #                             window=7).mean(),
        #                         name='Média Movel de 7 Dias',
        #                         type='line'
        #                     )
        #                 ],
        #                 'layout': dict(
        #                     xaxis={
        #                         'type': 'line',
        #                         'title': 'data',
        #                         'range': [doisMesesAtras, today]
        #                     },
        #                     yaxis={
        #                         'title': 'taxa (%)',
        #                         # 'range':[0,df.query("state=='BA'")['rateNewDeaths'].tail(31).max()]
        #                         'range': [0, 50]
        #                     },
        #                     #title='Taxa de Crescimento de Novas Mortes na Bahia',
        #                     #legend={'x': 1, 'xanchor': 'center', 'yanchor':'top', 'y': 0.5},
        #                     legend={'x': 1, 'xanchor': 'right', 'y': 1},
        #                     margin={'l':40,'b':80,'r':40,'t': 40},
        #                     hovermode='closest'
        #                 )
        #             }
        #         )
        #     ])
        # ]),

        html.Div(className='row', children=[
            html.Div(className='col-sm', children=[
                html.H3('Total de Mortes na Bahia',className='text-center'),
                dcc.Graph(
                    id='mortesBahia',
                    figure={
                        'data': [
                            dict(
                                x=df[df['state'] == 'BA']['date'],
                                y=df[df['state'] == 'BA']['deaths'],
                                name='BA',
                            )
                        ],
                        'layout': dict(
                            xaxis={
                                'type': 'line',
                                'title': 'data',
                                # 'range':[umMesAtras,today]
                            },
                            yaxis={
                                'title': 'casos',
                                'range': [0, df.query("state=='BA'")['deaths'].max()],
                            },
                            #title='Total de Mortes na Bahia',
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            hovermode='closest',
                            updatemenus=updatemenus
                        )
                    }
                )
            ]),
            html.Div(className='col-sm', children=[
                html.H3('Novas Mortes na Bahia',className='text-center'),
                dcc.Graph(
                    id='novasMortesBahia',
                    figure={
                        'data': [
                            dict(
                                x=df[df['state'] == 'BA']['date'],
                                # newCases is collumn 6

                                y=df[df['state'] == 'BA']['newDeaths'],
                                name='Novas Mortes',
                                type='bar'
                            ),
                            dict(
                                x=df[df['state'] == 'BA']['date'],
                                # newCases is collumn 6

                                y=df[df['state'] == 'BA']['newDeaths'].rolling(
                                    window=7).mean(),
                                name='Média Movel de 7 Dias',
                                type='line'
                            )
                        ],
                        'layout': dict(
                            xaxis={
                                'type': 'line',
                                'title': 'data'
                                #'range': [umMesAtras, today]
                            },
                            yaxis={
                                'title': 'Quantidade'
                                # 'range':[0,df.query("state=='BA'")['rateNewDeaths'].tail(31).max()]
                                #'range': [0, 50]
                            },
                            #title='Taxa de Crescimento de Novas Mortes na Bahia',
                            #legend={'x': 1, 'xanchor': 'center', 'yanchor':'top', 'y': 0.5},
                            legend={'x': 0.5, 'xanchor': 'right', 'y': 1},
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            hovermode='closest'
                        )
                    }
                )
            ])
        ]),

        




        
    html.Div(className='container', children=[
        html.H2('Casos em Salvador', className='text-center bg-secondary text-white display-3'),

        html.Div(className='row', children=[
            html.Div(className='col-sm', children=[
                html.H3('UTIs Adulto exclusivas para COVID19 em Salvador',
                        className='text-center'),
                html.P(
                    '''
                    Números divulgados Secretaria de Saúde da Bahia (SESAB). 
                    Segundo a SESAB o número de leitos é flutuante, representando o quantitativo exato de vagas disponíveis no dia. Intercorrências com equipamentos, rede de gases ou equipes incompletas, por exemplo, inviabilizam a disponibilidade do leito. 
                '''
                ),
                
                dcc.Graph(
                    id='leitosUTISsa',
                    figure={
                        'data': [
                            dict(
                                x=dfLeitosSalvador['data'],
                                y=dfLeitosSalvador['utis totais'],
                                name='UTIs totais'
                            ),
                            dict(
                                x=dfLeitosSalvador['data'],
                                y=dfLeitosSalvador['utis ocupadas'],
                                name='UTIs ocupadas'
                            )
                            
                        ],
                        'layout': dict(
                            xaxis={
                                'type': 'line',
                                'title': 'data',
                                # 'range':[umMesAtras,today]
                            },
                            yaxis={
                                'title': 'UTIs',
                                # 'range': [0, df.query("state=='BA'")['deaths'].max()],
                            },
                            #margin={'t': 20},
                            #legend={'x': 0, 'y': 1},
                            legend={'x': 0.5, 'xanchor': 'center', 'yanchor':'center','y': 0.5},
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            #title='UTIs exclusivas para COVID19 na Bahia',

                            hovermode='closest'
                        )
                    }
                )
            ]),

        ]),

        html.Div(className='row', children=[
            html.Div(className='col-sm', children=[
                html.H3('Total de casos em Salvador',className='text-center'),
                dcc.Graph(
                    id='totCasesSalvador',
                    figure={
                        'data': [
                            dict(
                                x=dfCities[dfCities['city'] == 'Salvador']['date'],
                                y=dfCities[dfCities['city'] == 'Salvador']['last_available_confirmed'],
                                name='Acumulado Salvador'
                            )
                        ],
                        'layout': dict(
                            xaxis={'type': 'line', 'title': 'data'},
                            yaxis={
                                'title': 'casos',
                                'range': [0, dfCities.query("city=='Salvador'")['last_available_confirmed'].max()],
                            },
                            #title='Total de Casos na Bahia',
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            hovermode='closest'
                        )
                    }
                )
            ]),
            html.Div(className='col-sm', children=[
                html.H3('Novos Casos em Salvador',className='text-center'),
                dcc.Graph(
                    id='newCasesSalvador',
                    figure={
                        'data': [
                            dict(
                                x=dfCities[dfCities['city'] == 'Salvador']['date'],
                                # newCases is collumn 6

                                y=dfCities[dfCities['city'] == 'Salvador']['new_confirmed'],
                                name='Novos Casos',
                                type='bar'
                            ),
                            dict(
                                x=dfCities[dfCities['city'] == 'Salvador']['date'],
                                # newCases is collumn 6

                                y=dfCities[dfCities['city'] == 'Salvador']['new_confirmed'].rolling(
                                    window=7).mean().shift(-6),
                                name='Média Movel de 7 Dias',
                                type='line'
                            )
                        ],
                        'layout': dict(
                            xaxis={'type': 'line', 'title': 'data'
                                   #'range': [umMesAtras, today]
                                   },
                            yaxis={
                                'title': 'Quantidade'
                                # 'range':[0,df.query("state=='BA'")['rateNewDeaths'].tail(31).max()]
                                #'range': [0, 50]
                            },
                            #title='Taxa de Crescimento de Novos Casos na Bahia',
                            legend={'x': 0.5, 'xanchor': 'right', 'y': 1},
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            hovermode='closest'
                        )
                    }
                ),
            ]),
        ]),
        html.Div(className='row', children=[
            html.Div(className='col-sm', children=[
                html.H3('Total de Mortes em Salvador',className='text-center'),
                dcc.Graph(
                    id='totMortesSalvador',
                    figure={
                        'data': [
                            dict(
                                x=dfCities[dfCities['city'] == 'Salvador']['date'],
                                y=dfCities[dfCities['city'] == 'Salvador']['last_available_deaths'],
                                name='Acumulado Salvador'
                            )
                        ],
                        'layout': dict(
                            xaxis={'type': 'line', 'title': 'data'},
                            yaxis={
                                'title': 'casos',
                                'range': [0, dfCities.query("city=='Salvador'")['last_available_deaths'].max()],
                            },
                            #title='Total de Casos na Bahia',
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            hovermode='closest'
                        )
                    }
                )
            ]),
            html.Div(className='col-sm', children=[
                html.H3('Novas Mortes em Salvador',className='text-center'),
                dcc.Graph(
                    id='newDeathsSalvador',
                    figure={
                        'data': [
                            dict(
                                x=dfCities[dfCities['city'] == 'Salvador']['date'],
                                # newCases is collumn 6

                                y=dfCities[dfCities['city'] == 'Salvador']['new_deaths'],
                                name='Novas Mortes',
                                type='bar'
                            ),
                            dict(
                                x=dfCities[dfCities['city'] == 'Salvador']['date'],
                                # newCases is collumn 6

                                y=dfCities[dfCities['city'] == 'Salvador']['new_deaths'].rolling(
                                    window=7).mean().shift(-6),
                                name='Média Movel de 7 Dias',
                                type='line'
                            )
                        ],
                        'layout': dict(
                            xaxis={'type': 'line', 'title': 'data'
                                   #'range': [umMesAtras, today]
                                   },
                            yaxis={
                                'title': 'Quantidade',
                                # 'range':[0,df.query("state=='BA'")['rateNewDeaths'].tail(31).max()]
                                'range': [0, 50]
                            },
                            #title='Taxa de Crescimento de Novos Casos na Bahia',
                            legend={'x': 0.5, 'xanchor': 'right', 'y': 1},
                            margin={'l':40,'b':80,'r':40,'t': 40},
                            hovermode='closest'
                        )
                    }
                ),
            ]),
        ]),
    ]),


    html.Div(className='container', children=[
        html.H2('Comparação Entre Estados do Brasil', className='text-center bg-secondary text-white display-3'),
        html.Div(className='row', children=[
            html.Div(className='col-sm', children=[
                html.H3('Média dos últimos 7 dias da Velocidade de Crescimento de Novos Casos por Dia',className='text-center'),
                dcc.Graph(
                    id='rateNewCasesStates',
                    figure={
                        'data': [
                            dict(
                                x=statesClean,
                                y=[
                                    (
                                        df[df['state'] == i]['rateNewCases'].rolling(
                                            window=7).mean().tail(1).tolist()[0]
                                    ) for i in statesClean
                                ],
                                type='bar',
                                name='taxa dos estados'
                            )
                        ],
                        'layout': dict(
                            xaxis={
                                'type': 'bar',
                                'title': 'Estado',
                                # 'range': [umMesAtras, today]
                            },
                            yaxis={
                                'title': 'taxa (%)',
                                #'range': [0, 50]
                            },
                            #title='Média dos Últimos 5 dias da Taxa de Novos Casos por Dia',
                            # margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                            # legend={'x': 0, 'y': 1},
                            hovermode='closest',
                            margin={'l':40,'b':80,'r':40,'t': 40}
                        )
                    }
                )
            ]),
            html.Div(className='col-sm', children=[
                html.H3('Média dos últimos 7 dias da Velocidade de Crescimento de Novas Mortes por Dia',className='text-center'),
                dcc.Graph(
                    id='rateNewDeathsStates',
                    figure={
                        'data': [
                            dict(
                                # x=df[df['continent'] == i]['gdp per capita'],
                                x=statesClean,
                                y=[
                                    (
                                        df[df['state'] == i]['rateNewDeaths'].rolling(
                                            window=7).mean().tail(1).tolist()[0]
                                    ) for i in statesClean
                                ],
                                type='bar',
                                name='taxa dos estados',
                                
                                # text=df[df['state'] == i]['state'],
                                # mode='markers',
                                # opacity=0.7,
                                # marker={
                                #    'size': 15,
                                #    'line': {'width': 0.5, 'color': 'white'}
                                # },
                            )
                        ],
                        'layout': dict(
                            xaxis={
                                'type': 'line',
                                'title': 'Estado',
                                #'range': [umMesAtras, today]
                            },
                            yaxis={
                                'title': 'taxa (%)',
                                #'range': [0, 50]
                            },
                            margin={'l': 40, 'b': 80, 't': 40, 'r': 40},
                            #title='Média Móvel de 5 dias da Taxa de Novas Mortes por Dia',
                            # legend={'x': 0, 'y': 1},
                            hovermode='closest'
                        )
                    }
                ),
            ]),
        ]),
        html.Div(className='row', children=[
            html.Div(className='col-sm', children=[
                html.H3('Mortes por 100k habitantes',className='text-center'),
                dcc.Graph(
                    id='deaths_per_100k_inhabitants',
                    figure={
                        'data': [
                            dict(
                                # x=df[df['continent'] == i]['gdp per capita'],
                                #x=df[df['state'] == i]['date'],
                                x=statesClean,
                                y=[
                                    (
                                        df[df['state'] == i]['deaths_per_100k_inhabitants'].tail(1).tolist()[0]
                                    ) for i in statesClean
                                ],
                                #y=df[df['state'] == i]['deaths_per_100k_inhabitants'].tail(1),
                                # text=df[df['state'] == i]['state'],
                                # mode='markers',
                                # opacity=0.7,
                                # marker={
                                #    'size': 15,
                                #    'line': {'width': 0.5, 'color': 'white'}
                                # },
                                #name=i,
                                type='bar',
                                #orientation='h'
                            ) #for i in statesClean
                        ],
                        'layout': dict(
                            xaxis={
                                'type': 'line',
                                'title': 'data',
                                'range': [umMesAtras, today]
                            },
                            yaxis={'title': 'Mortes por 100k habitantes'},
                            margin={'l': 40, 'b': 80, 't': 40, 'r': 40},
                            #title='Mortes por 100k habitantes',
                            # legend={'x': 0, 'y': 1},
                            hovermode='closest'
                        )
                    }
                )
            ])
        ])
    ]),
    html.Div(children=[
        html.P(children=[
            'Produzido por ',
            html.A(children='Galdir Reges', href='https://galdir.github.io/')
        ]),

        html.P(children=[
            'Dados de ',
            html.A(children='Wesley Cota', href="https://covid19br.wcota.me/"),
            ' e ',
            html.A(children='Secretaria de Saúde da Bahia',
                   href="http://www.saude.ba.gov.br/"),

        ]),
    ]),


])
# deaths_per_100k_inhabitants
if __name__ == '__main__':
    app.run_server(debug=True)
