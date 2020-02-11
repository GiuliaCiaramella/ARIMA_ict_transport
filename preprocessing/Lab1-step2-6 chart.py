import plotly.graph_objects as go
import pandas as pd


filename1 = "1-2-6-geodf_origins.csv"

df = pd.read_csv(filename1, usecols=['NIL'])
df = df.rename({'NIL': 'origin'}, axis=1)

filename2 = "1-2-6-geodf_dests.csv"
df1 = pd.read_csv(filename2, usecols=['NIL'])
df1 = df1.rename({'NIL': 'destination'}, axis=1)

df = df.join(df1)
df["flag"] = 0
df = df.sort_values(by=['origin', 'destination'])
df_group = df.groupby(['origin', 'destination']).size().sort_values(ascending=False).reset_index(name='count')

number_of_line = 20
sources = []
targets = []
values = []
labels = []

for i in range(number_of_line):
    labelOrg = df_group.iloc[i]['origin']
    labelDes = df_group.iloc[i]['destination']
    value = df_group.iloc[i]['count']
    if labelOrg == labelDes:
        if labelOrg in labels:
            index = labels.index(labelOrg)
            sources.append(index)
            targets.append(index)
            values.append(value)
        else:
            lenLabel = len(labels)
            labels.insert(lenLabel, labelOrg)
            sources.append(lenLabel)
            if labelDes not in labels:
                labels.insert(lenLabel, labelOrg)
                targets.append(lenLabel)
            else:
                index = labels.index(labelOrg)
                targets.append(index)
            values.append(value)
    else:
        if labelOrg in labels:
            index = labels.index(labelOrg)
            sources.append(index)
        else:
            lenLabel = len(labels)
            labels.insert(lenLabel, labelOrg)
            sources.append(lenLabel)

        if labelDes in labels:
            index = labels.index(labelDes)
            targets.append(index)
        else:
            lenLabel = len(labels)
            labels.insert(lenLabel, labelDes)
            targets.append(lenLabel)
        values.append(value)


fig = go.Figure(data=[go.Sankey(
    node=dict(
      pad=15,
      thickness=20,
      line=dict(color="black", width=0.5),
      label=labels,
      color="blue"
    ),
    link=dict(
      source=sources, # indices correspond to labels, eg A1, A2, A2, B1, ...
      target=targets,
      value=values
  ))])

fig.update_layout(title_text="Flow Chart", font_size=10)
fig.show()