import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# All AMCAT score columns in the dataset
# ─────────────────────────────────────────────
ALL_SCORE_COLS = [
    'English', 'Quant', 'Logical', 'WriteX',
    'Automata', 'Automata Fix', 'Computer Prog.',
    'Telecommunications', 'Electrical Engg.', 'Civil Engg.',
    'Mechanical Engg.', 'Data Science', 'Marketing',
    'Human Resources', 'Data Structures', 'Python',
    'C++ Programming', 'Core Java'
]

# Department-relevant subjects for weighted scoring
DEPT_RELEVANT_COLS = {
    'BTECH-CSE':   ['English', 'Quant', 'Logical', 'WriteX', 'Computer Prog.', 'Automata', 'Automata Fix', 'Data Structures'],
    'BTECH-AIDS':  ['English', 'Quant', 'Logical', 'WriteX', 'Computer Prog.', 'Data Science', 'Data Structures', 'Python'],
    'BTECH-ETE':   ['English', 'Quant', 'Logical', 'WriteX', 'Automata', 'Telecommunications'],
    'BTECH-EE':    ['English', 'Quant', 'Logical', 'WriteX', 'Electrical Engg.'],
    'BTECH-CIVIL': ['English', 'Quant', 'Logical', 'WriteX', 'Civil Engg.'],
    'BTECH-MECH':  ['English', 'Quant', 'Logical', 'WriteX', 'Mechanical Engg.'],
    'MBA':         ['English', 'Quant', 'Logical', 'WriteX', 'Marketing', 'Human Resources'],
    'MCA':         ['English', 'Quant', 'Logical', 'WriteX', 'Computer Prog.', 'Data Structures', 'Python', 'Core Java'],
}

# Industry standard thresholds
INDUSTRY_THRESHOLDS = {
    'English': 60, 'Quant': 55, 'Logical': 55, 'WriteX': 60,
    'Computer Prog.': 60, 'Data Structures': 65, 'Python': 60,
    'Data Science': 60, 'Automata': 55, 'Automata Fix': 50,
    'Telecommunications': 50, 'Electrical Engg.': 55,
    'Civil Engg.': 50, 'Mechanical Engg.': 50,
    'Marketing': 55, 'Human Resources': 55,
    'C++ Programming': 55, 'Core Java': 55
}

# Talent tier thresholds (based on dept-relevant score)
TALENT_TIERS = {
    'Diamond 💎': (80, 100),
    'Gold 🥇':    (65, 80),
    'Silver 🥈':  (50, 65),
    'Bronze 🥉':  (0, 50),
}

DEPT_COLORS = {
    'BTECH-CSE':   '#6366f1',
    'BTECH-AIDS':  '#10b981',
    'BTECH-ETE':   '#f59e0b',
    'BTECH-EE':    '#ef4444',
    'BTECH-CIVIL': '#8b5cf6',
    'BTECH-MECH':  '#06b6d4',
    'MBA':         '#f97316',
    'MCA':         '#ec4899',
}


