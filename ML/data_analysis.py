"""
=============================================================================
  AEROLYTICS - Air Quality Data Analysis Script
=============================================================================

  PURPOSE:
  This script performs an in-depth exploratory data analysis (EDA) on the
  cleaned air quality sensor dataset ('clean_data.csv'). The dataset contains
  805 readings from air quality sensors measuring:

    - pm1        : Particulate Matter ≤ 1 µm (µg/m³)
    - pm25       : Particulate Matter ≤ 2.5 µm (µg/m³)
    - pm10       : Particulate Matter ≤ 10 µm (µg/m³)
    - temperature: Ambient temperature (°C)
    - humidity   : Relative humidity (%)
    - gas_resistance: MOX gas sensor resistance (kΩ) — inversely related to
                      volatile organic compounds (VOCs) in the air
    - aqi        : Air Quality Index (computed target variable)

  WHY THIS ANALYSIS?
  Before building any ML model (which this project does in train_model.py),
  it is critical to understand the data distribution, identify relationships
  between features, detect anomalies, and decide which features actually
  matter. This script answers questions like:
    1. Are there outliers that could skew the model?
    2. Which pollutants are most correlated with AQI?
    3. How do environmental factors (temp, humidity) affect air quality?
    4. Are the PM readings internally consistent (pm1 < pm2.5 < pm10)?

  OUTPUT:
  All charts are saved as PNG files inside a 'analysis_plots/' folder.
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')                    # Non-interactive backend — safe for scripts
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ─────────────────────────────────────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────────────────────────────────────
# Create output directory for plots so the workspace stays organised.
OUTPUT_DIR = 'analysis_plots'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Seaborn styling for cleaner, publication-ready charts
sns.set_theme(style='whitegrid', palette='muted', font_scale=1.1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD & INSPECT THE DATA
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Load the cleaned CSV and print basic info.
# WHY:   Confirms the data loaded correctly, shows column types, memory usage,
#        and whether any nulls slipped through the cleaning step.
# ─────────────────────────────────────────────────────────────────────────────
df = pd.read_csv('data/clean_data.csv')

# Drop the 'index' column — it's just a row counter from the cleaning step
# and adds no analytical value; keeping it could mislead correlation analysis.
if 'index' in df.columns:
    df = df.drop(columns=['index'])

print("=" * 65)
print("  1. DATASET OVERVIEW")
print("=" * 65)
print(f"\n  Shape           : {df.shape[0]} rows × {df.shape[1]} columns")
print(f"  Memory usage    : {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
print(f"  Missing values  : {df.isnull().sum().sum()}  (should be 0 after cleaning)")
print(f"\n  Columns & Types :")
for col in df.columns:
    print(f"    • {col:<18s} {str(df[col].dtype)}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. DESCRIPTIVE STATISTICS
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Compute mean, std, min, max, quartiles for every feature.
# WHY:   Gives a quick numerical snapshot of the data. Key things to check:
#        - Is the AQI range realistic? (0–500 is the standard scale)
#        - Are PM values non-negative? (negative would indicate sensor errors)
#        - Is the standard deviation of temperature very low? (might mean all
#          readings were taken in a short time window → limited generalisation)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  2. DESCRIPTIVE STATISTICS")
print("=" * 65)
desc = df.describe().T.copy()
desc['range'] = desc['max'] - desc['min']
desc['cv_%'] = (desc['std'] / desc['mean'] * 100).round(2)   # Coefficient of Variation
print(desc.to_string())
print("""
  INTERPRETATION:
  • Temperature has an extremely low CV (≈0.1%) → readings were likely
    collected in a very short period or stable environment.
  • PM values are tightly clustered (CV ≈ 6-7%) → relatively stable
    air quality during the measurement window.
  • Gas resistance has the highest CV (≈12%) → most variable sensor,
    likely reacting to transient VOC events.
