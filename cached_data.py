@st.cache_data
def get_profile_dataset(number_of_items: int = 20, seed: int = 0) -> pd.DataFrame:
    new_data = []


    for i in range(number_of_items):
        new_data.append(
            {
                "Query": np.random.choice(100),
                "Date": "2021-01-01",
                "Results": 0,
                "JSON": "{}",
            }
        )

    profile_df = pd.DataFrame(new_data)
    return profile_df


column_configuration = {
    "Query": st.column_config.TextColumn(
        "Query", help="The name of the user", max_chars=100, width="medium"
    ),
    "Date": st.column_config.LineChartColumn(
        "Activity (1 year)",
        help="The user's activity over the last 1 year",
        width="large",
        y_min=0,
        y_max=100,
    ),
    "JSON": st.column_config.BarChartColumn(
        "Activity (daily)",
        help="The user's activity in the last 25 days",
        width="medium",
        y_min=0,
        y_max=1,
    ),
}

select, compare = st.tabs(["Select members", "Compare selected"])

with select:
    st.header("All members")

    df = get_profile_dataset()

    event = st.dataframe(
        df,
        column_config=column_configuration,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
    )

    st.header("Selected members")
    people = event.selection.rows
    filtered_df = df.iloc[people]
    st.dataframe(
        filtered_df,
        column_config=column_configuration,
        use_container_width=True,
    )

#horizontal container
with st.container():
    #4 columns
    col1, col2, col3, col4 = st.columns(4)

    #a button in each column
    with col1:
        st.button('Merge',icon="🥪", use_container_width=True)
    with col2:
        st.button('Visualize',icon="👁️", use_container_width=True)
    with col3:
        st.button('Export',icon="⬇️" ,use_container_width=True)
    with col4:
        st.button('Delete', use_container_width=True, type='primary', icon="🚨")    
