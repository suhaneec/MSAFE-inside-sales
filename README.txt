MSafe Inside Sales Dashboard — Streamlit App
============================================

HOW TO RUN
----------

Step 1 — Make sure Python 3.9+ is installed
    python --version

Step 2 — Install dependencies (one time only)
    pip install -r requirements.txt

Step 3 — Run the dashboard
    streamlit run msafe_dashboard.py

Step 4 — Opens automatically at http://localhost:8501

Step 5 — Upload your KIT19 export
    Use the file uploader in the left sidebar.
    Drag and drop any .xls or .xlsx export from KIT19.
    The dashboard refreshes instantly.


FILTERS (sidebar)
-----------------
- Rep          — select one, multiple, or all reps
- Source       — filter by lead source
- Stage        — Active / Won / Lost (or any combination)
- Date range   — filter by lead creation date


TABS
----
1. Leads by Rep & Source   — cross-tab showing how many leads each rep
                              gets from each source, with stacked bar chart
2. Rep Performance         — Active / Won / Lost with Win% and Loss%,
                              colour coded, with wins bar chart
3. CRM Hygiene             — % of leads with key fields filled per rep,
                              red/amber/green heatmap
4. Pipeline & Lost         — Active pipeline breakdown + lost reasons side
                              by side, with donut and bar charts
5. Charts                  — Won vs Lost stacked bars, source volume pie,
                              win rate by rep, raw filtered data + download


DOWNLOADS
---------
Every table has a "Download (CSV)" button.
The raw filtered data in Tab 5 also has a download button.
All downloads respect the current sidebar filters.


UPDATING DATA
-------------
Just upload a new KIT19 export file in the sidebar.
No need to restart the app.


REQUIREMENTS
------------
Python 3.9 or higher
Internet connection not required after install
Works on Windows, Mac, Linux