class AMCATAnalyzer:
    def __init__(self, data_path='amcat-raw-data.csv'):
        import io
        if isinstance(data_path, str):
            if data_path.lower().endswith(('.xlsx', '.xls')):
                self.df = pd.read_excel(data_path)
            else:
                self.df = pd.read_csv(data_path)
        else:
            # StringIO / BytesIO fallback
            try:
                self.df = pd.read_csv(data_path)
            except Exception:
                data_path.seek(0)
                self.df = pd.read_excel(data_path)
        self._clean_data()
        self.branches = sorted(self.df['Branch'].dropna().unique().tolist())
        self.batches = sorted(self.df['Batch'].dropna().unique().tolist())
        self.score_columns = ALL_SCORE_COLS
        self._compute_scores()

    # ──────────────────────────────────────────
    # DATA CLEANING
    # ──────────────────────────────────────────
    def _clean_data(self):
        # Standardize column names
        self.df.columns = self.df.columns.str.strip()
        # Convert score columns to numeric (treat missing as NaN, not 0!)
        for col in ALL_SCORE_COLS:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        # Clean branch names
        self.df['Branch'] = self.df['Branch'].str.strip()
        # Convert Batch to int where possible
        self.df['Batch'] = pd.to_numeric(self.df['Batch'], errors='coerce')

    def _compute_scores(self):
        """Compute overall + dept-relevant placement readiness scores."""
        # Overall score: mean of non-null subject scores (ignore domain-irrelevant 0s)
        self.df['Overall_Score'] = self.df[ALL_SCORE_COLS].mean(axis=1, skipna=True)

        # Department-specific readiness score
        def compute_dept_score(row):
            dept = row.get('Branch', None)
            if dept and dept in DEPT_RELEVANT_COLS:
                cols = [c for c in DEPT_RELEVANT_COLS[dept] if c in self.df.columns]
                vals = [row[c] for c in cols if pd.notna(row[c])]
                return np.mean(vals) if vals else np.nan
            return row.get('Overall_Score', np.nan)

        self.df['Dept_Score'] = self.df.apply(compute_dept_score, axis=1)

        # Core aptitude: Eng + Quant + Logical average
        core_cols = ['English', 'Quant', 'Logical']
        self.df['Core_Aptitude'] = self.df[core_cols].mean(axis=1, skipna=True)

        # Percentile within department
        self.df['Dept_Percentile'] = self.df.groupby('Branch')['Dept_Score'].rank(pct=True) * 100

        # Talent tier
        def get_tier(score):
            if pd.isna(score):
                return 'Unranked'
            for tier, (lo, hi) in TALENT_TIERS.items():
                if lo <= score < hi:
                    return tier
            return 'Bronze 🥉'

        self.df['Talent_Tier'] = self.df['Dept_Score'].apply(get_tier)

        # Placement readiness flag (dept score >= 50)
        self.df['Placement_Ready'] = self.df['Dept_Score'] >= 50

    # ──────────────────────────────────────────
    # BASIC GETTERS
    # ──────────────────────────────────────────
    def get_branch_data(self, branch=None, batch=None):
        data = self.df.copy()
        if branch and branch != 'All Departments':
            if isinstance(branch, list):
                data = data[data['Branch'].isin(branch)]
            else:
                data = data[data['Branch'] == branch]
        if batch and batch != 'All Batches':
            if isinstance(batch, list):
                data = data[data['Batch'].isin(batch)]
            else:
                data = data[data['Batch'] == batch]
        return data

    def get_relevant_cols(self, branch):
        """Return the domain-relevant columns for a given dept."""
        return DEPT_RELEVANT_COLS.get(branch, ['English', 'Quant', 'Logical', 'WriteX'])

    # ──────────────────────────────────────────
    # SUMMARY STATS
    # ──────────────────────────────────────────
    def summary_stats(self, branch=None, batch=None):
        data = self.get_branch_data(branch, batch)
        n = len(data)
        return {
            'Total Students':        n,
            'Avg Dept Score':        round(data['Dept_Score'].mean(), 1),
            'Avg Core Aptitude':     round(data['Core_Aptitude'].mean(), 1),
            'Top Performers (>70%)': int((data['Dept_Score'] > 70).sum()),
            'Placement Ready (≥50)': int(data['Placement_Ready'].sum()),
            'Placement Ready %':     round(data['Placement_Ready'].mean() * 100, 1),
            'Diamond Tier':          int((data['Talent_Tier'] == 'Diamond 💎').sum()),
            'Gold Tier':             int((data['Talent_Tier'] == 'Gold 🥇').sum()),
            'Silver Tier':           int((data['Talent_Tier'] == 'Silver 🥈').sum()),
            'Bronze Tier':           int((data['Talent_Tier'] == 'Bronze 🥉').sum()),
        }

    # ──────────────────────────────────────────
    # TOP / BOTTOM PERFORMERS
    # ──────────────────────────────────────────
    def top_performers(self, by='Dept_Score', n=15, branch=None, batch=None):
        data = self.get_branch_data(branch, batch)
        cols = ['fullName', 'Branch', 'Batch', 'Dept_Score', 'Core_Aptitude', 'Talent_Tier', 'Dept_Percentile']
        cols = [c for c in cols if c in data.columns]
        return (data[cols]
                .sort_values(by=by, ascending=False)
                .head(n)
                .reset_index(drop=True))

    def bottom_performers(self, n=20, branch=None, batch=None):
        data = self.get_branch_data(branch, batch)
        cols = ['fullName', 'Branch', 'Batch', 'Dept_Score', 'Core_Aptitude', 'Talent_Tier']
        cols = [c for c in cols if c in data.columns]
        return (data[cols]
                .sort_values('Dept_Score', ascending=True)
                .head(n)
                .reset_index(drop=True))

    def search_student(self, query):
        q = query.strip().lower()
        mask = (
            self.df['fullName'].str.lower().str.contains(q, na=False) |
            self.df['UniversityRollNumber'].str.lower().str.contains(q, na=False)
        )
        return self.df[mask]

    # ──────────────────────────────────────────
    # DEPARTMENT COMPETITIVENESS
    # ──────────────────────────────────────────
    def branch_competitiveness(self, batch=None):
        rows = []
        for branch in self.branches:
            data = self.get_branch_data(branch, batch)
            if len(data) == 0:
                continue
            rows.append({
                'Branch':             branch,
                'Students':           len(data),
                'Avg_Dept_Score':     round(data['Dept_Score'].mean(), 1),
                'Avg_Core_Aptitude':  round(data['Core_Aptitude'].mean(), 1),
                'Top_Performer_%':    round((data['Dept_Score'] > 70).mean() * 100, 1),
                'Placement_Ready_%':  round(data['Placement_Ready'].mean() * 100, 1),
                'Diamond_%':          round((data['Talent_Tier'] == 'Diamond 💎').mean() * 100, 1),
                'Consistency':        round(data['Dept_Score'].std(), 1),
            })
        return pd.DataFrame(rows).set_index('Branch')

    # ──────────────────────────────────────────
    # SUBJECT-LEVEL ANALYSIS
    # ──────────────────────────────────────────
    def subject_avg_by_dept(self):
        """Returns a DataFrame: rows=depts, cols=subjects, values=avg score."""
        result = {}
        for branch in self.branches:
            data = self.get_branch_data(branch)
            relevant = self.get_relevant_cols(branch)
            row = {}
            for col in relevant:
                if col in data.columns:
                    row[col] = round(data[col].mean(skipna=True), 1)
            result[branch] = row
        return pd.DataFrame(result).T

    def skill_gap_analysis(self, branch=None, batch=None):
        data = self.get_branch_data(branch, batch)
        relevant = self.get_relevant_cols(branch) if branch and branch != 'All Departments' else list(INDUSTRY_THRESHOLDS.keys())
        gaps = {}
        for subject in relevant:
            if subject in data.columns and subject in INDUSTRY_THRESHOLDS:
                avg = data[subject].mean(skipna=True)
                if pd.notna(avg):
                    gaps[subject] = {
                        'avg':       round(avg, 1),
                        'threshold': INDUSTRY_THRESHOLDS[subject],
                        'gap':       round(INDUSTRY_THRESHOLDS[subject] - avg, 1)
                    }
        return gaps

    def subject_correlation_matrix(self, branch=None, batch=None):
        data = self.get_branch_data(branch, batch)
        relevant = self.get_relevant_cols(branch) if branch and branch != 'All Departments' else ['English', 'Quant', 'Logical', 'WriteX', 'Computer Prog.', 'Data Structures']
        cols = [c for c in relevant if c in data.columns]
        return data[cols].corr()

    # ──────────────────────────────────────────
    # BATCH COMPARISON
    # ──────────────────────────────────────────
    def batch_comparison(self, branch=None):
        rows = []
        for batch in self.batches:
            data = self.get_branch_data(branch, batch)
            if len(data) == 0:
                continue
            rows.append({
                'Batch':              int(batch),
                'Students':          len(data),
                'Avg_Score':         round(data['Dept_Score'].mean(), 1),
                'Placement_Ready_%': round(data['Placement_Ready'].mean() * 100, 1),
                'Top_Performers':    int((data['Dept_Score'] > 70).sum()),
                'Avg_English':       round(data['English'].mean(skipna=True), 1),
                'Avg_Quant':         round(data['Quant'].mean(skipna=True), 1),
                'Avg_Logical':       round(data['Logical'].mean(skipna=True), 1),
            })
        return pd.DataFrame(rows)

    # ──────────────────────────────────────────
    # CLUSTERING
    # ──────────────────────────────────────────
    def student_clustering(self, branch=None, batch=None, n_clusters=4):
        data = self.get_branch_data(branch, batch).copy()
        features = ['English', 'Quant', 'Logical', 'Core_Aptitude']
        data_clean = data[features].fillna(data[features].median())
        if len(data_clean) < n_clusters:
            n_clusters = max(2, len(data_clean))
        scaler = StandardScaler()
        scaled = scaler.fit_transform(data_clean)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        data = data.copy()
        data['Cluster'] = kmeans.fit_predict(scaled).astype(str)
        cluster_labels = {
            '0': 'Cluster A', '1': 'Cluster B',
            '2': 'Cluster C', '3': 'Cluster D'
        }
        data['Cluster_Label'] = data['Cluster'].map(cluster_labels).fillna('Cluster X')
        return data

    # ──────────────────────────────────────────
    # TALENT TIER DISTRIBUTION
    # ──────────────────────────────────────────
    def talent_tier_distribution(self, branch=None, batch=None):
        data = self.get_branch_data(branch, batch)
        counts = data['Talent_Tier'].value_counts().reset_index()
        counts.columns = ['Tier', 'Count']
        return counts

    # ──────────────────────────────────────────
    # RECOMMENDATIONS
    # ──────────────────────────────────────────
    def generate_recommendations(self, branch=None, batch=None):
        data = self.get_branch_data(branch, batch)
        recs = []
        gaps = self.skill_gap_analysis(branch, batch)

        critical = [(s, v) for s, v in gaps.items() if v['gap'] > 15]
        moderate = [(s, v) for s, v in gaps.items() if 5 < v['gap'] <= 15]

        for s, v in sorted(critical, key=lambda x: -x[1]['gap'])[:3]:
            recs.append(f"🔴 **CRITICAL — {s}**: Average is {v['avg']}, needs {v['threshold']} (gap: {v['gap']} pts). Conduct intensive workshops immediately.")

        for s, v in sorted(moderate, key=lambda x: -x[1]['gap'])[:3]:
            recs.append(f"🟡 **FOCUS — {s}**: Average is {v['avg']}, target {v['threshold']} (gap: {v['gap']} pts). Incorporate mock tests in curriculum.")

        ready_pct = data['Placement_Ready'].mean() * 100
        if ready_pct < 40:
            recs.append(f"🔴 Only **{ready_pct:.0f}%** students are placement-ready. Emergency intervention needed.")
        elif ready_pct < 60:
            recs.append(f"🟡 **{ready_pct:.0f}%** students are placement-ready. Targeted coaching for mid-tier students recommended.")
        else:
            recs.append(f"🟢 **{ready_pct:.0f}%** students are placement-ready. Focus on pushing Silver → Gold tier students.")

        diamond_pct = (data['Talent_Tier'] == 'Diamond 💎').mean() * 100
        if diamond_pct < 5:
            recs.append(f"💎 Only **{diamond_pct:.1f}%** Diamond-tier students. Introduce advanced competitive programming / case study tracks.")

        return recs

    # ──────────────────────────────────────────
    # EXPORT DATA
    # ──────────────────────────────────────────
    def export_presentation_data(self, branch=None, batch=None):
        data = self.get_branch_data(branch, batch)
        return {
            'summary_stats':     self.summary_stats(branch, batch),
            'top_performers':    self.top_performers(n=20, branch=branch, batch=batch),
            'branch_comparison': self.branch_competitiveness(batch) if not branch or branch == 'All Departments' else None,
            'recommendations':   self.generate_recommendations(branch, batch),
            'talent_distribution': self.talent_tier_distribution(branch, batch),
        }

    def export_to_excel(self, branch=None, batch=None):
        """Export multi-sheet Excel for presentation."""
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            summary = pd.DataFrame(
                list(self.summary_stats(branch, batch).items()),
                columns=['Metric', 'Value']
            )
            summary.to_excel(writer, sheet_name='Summary', index=False)

            self.branch_competitiveness(batch).to_excel(writer, sheet_name='Dept Comparison')
            self.top_performers(n=50, branch=branch, batch=batch).to_excel(writer, sheet_name='Top 50 Students', index=False)
            self.bottom_performers(n=30, branch=branch, batch=batch).to_excel(writer, sheet_name='At-Risk Students', index=False)

            gap_data = self.skill_gap_analysis(branch, batch)
            gap_df = pd.DataFrame(gap_data).T.reset_index()
            gap_df.columns = ['Subject', 'Avg Score', 'Industry Threshold', 'Gap']
            gap_df.to_excel(writer, sheet_name='Skill Gaps', index=False)

            raw = self.get_branch_data(branch, batch)
            raw.to_excel(writer, sheet_name='Raw Data', index=False)

        output.seek(0)
        return output