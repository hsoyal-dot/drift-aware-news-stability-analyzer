import pathlib
from drift_analyzer.pipeline import run_analysis

# Dummy article text
article = "Breaking news: City council approves new park. The park will open on July 1st, 2024. Mayor Jane Doe announced the project."

# Run analysis
config_file = pathlib.Path("drift_analyzer/config.yaml")
report = run_analysis(article, config_path=str(config_file))
print(report)