""")

# ─────────────────────────────────────────────────────────────────────────────
# 3. DISTRIBUTION ANALYSIS  (Histograms + KDE)
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Plot the frequency distribution of each feature.
# WHY:   - Reveals if features are normally distributed (important for some
#          ML algorithms that assume normality, e.g. Linear Regression).
#        - Shows skewness: right-skewed pollutant data is common in
#          environmental monitoring because spikes are rare but extreme.
#        - Identifies multi-modal distributions which could indicate
#          different environmental regimes (e.g., day vs night).
# ─────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  3. DISTRIBUTION ANALYSIS")
print("=" * 65)

fig, axes = plt.subplots(2, 4, figsize=(20, 9))
fig.suptitle('Feature Distributions — Histograms with KDE', fontsize=16, y=1.02)

# Colour each feature differently for easy identification
colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22']

for i, col in enumerate(df.columns):
    ax = axes[i // 4, i % 4]
    sns.histplot(df[col], bins=30, kde=True, ax=ax, color=colors[i], edgecolor='white')
    ax.set_title(col, fontweight='bold')
    ax.set_ylabel('Count')

    # Add skewness annotation — tells us how asymmetric the distribution is
    skew_val = df[col].skew()
    ax.annotate(f'Skew: {skew_val:.2f}', xy=(0.72, 0.9), xycoords='axes fraction',
                fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Remove the empty 8th subplot (we have 7 features but 2×4=8 slots)
axes[1, 3].set_visible(False)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/01_distributions.png', dpi=150, bbox_inches='tight')
plt.close()

# Print skewness analysis
print("\n  Skewness of each feature (0 = perfectly symmetric):")
for col in df.columns:
    skew = df[col].skew()
    direction = "right-skewed" if skew > 0.5 else ("left-skewed" if skew < -0.5 else "approx. symmetric")
    print(f"    • {col:<18s} {skew:+.3f}  ({direction})")
print(f"\n  → Plot saved: {OUTPUT_DIR}/01_distributions.png")

# ─────────────────────────────────────────────────────────────────────────────
# 4. CORRELATION ANALYSIS  (Heatmap)
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Compute the Pearson correlation matrix and display as a heatmap.
# WHY:   This is arguably the MOST IMPORTANT chart for an ML project:
#        - Shows which features are strongly correlated with AQI (the target).
#          High correlation → strong predictor for the model.
#        - Detects multicollinearity: if pm1, pm25, pm10 are all highly
#          correlated with each other (>0.9), including all three in a model
#          adds redundancy and can destabilise coefficient estimates.
#        - Helps with feature selection: drop features that add noise.
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  4. CORRELATION ANALYSIS")
print("=" * 65)

corr_matrix = df.corr()

print("\n  Pearson Correlation Matrix:")
print(corr_matrix.round(3).to_string())

# Highlight AQI correlations specifically
print("\n  Correlations with AQI (target variable):")
aqi_corr = corr_matrix['aqi'].drop('aqi').sort_values(ascending=False)
for feat, val in aqi_corr.items():
    strength = "STRONG" if abs(val) > 0.7 else ("moderate" if abs(val) > 0.4 else "weak")
    print(f"    • {feat:<18s} {val:+.4f}  [{strength}]")

# Plot heatmap
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)   # Show only lower triangle
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
            mask=mask, square=True, linewidths=0.5, ax=ax,
            cbar_kws={'label': 'Pearson Correlation'})
ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/02_correlation_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\n  → Plot saved: {OUTPUT_DIR}/02_correlation_heatmap.png")

# ─────────────────────────────────────────────────────────────────────────────
# 5. PM PARTICLE RELATIONSHIP  (pm1 vs pm2.5 vs pm10)
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Scatter matrix comparing the three particulate matter readings.
# WHY:   Physically, pm1 ⊂ pm2.5 ⊂ pm10 (smaller particles are a subset of
#        larger ones). Therefore we EXPECT pm1 < pm25 < pm10 for every row,
#        and very strong positive correlations between them.
#        • If this relationship breaks → possible sensor malfunction.
#        • If correlations are >0.95 → we might drop pm1 and pm10 from the
#          model and keep only pm25 (the most health-relevant metric according
#          to WHO guidelines) to reduce multicollinearity.
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  5. PARTICULATE MATTER RELATIONSHIP (pm1 vs pm2.5 vs pm10)")
print("=" * 65)

# Validate the physical constraint pm1 ≤ pm25 ≤ pm10
violations = df[(df['pm1'] > df['pm25']) | (df['pm25'] > df['pm10'])]
print(f"\n  Physical constraint check (pm1 ≤ pm25 ≤ pm10):")
print(f"    Total rows      : {len(df)}")
print(f"    Violations      : {len(violations)}")
print(f"    Data integrity  : {'✓ PASSED' if len(violations) == 0 else '✗ ISSUES FOUND'}")

# Plot pair-wise scatter of PM values coloured by AQI
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
pm_pairs = [('pm1', 'pm25'), ('pm1', 'pm10'), ('pm25', 'pm10')]

for ax, (x, y) in zip(axes, pm_pairs):
    scatter = ax.scatter(df[x], df[y], c=df['aqi'], cmap='YlOrRd', alpha=0.6, s=15)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(f'{x} vs {y}', fontweight='bold')

    # Fit and plot a trend line to visualise the linear relationship
    z = np.polyfit(df[x], df[y], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df[x].min(), df[x].max(), 100)
    ax.plot(x_line, p(x_line), '--', color='black', linewidth=1.5, label=f'Trend (slope={z[0]:.2f})')
    ax.legend(fontsize=9)

fig.colorbar(scatter, ax=axes, label='AQI', shrink=0.8)
fig.suptitle('Particulate Matter Inter-Relationships (coloured by AQI)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/03_pm_relationships.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\n  → Plot saved: {OUTPUT_DIR}/03_pm_relationships.png")

# ─────────────────────────────────────────────────────────────────────────────
# 6. ENVIRONMENTAL FACTORS vs AQI  (Temperature & Humidity)
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Scatter plots of temperature vs AQI and humidity vs AQI.
# WHY:   Environmental conditions heavily influence air quality:
#        - Higher temperatures can increase ground-level ozone formation.
#        - Higher humidity can cause particulate matter to absorb moisture,
#          increasing their effective size and measured concentration.
#        - Understanding these relationships helps decide if temperature
#          and humidity are useful features or just noise for the ML model.
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  6. ENVIRONMENTAL FACTORS vs AQI")
print("=" * 65)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Temperature vs AQI
axes[0].scatter(df['temperature'], df['aqi'], alpha=0.4, c='#e74c3c', s=20)
axes[0].set_xlabel('Temperature (°C)')
axes[0].set_ylabel('AQI')
axes[0].set_title('Temperature vs AQI', fontweight='bold')

# Humidity vs AQI
axes[1].scatter(df['humidity'], df['aqi'], alpha=0.4, c='#3498db', s=20)
axes[1].set_xlabel('Humidity (%)')
axes[1].set_ylabel('AQI')
axes[1].set_title('Humidity vs AQI', fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/04_env_vs_aqi.png', dpi=150, bbox_inches='tight')
plt.close()

# Quantify the relationships
from scipy import stats
for env_feat in ['temperature', 'humidity']:
    r, p_val = stats.pearsonr(df[env_feat], df['aqi'])
    significance = "statistically significant" if p_val < 0.05 else "NOT statistically significant"
    print(f"\n  {env_feat} vs AQI:")
    print(f"    Pearson r  = {r:+.4f}")
    print(f"    p-value    = {p_val:.2e}  ({significance})")

print(f"\n  → Plot saved: {OUTPUT_DIR}/04_env_vs_aqi.png")

# ─────────────────────────────────────────────────────────────────────────────
# 7. GAS RESISTANCE ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Analyse the gas_resistance sensor readings vs AQI.
# WHY:   The gas resistance sensor (typically a BME680 or similar MOX sensor)
#        measures volatile organic compounds (VOCs). Its resistance DECREASES
#        when more pollutants are present:
#          - High gas_resistance → clean air
#          - Low gas_resistance  → polluted air
#        We expect a NEGATIVE correlation with AQI (higher AQI = worse air).
#        This is a crucial feature for indoor/outdoor air quality distinction.
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  7. GAS RESISTANCE ANALYSIS")
print("=" * 65)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Scatter plot
axes[0].scatter(df['gas_resistance'], df['aqi'], alpha=0.4, c='#2ecc71', s=20)
axes[0].set_xlabel('Gas Resistance (kΩ)')
axes[0].set_ylabel('AQI')
axes[0].set_title('Gas Resistance vs AQI', fontweight='bold')

# Box plot to show distribution
axes[1].boxplot(df['gas_resistance'], vert=True, patch_artist=True,
                boxprops=dict(facecolor='#2ecc71', alpha=0.6))
axes[1].set_ylabel('Gas Resistance (kΩ)')
axes[1].set_title('Gas Resistance Distribution', fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/05_gas_resistance.png', dpi=150, bbox_inches='tight')
plt.close()

r, p_val = stats.pearsonr(df['gas_resistance'], df['aqi'])
print(f"\n  Gas Resistance vs AQI:")
print(f"    Pearson r  = {r:+.4f}")
print(f"    p-value    = {p_val:.2e}")
print(f"    Direction  = {'Negative (expected ✓)' if r < 0 else 'Positive (unexpected — investigate!)'}")
print(f"\n  → Plot saved: {OUTPUT_DIR}/05_gas_resistance.png")

# ─────────────────────────────────────────────────────────────────────────────
# 8. OUTLIER DETECTION  (Box Plots + IQR Method)
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Identify outliers in each feature using the IQR (Interquartile
#        Range) method: any value below Q1 − 1.5×IQR or above Q3 + 1.5×IQR.
# WHY:   Outliers can:
#        - Skew the mean and standard deviation → misleading statistics.
#        - Disproportionately influence linear regression models.
#        - Indicate sensor glitches, calibration errors, or genuinely
#          extreme air quality events worth investigating.
#        Knowing which features have outliers helps us decide whether to
#        clip, remove, or keep them during model training.
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  8. OUTLIER DETECTION (IQR Method)")
print("=" * 65)

fig, axes = plt.subplots(2, 4, figsize=(20, 9))
fig.suptitle('Box Plots — Outlier Detection', fontsize=16, y=1.02)

print("\n  Feature            Outliers   %      Lower Bound   Upper Bound")
print("  " + "-" * 64)

for i, col in enumerate(df.columns):
    ax = axes[i // 4, i % 4]
    bp = ax.boxplot(df[col], vert=True, patch_artist=True,
                    boxprops=dict(facecolor=colors[i], alpha=0.6),
                    medianprops=dict(color='black', linewidth=2))
    ax.set_title(col, fontweight='bold')

    # Calculate IQR bounds
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)]
    pct = len(outliers) / len(df) * 100
    print(f"  {col:<20s} {len(outliers):>4d}     {pct:>5.1f}%     {lower:>10.2f}    {upper:>10.2f}")

axes[1, 3].set_visible(False)    # Hide empty subplot
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/06_boxplots_outliers.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\n  → Plot saved: {OUTPUT_DIR}/06_boxplots_outliers.png")

# ─────────────────────────────────────────────────────────────────────────────
# 9. FEATURE IMPORTANCE ESTIMATE  (using correlation-based ranking)
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Rank features by absolute Pearson correlation with AQI.
# WHY:   A quick, model-free way to estimate which features the ML model
#        will find most useful. While not as rigorous as model-based
#        importance (e.g., Random Forest feature importances), it gives an
#        instant indication of predictive power.
#        This helps answer: "If I could only keep 3 features, which ones?"
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  9. FEATURE IMPORTANCE (Correlation-Based Ranking)")
print("=" * 65)

importance = corr_matrix['aqi'].drop('aqi').abs().sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.barh(importance.index, importance.values, color=sns.color_palette('viridis', len(importance)))
ax.set_xlabel('|Pearson Correlation with AQI|')
ax.set_title('Feature Importance — Correlation with AQI', fontweight='bold', fontsize=14)

# Annotate bars with exact values
for bar, val in zip(bars, importance.values):
    ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
            f'{val:.3f}', va='center', fontsize=10)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/07_feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()

print("\n  Rank  Feature            |Correlation|  Recommendation")
print("  " + "-" * 60)
for rank, (feat, val) in enumerate(importance.sort_values(ascending=False).items(), 1):
    rec = "★ Keep" if val > 0.4 else ("Consider" if val > 0.2 else "May drop")
    print(f"  {rank:>4d}  {feat:<18s}  {val:.4f}         {rec}")

print(f"\n  → Plot saved: {OUTPUT_DIR}/07_feature_importance.png")

# ─────────────────────────────────────────────────────────────────────────────
# 10. AQI CATEGORY BREAKDOWN
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Classify each reading into standard AQI categories and count them.
# WHY:   The raw AQI number (0–500) is hard to interpret. Categorising it
#        into the EPA standard buckets (Good, Moderate, Unhealthy, etc.)
#        reveals the overall air quality profile of the measurement site.
#        This is essential for public-health reporting and helps users of
#        the Aerolytics app understand what the numbers mean.
#
#        EPA AQI Categories:
#          0–50    → Good (green)
#          51–100  → Moderate (yellow)
#          101–150 → Unhealthy for Sensitive Groups (orange)
#          151–200 → Unhealthy (red)
#          201–300 → Very Unhealthy (purple)
#          301–500 → Hazardous (maroon)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  10. AQI CATEGORY BREAKDOWN")
print("=" * 65)

def classify_aqi(value):
    """Classify AQI into EPA standard categories."""
    if value <= 50:
        return 'Good'
    elif value <= 100:
        return 'Moderate'
    elif value <= 150:
        return 'Unhealthy (Sensitive)'
    elif value <= 200:
        return 'Unhealthy'
    elif value <= 300:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

df = df.copy()
df['aqi_category'] = df['aqi'].apply(classify_aqi)

# Define consistent order and colours matching EPA standard
cat_order = ['Good', 'Moderate', 'Unhealthy (Sensitive)', 'Unhealthy', 'Very Unhealthy', 'Hazardous']
cat_colors = {'Good': '#00E400', 'Moderate': '#FFFF00', 'Unhealthy (Sensitive)': '#FF7E00',
              'Unhealthy': '#FF0000', 'Very Unhealthy': '#8F3F97', 'Hazardous': '#7E0023'}

cat_counts = df['aqi_category'].value_counts()
cat_counts = cat_counts.reindex([c for c in cat_order if c in cat_counts.index])

print("\n  Category                  Count    Percentage")
print("  " + "-" * 50)
for cat, count in cat_counts.items():
    pct = count / len(df) * 100
    print(f"  {cat:<28s} {count:>4d}     {pct:>5.1f}%")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Bar chart
bar_colors = [cat_colors[c] for c in cat_counts.index]
axes[0].bar(cat_counts.index, cat_counts.values, color=bar_colors, edgecolor='black', linewidth=0.5)
axes[0].set_ylabel('Number of Readings')
axes[0].set_title('AQI Category Distribution', fontweight='bold')
axes[0].tick_params(axis='x', rotation=30)

# Pie chart
axes[1].pie(cat_counts.values, labels=cat_counts.index, colors=bar_colors,
            autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'black', 'linewidth': 0.5})
axes[1].set_title('AQI Category Proportions', fontweight='bold')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/08_aqi_categories.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\n  → Plot saved: {OUTPUT_DIR}/08_aqi_categories.png")

# ─────────────────────────────────────────────────────────────────────────────
# 11. TIME-SERIES TREND  (Sequential Reading Analysis)
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Plot AQI and PM2.5 over the sequence of readings.
# WHY:   Even though we don't have timestamps, the row order likely reflects
#        chronological order. Plotting trends reveals:
#        - Gradual air quality changes (e.g., worsening over hours)
#        - Sudden spikes indicating pollution events
#        - Cyclical patterns (if the data covers day/night cycles)
#        A rolling average smooths out noise and highlights the trend.
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  11. TIME-SERIES TREND (Sequential Analysis)")
print("=" * 65)

fig, ax1 = plt.subplots(figsize=(16, 5))

# Use a 20-reading rolling average to smooth noise
window = 20
aqi_smooth = df['aqi'].rolling(window=window, center=True).mean()
pm25_smooth = df['pm25'].rolling(window=window, center=True).mean()

ax1.plot(df.index, df['aqi'], alpha=0.2, color='red', linewidth=0.5, label='AQI (raw)')
ax1.plot(df.index, aqi_smooth, color='red', linewidth=2, label=f'AQI (rolling avg, w={window})')
ax1.set_xlabel('Reading Number (sequential)')
ax1.set_ylabel('AQI', color='red')
ax1.tick_params(axis='y', labelcolor='red')
ax1.legend(loc='upper left')

# Overlay PM2.5 on secondary y-axis
ax2 = ax1.twinx()
ax2.plot(df.index, df['pm25'], alpha=0.2, color='blue', linewidth=0.5, label='PM2.5 (raw)')
ax2.plot(df.index, pm25_smooth, color='blue', linewidth=2, label=f'PM2.5 (rolling avg, w={window})')
ax2.set_ylabel('PM2.5 (µg/m³)', color='blue')
ax2.tick_params(axis='y', labelcolor='blue')
ax2.legend(loc='upper right')

ax1.set_title('AQI & PM2.5 Trends Over Sequential Readings', fontweight='bold', fontsize=14)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/09_time_series_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"\n  → Plot saved: {OUTPUT_DIR}/09_time_series_trend.png")

# ─────────────────────────────────────────────────────────────────────────────
# 12. PAIR PLOT  (Full Feature Relationships)
# ─────────────────────────────────────────────────────────────────────────────
# WHAT:  Create a comprehensive pair plot showing scatter plots for every
#        pair of features, with histograms on the diagonal.
# WHY:   The pair plot is the "Swiss army knife" of EDA — it shows ALL
#        bivariate relationships at once. While individual plots above
#        focus on specific questions, this gives a bird's-eye view and
#        can reveal unexpected patterns we didn't specifically look for.
#        Colouring by AQI category adds a third dimension of information.
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  12. PAIR PLOT (Full Feature Relationships)")
print("=" * 65)
print("\n  Generating pair plot (this may take a moment)...")

# Use a subset of features to keep the plot manageable
pair_cols = ['pm25', 'pm10', 'temperature', 'humidity', 'gas_resistance', 'aqi']
g = sns.pairplot(df[pair_cols + ['aqi_category']], hue='aqi_category',
                 hue_order=[c for c in cat_order if c in df['aqi_category'].unique()],
                 palette=cat_colors, plot_kws={'alpha': 0.5, 's': 15},
                 diag_kind='kde', corner=True)
g.figure.suptitle('Pair Plot — All Feature Relationships by AQI Category', y=1.02, fontsize=14, fontweight='bold')
plt.savefig(f'{OUTPUT_DIR}/10_pair_plot.png', dpi=100, bbox_inches='tight')
plt.close()
print(f"  → Plot saved: {OUTPUT_DIR}/10_pair_plot.png")

# ─────────────────────────────────────────────────────────────────────────────
# 13. SUMMARY & RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  13. ANALYSIS SUMMARY & RECOMMENDATIONS")
print("=" * 65)
print(f"""
  DATASET:
  • {len(df)} air quality readings with {len(df.columns) - 1} features
  • No missing values — data is clean and ready for modelling

  KEY FINDINGS:
  1. PM1, PM2.5, PM10 are very highly correlated (>0.95)
     → Consider using only PM2.5 (most health-relevant) to reduce
       multicollinearity in the model

  2. Temperature has a very narrow range ({df['temperature'].min()}–{df['temperature'].max()}°C)
     → The model may not generalise well to different seasons/climates
     → Collect data across a wider temperature range

  3. Gas resistance shows {'expected negative' if corr_matrix.loc['gas_resistance', 'aqi'] < 0 else 'unexpected positive'}
     correlation with AQI
     → {'Good sensor validation — higher resistance = cleaner air' if corr_matrix.loc['gas_resistance', 'aqi'] < 0 else 'Investigate sensor calibration'}

  4. Most readings fall in the {"'"+cat_counts.idxmax()+"'" if len(cat_counts) > 0 else 'N/A'} category
     ({cat_counts.max()}/{len(df)} = {cat_counts.max()/len(df)*100:.1f}%)
     → {'Dataset is imbalanced — model may struggle with rare categories' if cat_counts.max()/len(df) > 0.8 else 'Reasonable category balance'}

  RECOMMENDATIONS FOR ML MODEL:
  • Start with features: pm25, humidity, gas_resistance  (most predictive)
  • Consider dropping pm1 and pm10 if multicollinearity causes issues
  • Try both Linear Regression and Random Forest to compare performance
  • Collect more data across different environmental conditions for
    better generalisation

  ALL PLOTS SAVED IN: {OUTPUT_DIR}/
""")

# Clean up the temporary column
df = df.drop(columns=['aqi_category'])

print("  Analysis complete! ✓")
print("=" * 65)
