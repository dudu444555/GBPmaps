import streamlit as st
import pandas as pd
import plotly.express as px
import us  # pip install us

st.set_page_config(layout="wide")

# Load CSVs
may_df = pd.read_csv("YouGov Data - May.csv")
june_df = pd.read_csv("YouGov Data - June.csv")
july_df = pd.read_csv("YouGov Data - July.csv")

# Add month column
may_df["Month"] = "May"
june_df["Month"] = "June"
july_df["Month"] = "July"

# Combine
df = pd.concat([may_df, june_df, july_df])

"""#Geographic visualizations of US states

These visualizations will create interactive maps of the US states, with breakdowns of votes on different criteria.

These visualizations are for a single month at a time only.
"""

# US state name to abbreviation mapping
us_state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
}

# Add state abbreviations
df['inputstate'] = df['inputstate'].map(us_state_abbrev)

# Visualize who voted for the "Grand Bargain" vs. the "Current Direction" by US state

# 1. Map Yes/No to readable labels
df['GBP Label'] = df['Grand Bargain or Current Direction?']

# 2. Add state abbreviations
df['State Abbr'] = df['inputstate'].apply(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else None)

# 3. Make labels categorical to control legend order
df['GBP Label'] = pd.Categorical(df['GBP Label'], categories=['Grand Bargain', 'Current Direction'], ordered=True)

# Month toggle
month = st.radio("Select Month", ["May", "June", "July"], horizontal=True)
month_df = df[df["Month"] == month]

# 4. Compute % choosing Grand Bargain and total participants per state
support_counts = (
    month_df.groupby(['State Abbr', 'GBP Label'])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

support_counts['Total Participants'] = support_counts['Grand Bargain'] + support_counts['Current Direction']
support_counts['Percent'] = support_counts['Grand Bargain'] / support_counts['Total Participants']
support_counts['Grand Bargain %'] = (
    (support_counts['Percent'] * 100)
    .fillna(0)              # handle states with no data
    .round(0)
    .astype(int)
    .astype(str) + '%'
)

# 5. Plot choropleth
fig = px.choropleth(
    support_counts,
    locations='State Abbr',
    locationmode='USA-states',
    scope="usa",
    color='Percent',
    hover_name='State Abbr',
    hover_data={
        'Percent': False,
        'Grand Bargain %': True,
        'Total Participants': True
    },
    color_continuous_scale='RdYlGn',
    labels={
        'Percent': 'Grand Bargain',
        'Grand Bargain %': 'The Grand Bargain',
        'Total Participants': 'Total Respondents'
    },
    title="Which would you choose: The Grand Bargain or the country's current direction?"
)

fig.update_layout(
    geo=dict(bgcolor='rgba(0,0,0,0)'),
    plot_bgcolor='white',
    coloraxis_colorbar=dict(
        orientation='h',
        yanchor='bottom',
        y=-0.3,
        xanchor='center',
        x=0.5,
        title_side='right'   # ✅ puts the title on the right
    )
)
st.plotly_chart(fig, use_container_width=True)
