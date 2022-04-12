import folium
import geocoder
import dash
import re
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import requests
from bs4 import BeautifulSoup
import dash_table


type_ = ['Active', 'Passive', 'Both']
budget_ = ['< $25', '< $50', '< $100', '< $150', '< $200', '< $300', '< $500']
distance = ['<10km', '<25km', '<50km', '<100km', '<150km', '<300km']
regions = {'yerevan': 'yerevan', 'aragatsotn': 'ashtarak',
           'ararat': 'artashat', 'armavir': 'armavir',
           'gegharkunik': 'gavar', 'kotayk': 'abovyan',
           'lori': 'vanadzor', 'shirak': 'gyumri',
           'syunik': 'kapan', 'tavush': 'ijevan',
           'vayotsdzor': 'yeghegnadzor', 'artsakh': 'stepanakert'}

g = geocoder.ip('me')
mapp = folium.Map(location=g.latlng, zoom_start=11)
mapp.save('map.html')

res = dict()
for i, j in regions.items():
    url = f'https://exanak.am/current-weather-forecast/{i}/{j}'
    page = requests.get(url).content
    page = BeautifulSoup(page, 'html.parser')
    res[f'{f"{i}".capitalize()}, {f"{j}".capitalize()}'] = f'{page.find("div", class_="num").text}'
weather = pd.DataFrame({"Region": res.keys(), "Weather": res.values()})

app = dash.Dash(__name__)

app.layout = html.Div(
    children = [
        html.Div([
            html.Div([
                html.Div(id="info4", children="WhereNow?"),
                html.Div(id="logo", className="logo"),
            ], className="name"),
        ], className = "div5"),

        html.Div(
            children = [

                html.B('Type'),
                dcc.Dropdown(
                    id='q1',
                    value='q1-container',
                    options=[{'label': v, 'value': v} for v in type_],
                    persistence=True,
                    className="dropdown"
                ),
                html.Br(),

                html.B('Distance'),
                dcc.Dropdown(
                    id='q2',
                    value='q2-container',
                    options=[{'label': v, 'value': v} for v in distance],
                    persistence=True,
                    className="dropdown"
                ),
                html.Br(),

                html.B('Budget ($)'),
                dcc.Dropdown(
                    id='q3',
                    value='q3-container',
                    options=[{'label': v, 'value': v} for v in budget_],
                    persistence=True,
                    className="dropdown"
                ),
                html.Br(),

                html.B(' '),
                html.Button('Submit', id='submit-val', n_clicks=0, className="button1"),
                html.Br(),
            ],
            className="div2"
        ),
        html.Div([
            html.Iframe(id='map', srcDoc=open("map.html", 'r').read(), className = 'map')
        ]),
        html.Div(id='info', children='Powered by Sona Hakobyan, Anna Manasyan, and Ararat Kazarian for learning purposes.', className="div4"),
        html.Div(
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in weather],
                data = weather.to_dict('records'),
                style_as_list_view=True,
                style_data={ 'border': '1px solid blue' },
                style_header={ 'border': '1px solid blue' },
            ), className = "weather"
            ),
    ],
    className="div1"
)

@app.callback(
    Output('map', 'srcDoc'),
    [Input('submit-val', 'n_clicks'), Input('q1', 'value'), Input('q2', 'value'), Input('q3', 'value')]
)

