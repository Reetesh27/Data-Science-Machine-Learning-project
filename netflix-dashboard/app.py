import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt

# Set up the page
st.set_page_config(page_title="Netflix Dashboard", page_icon="🎬", layout="wide")

# Title
st.title("🎬 Netflix Content Analysis Dashboard")
st.markdown("Analyzing Netflix's movie and TV show collection")

# Load and clean data (using our previous functions)


def create_sample_data():
    """Create sample data as fallback"""
    st.warning("⚠️ Using sample data because CSV file couldn't be loaded")
    sample_data = {
        'show_id': [f's{i}' for i in range(1, 21)],
        'type': ['Movie'] * 10 + ['TV Show'] * 10,
        'title': [f'Movie {i}' for i in range(1, 11)] + [f'TV Show {i}' for i in range(1, 11)],
        'country': ['United States'] * 8 + ['United Kingdom'] * 5 + ['India'] * 4 + ['Canada'] * 3,
        'release_year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022] * 3,
        'rating': ['TV-MA', 'TV-14', 'PG-13', 'R', 'PG'] * 4,
        'duration': ['120 min', '110 min', '95 min', '130 min'] * 5,
        'listed_in': ['Dramas', 'Comedies', 'Thrillers', 'Action'] * 5,
    }
    return pd.DataFrame(sample_data)

@st.cache_data
def load_data():
    """Try multiple methods to load the CSV file"""
    st.info("🔄 Attempting to load your Netflix CSV file...")

    # Method 3: Try with error handling for bad lines
    try:
        st.write("🛠️ Trying with error handling...")
        df = pd.read_csv('https://github.com/Reetesh27/Data-Science-Machine-Learning-project/blob/main/netflix-dashboard/netflix_titles.csv', on_bad_lines='skip', encoding='latin-1')
        st.success("✅ CSV loaded successfully with error handling!")
        return df
    except Exception as e:
        st.warning(f"❌ Error handling method failed: {str(e)[:100]}...")
    
    # Method 4: Manual CSV parsing to handle problematic lines
    try:
        st.write("🔍 Trying manual CSV parsing...")
        with open('https://github.com/Reetesh27/Data-Science-Machine-Learning-project/blob/main/netflix-dashboard/netflix_titles.csv', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) == 0:
            st.error("❌ CSV file is empty")
            return create_sample_data()
        
        # Get headers
        headers = lines[0].strip().split(',')
        data = []
        skipped_lines = []
        
        # Process each line
        for i, line in enumerate(lines[1:], 1):
            line = line.strip()
            if not line:
                continue
                
            # Count commas to check if line has right number of fields
            comma_count = line.count(',')
            if comma_count == len(headers) - 1:
                # Line has correct number of fields
                values = line.split(',')
                data.append(values)
            else:
                # Problematic line - skip it
                skipped_lines.append(i + 1)
                continue
        
        if skipped_lines:
            st.warning(f"⚠️ Skipped {len(skipped_lines)} problematic lines: {skipped_lines[:5]}...")
        
        if data:
            df = pd.DataFrame(data, columns=headers)
            st.success(f"✅ Manual parsing successful! Loaded {len(df)} records")
            return df
        else:
            st.error("❌ No valid data could be parsed from CSV")
            return create_sample_data()
            
    except Exception as e:
        st.error(f"❌ Manual parsing failed: {str(e)[:100]}...")
    
    # Method 5: Try reading with Python's csv module
    try:
        st.write("🐍 Trying with Python's csv module...")
        import csv
        
        with open('https://github.com/Reetesh27/Data-Science-Machine-Learning-project/blob/main/netflix-dashboard/netflix_titles.csv', 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            data = list(csv_reader)
        
        if len(data) > 1:
            headers = data[0]
            # Filter out rows with different number of columns
            valid_data = [row for row in data[1:] if len(row) == len(headers)]
            df = pd.DataFrame(valid_data, columns=headers)
            st.success(f"✅ CSV module successful! Loaded {len(df)} records")
            return df
    except Exception as e:
        st.error(f"❌ CSV module failed: {str(e)[:100]}...")
    
    # Final fallback
    st.error("❌ All CSV loading methods failed. Using sample data.")
    return create_sample_data()

def clean_data(df):
    clean_df = df.copy()
    
    clean_df['cast'] = clean_df['cast'].fillna('No cast information')
    clean_df['director'] = clean_df['director'].fillna('No director information')
    clean_df['year_added'] = pd.to_datetime(clean_df['date_added'], errors='coerce').dt.year
    clean_df['year_added'] = clean_df['year_added'].fillna(clean_df['release_year'])
    return clean_df

df = load_data()
df_clean = clean_data(df)

# SIDEBAR - Filters
st.sidebar.header("🔍 Filters")

# Type filter
content_type = st.sidebar.multiselect(
    "Select Content Type:",
    options=df_clean['type'].unique(),
    default=df_clean['type'].unique()
)

# Country filter
countries = st.sidebar.multiselect(
    "Select Countries:",
    options=sorted(df_clean['country'].unique()),
    default=[]
)

# Year range filter
min_year = int(df_clean['release_year'].min())
max_year = int(df_clean['release_year'].max())
year_range = st.sidebar.slider(
    "Select Release Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Apply filters
filtered_df = df_clean.copy()
if content_type:
    filtered_df = filtered_df[filtered_df['type'].isin(content_type)]
if countries:
    filtered_df = filtered_df[filtered_df['country'].isin(countries)]
filtered_df = filtered_df[
    (filtered_df['release_year'] >= year_range[0]) & 
    (filtered_df['release_year'] <= year_range[1])
]

# MAIN DASHBOARD
# Key metrics
st.subheader("📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Filtered Content", len(filtered_df))
with col2:
    st.metric("Movies", len(filtered_df[filtered_df['type'] == 'Movie']))
with col3:
    st.metric("TV Shows", len(filtered_df[filtered_df['type'] == 'TV Show']))
with col4:
    st.metric("Countries", filtered_df['country'].nunique())

# Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Content Type Distribution")
    type_counts = filtered_df['type'].value_counts()
    fig = px.pie(values=type_counts.values, names=type_counts.index)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top 10 Countries")
    country_counts = filtered_df['country'].value_counts().head(10)
    fig = px.bar(x=country_counts.values, y=country_counts.index, orientation='h')
    st.plotly_chart(fig, use_container_width=True)


# Additional Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Content Added Over Time")
    yearly_data = filtered_df['year_added'].value_counts().sort_index()
    fig = px.line(x=yearly_data.index, y=yearly_data.values, 
                  labels={'x': 'Year', 'y': 'Number of Titles Added'})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Content Ratings")
    rating_counts = filtered_df['rating'].value_counts()
    fig = px.bar(x=rating_counts.index, y=rating_counts.values,
                 labels={'x': 'Rating', 'y': 'Count'})
    st.plotly_chart(fig, use_container_width=True)

# Top genres
st.subheader("🎭 Top Genres")
genres_list = []
for genres in filtered_df['listed_in'].dropna():
    genres_list.extend([genre.strip() for genre in genres.split(',')])

genre_counts = pd.Series(genres_list).value_counts().head(10)
fig = px.bar(x=genre_counts.values, y=genre_counts.index, orientation='h',
             title="Most Common Genres")
st.plotly_chart(fig, use_container_width=True)

# Sample of the filtered data
st.subheader("📋 Sample of Filtered Content")
st.dataframe(filtered_df[['title', 'type', 'country', 'release_year', 'rating']].head(10))

# Footer
st.markdown("---")

st.markdown("Built with ❤️ using Streamlit | Data Source: Kaggle Netflix Dataset")




