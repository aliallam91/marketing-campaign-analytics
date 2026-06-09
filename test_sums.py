from data_loader import load_data
import sys

# Configure stdout encoding to utf-8 if possible
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

print("Starting verification of data totals...")

try:
    data_dict = load_data()
    df = data_dict['merged']
except Exception as e:
    print(f"FAILED: Error loading data: {e}")
    sys.exit(1)

# Excel Grand Totals (Reference values from Pivot Tables sheet)
REF_COST = 91448131.19
REF_REVENUE = 2165462575.20
REF_LEADS = 1421284
REF_ENROLLMENTS = 392314
REF_IMPRESSIONS = 129158189
REF_CLICKS = 7138412

# Calculate totals from merged dataframe
calc_cost = df['Cost'].sum()
calc_revenue = df['Revenue'].sum()
calc_leads = df['Leads'].sum()
calc_enrollments = df['Enrollments'].sum()
calc_impressions = df['Impressions'].sum()
calc_clicks = df['Clicks'].sum()

print("\n" + "="*40)
print("METRIC COMPARISONS")
print("="*40)
print(f"Cost:        Excel={REF_COST:,.2f}  |  Calculated={calc_cost:,.2f}")
print(f"Revenue:     Excel={REF_REVENUE:,.2f}  |  Calculated={calc_revenue:,.2f}")
print(f"Leads:       Excel={REF_LEADS:,}  |  Calculated={calc_leads:,}")
print(f"Enrollments: Excel={REF_ENROLLMENTS:,}  |  Calculated={calc_enrollments:,}")
print(f"Impressions: Excel={REF_IMPRESSIONS:,}  |  Calculated={calc_impressions:,}")
print(f"Clicks:      Excel={REF_CLICKS:,}  |  Calculated={calc_clicks:,}")

# Run assertions
try:
    assert abs(calc_cost - REF_COST) < 0.01, f"Cost mismatch: Diff={abs(calc_cost - REF_COST)}"
    assert abs(calc_revenue - REF_REVENUE) < 0.01, f"Revenue mismatch: Diff={abs(calc_revenue - REF_REVENUE)}"
    assert calc_leads == REF_LEADS, f"Leads mismatch: Diff={calc_leads - REF_LEADS}"
    assert calc_enrollments == REF_ENROLLMENTS, f"Enrollments mismatch: Diff={calc_enrollments - REF_ENROLLMENTS}"
    assert calc_impressions == REF_IMPRESSIONS, f"Impressions mismatch: Diff={calc_impressions - REF_IMPRESSIONS}"
    assert calc_clicks == REF_CLICKS, f"Clicks mismatch: Diff={calc_clicks - REF_CLICKS}"
    print("\nSUCCESS: All calculated totals match the Excel sheet's grand totals perfectly!")
except AssertionError as ae:
    print(f"\nFAILURE: Validation check failed: {ae}")
    sys.exit(1)
except Exception as e:
    # Safe printing of errors
    clean_err = str(e).encode('ascii', errors='replace').decode('ascii')
    print(f"\nFAILURE: Unexpected error during validation: {clean_err}")
    sys.exit(1)
