# Core Pkgs
import streamlit as st
import pandas as pd

# DB Mgmt
import sqlite3
from contextlib import closing
from pathlib import Path


# Database path relative to app.py.
DB_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "world.sqlite"
)


# Fxn Make Execution
def sql_executor(raw_code):
    # Avoid creating an empty database if the file is missing.
    if not DB_PATH.is_file():
        raise FileNotFoundError(
            "Database not found. Place world.sqlite "
            "inside the data folder beside app.py."
        )

    # Use a fresh connection for each execution.
    with closing(sqlite3.connect(DB_PATH, timeout=15)) as conn:
        # Commit successful changes and roll back failed operations.
        with conn:
            c = conn.cursor()
            c.execute(raw_code)

            if c.description is not None:
                columns = [
                    column[0] for column in c.description
                ]

                data = c.fetchall()

                return data, columns, None

            # Statements that do not return a results table.
            return [], [], c.rowcount


city = [
    "ID",
    "Name",
    "CountryCode",
    "District",
    "Population",
]

country = [
    "Code",
    "Name",
    "Continent",
    "Region",
    "SurfaceArea",
    "IndepYear",
    "Population",
    "LifeExpectancy",
    "GNP",
    "GNPOld",
    "LocalName",
    "GovernmentForm",
    "HeadOfState",
    "Capital",
    "Code2",
]

countrylanguage = [
    "CountryCode",
    "Language",
    "IsOfficial",
    "Percentage",
]


def main():
    # Heading with a blue and teal background.
    st.markdown(
        """
        <div style="
            background:linear-gradient(135deg, #1e3a8a, #0f766e);
            padding:25px;
            border-radius:12px;
            text-align:center;
            margin-bottom:25px;">
            <h1 style="
                color:white;
                font-size:40px;
                margin:0;">
                SQL Playground
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu = ["Home", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home Page")

        # Columns/Layout
        col1, col2 = st.columns(2)

        with col1:
            with st.form(key="query_form"):
                raw_code = st.text_area(
                    "SQL Code Here",
                    value="SELECT * FROM city LIMIT 10;",
                    height=200,
                )

                submit_code = st.form_submit_button("Execute")

            st.caption(
                "Run one SQL statement at a time. "
                "Successful INSERT, UPDATE, DELETE, and table changes "
                "are saved to the database."
            )

            # Table of Info
            with st.expander("Table Info"):
                table_info = {
                    "city": city,
                    "country": country,
                    "countrylanguage": countrylanguage,
                }

                st.json(table_info)

        # Results Layouts
        with col2:
            if submit_code:
                if not raw_code.strip():
                    st.warning("Enter an SQL statement.")
                    return

                st.info("Query Submitted")
                st.code(raw_code, language="sql")

                try:
                    # Results
                    query_results, columns, affected_rows = (
                        sql_executor(raw_code.strip())
                    )

                except FileNotFoundError as exc:
                    st.error(str(exc))

                except sqlite3.Error as exc:
                    st.error(f"SQL error: {exc}")

                else:
                    if columns:
                        st.success(
                            f"Returned {len(query_results):,} row(s)."
                        )

                        with st.expander("Results"):
                            st.write(query_results)

                        with st.expander(
                            "Pretty Table",
                            expanded=True,
                        ):
                            query_df = pd.DataFrame(
                                query_results,
                                columns=columns,
                            )

                            st.dataframe(query_df)

                    elif (
                        affected_rows is not None
                        and affected_rows >= 0
                    ):
                        st.success(
                            "Statement executed successfully. "
                            f"Rows affected: {affected_rows:,}."
                        )

                    else:
                        st.success(
                            "Statement executed successfully."
                        )

    else:
        st.subheader("About")

        st.write(
            "Practise SQL using the World database. "
            "Explore cities, countries, and languages, "
            "execute SQL statements, and view results as tables."
        )

        st.write("Developed by John Bernard Conteh.")


if __name__ == "__main__":
    main()
