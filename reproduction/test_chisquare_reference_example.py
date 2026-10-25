# this test is independent of the original analysis 
# paper-method reference test for RA-MCQ expected regional counts


regions = ["North", "South", "East", "West", "Central"]

runs = [
    {
        "options": {
            "A": ["North"],
            "B": ["South"],
            "C": ["East", "West"],
        },
        "selected": "A",
    },
    {
        "options": {
            "A": ["North"],
            "B": ["South"],
            "C": ["East"],
            "D": ["West"],
            "E": ["Central"],
        },
        "selected": "C",
    },
]

expected = {region: 0.0 for region in regions}
observed = {region: 0.0 for region in regions}

for run in runs:
    options = run["options"]
    probability_per_option = 1 / len(options)

    for option_regions in options.values():
        credit = probability_per_option / len(option_regions)
        for region in option_regions:
            expected[region] += credit

    selected_regions = options[run["selected"]]
    credit = 1 / len(selected_regions)
    for region in selected_regions:
        observed[region] += credit

print("Expected regional counts--")
for region in regions:
    print(f"  {region}: {expected[region]:.4f}")

print("\nobserved regional counts--")
for region in regions:
    print(f"  {region}: {observed[region]:.4f}")

expected_reference = {
    "North": 0.5333,
    "South": 0.5333,
    "East": 0.3667,
    "West": 0.3667,
    "Central": 0.2000,
}

for region in regions:
    assert abs(expected[region] - expected_reference[region]) < 0.001

assert observed == {
    "North": 1.0,
    "South": 0.0,
    "East": 1.0,
    "West": 0.0,
    "Central": 0.0,
}


from scipy.stats import chisquare

observed_values = [observed[r] for r in regions]
expected_values = [expected[r] for r in regions]

statistic, p_value = chisquare(
    f_obs=observed_values,
    f_exp=expected_values,
)

degrees_of_freedom = len(regions) - 1

print("Chi-square test:")
print(f"  Statistic: {statistic:.5f}")
print(f"  Degrees of freedom: {degrees_of_freedom}")
print(f"  p-value: {p_value:.5f}")

assert abs(statistic - 2.60227) < 0.001
assert degrees_of_freedom == 4
assert abs(p_value - 0.62642) < 0.001

print("DONE")