def update_output(n_clicks, type_, distance, budget):

    df = pd.read_excel("data.xlsx")
    my_loc = {'name': 'My location', 'type_': 'Both', 'price': 0, 'lat': g.latlng[0], 'long': g.latlng[1]}
    df = df.append(my_loc, ignore_index=True)

    input_dist = int("".join(re.findall(r'[\d]+', distance)))
    input_bud = int("".join(re.findall(r'[\d]+', budget)))
    my_loc = geocoder.ip('me').latlng
    df["budget"] = df.price + [int(((my_loc[0] - df.lat.tolist()[i]) ** 2 + (my_loc[1] - df.long.tolist()[i]) ** 2) ** (1 / 2) * 100) * 0.4 for i in range(df.shape[0])]

    if type_ == "Passive":
        def passive(df):

            df = df.loc[df.type_.isin(["Passive", "Both", "Hotel"])]
            g = geocoder.ip('me')
            mapp = folium.Map(location=g.latlng, zoom_start=11)
            markers = ''

            for i in range(df.shape[0]):
                if int(((my_loc[0] - df.lat.tolist()[i]) ** 2 + (my_loc[1] - df.long.tolist()[i]) ** 2) ** (1 / 2) * 100) <= input_dist and df.budget.tolist()[i] <= input_bud:
                    if df.name.tolist()[i] == "My location":
                        markers += f'folium.Marker({df.lat.tolist()[i], df.long.tolist()[i]}, popup="{df.name.tolist()[i]}", tooltip = "{df.name.tolist()[i]}", icon=folium.Icon(color="orange", icon="home")).add_to(mapp)\n'
                    elif df.type_.tolist()[i] == "Hotel":
                        markers += f'folium.Marker({df.lat.tolist()[i], df.long.tolist()[i]}, popup="{df.description.tolist()[i]}", tooltip = "{df.name.tolist()[i]}", icon=folium.Icon(color="green", icon="home")).add_to(mapp)\n'
                    else:
                        markers += f'folium.Marker({df.lat.tolist()[i], df.long.tolist()[i]}, popup="{df.description.tolist()[i]}", tooltip = "{df.name.tolist()[i]}", icon=folium.Icon(color="blue", icon="glyphicon-certificate", prefix="glyphicon")).add_to(mapp)\n'
            exec(markers)
            return mapp
        pf = passive(df)
        pf.save('map.html')

    elif type_ == 'Active':
        def active(df):

            df = df.loc[df.type_.isin(["Active", "Both", "Hotel"])]
            g = geocoder.ip('me')
            mapp = folium.Map(location=g.latlng, zoom_start=11)
            markers = ''

            for i in range(df.shape[0]):
                if int(((my_loc[0] - df.lat.tolist()[i]) ** 2 + (my_loc[1] - df.long.tolist()[i]) ** 2) ** (1 / 2) * 100) <= input_dist and df.budget.tolist()[i] <= input_bud:
                    if df.name.tolist()[i] == "My location":
                        markers += f'folium.Marker({df.lat.tolist()[i], df.long.tolist()[i]}, popup="{df.name.tolist()[i]}", tooltip = "{df.name.tolist()[i]}", icon=folium.Icon(color="orange", icon="home")).add_to(mapp)\n'
                    elif df.type_.tolist()[i] == "Hotel":
                        markers += f'folium.Marker({df.lat.tolist()[i], df.long.tolist()[i]}, popup="{df.description.tolist()[i]}", tooltip = "{df.name.tolist()[i]}", icon=folium.Icon(color="green", icon="home")).add_to(mapp)\n'
                    else:
                        markers += f'folium.Marker({df.lat.tolist()[i], df.long.tolist()[i]}, popup="{df.description.tolist()[i]}", tooltip = "{df.name.tolist()[i]}", icon=folium.Icon(color="red", icon="glyphicon-certificate", prefix="glyphicon")).add_to(mapp)\n'
            exec(markers)
            return mapp

        pf = active(df)
        pf.save('map.html')

    elif type_ == "Both":
        def both(df):

            df1 = df.loc[df.type_.isin(["Passive", "Both", "Hotel"])]
            df2 = df.loc[df.type_ == "Active"]
            g = geocoder.ip('me')
            mapp = folium.Map(location=g.latlng, zoom_start=11)
            markers = ''

            for i in range(df1.shape[0]):
                if int(((my_loc[0] - df1.lat.tolist()[i]) ** 2 + (my_loc[1] - df1.long.tolist()[i]) ** 2) ** (1 / 2) * 100) <= input_dist and df1.budget.tolist()[i] <= input_bud:
                    if df1.name.tolist()[i] == "My location":
                        markers += f'folium.Marker({df1.lat.tolist()[i], df1.long.tolist()[i]}, popup="{df1.name.tolist()[i]}", tooltip = "{df1.name.tolist()[i]}", icon=folium.Icon(color="orange", icon="home")).add_to(mapp)\n'
                    elif df1.type_.tolist()[i] == "Hotel":
                        markers += f'folium.Marker({df1.lat.tolist()[i], df1.long.tolist()[i]}, popup="{df1.description.tolist()[i]}", tooltip = "{df1.name.tolist()[i]}", icon=folium.Icon(color="green", icon="home")).add_to(mapp)\n'
                    else:
                        markers += f'folium.Marker({df1.lat.tolist()[i], df1.long.tolist()[i]}, popup="{df1.description.tolist()[i]}", tooltip = "{df1.name.tolist()[i]}", icon=folium.Icon(color="blue", icon="glyphicon-certificate", prefix="glyphicon")).add_to(mapp)\n'
            for i in range(df2.shape[0]):
                if int(((my_loc[0] - df2.lat.tolist()[i]) ** 2 + (my_loc[1] - df2.long.tolist()[i]) ** 2) ** (1 / 2) * 100) <= input_dist and df2.budget.tolist()[i] <= input_bud:
                    markers += f'folium.Marker({df2.lat.tolist()[i], df2.long.tolist()[i]}, popup="{df2.name.tolist()[i]}", tooltip = "{df2.name.tolist()[i]}", icon=folium.Icon(color="red", icon="glyphicon-certificate", prefix="glyphicon")).add_to(mapp)\n'
            exec(markers)
            return mapp
        pf = both(df)
        pf.save('map.html')

    if n_clicks is None:
        return dash.no_update
    else:
        return open('map.html', 'r').read()

if __name__ == '__main__':
    app.run_server(debug=True)
