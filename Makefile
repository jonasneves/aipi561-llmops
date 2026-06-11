.PHONY: data check run test report

data:    ## pull the course dataset into data/ (~50MB, git-ignored)
	python scripts/fetch_data.py

check:   ## verify data files + config are present
	python app.py check

run:     ## ask one question, e.g. make run Q="What is the travel policy?"
	python app.py ask "$(Q)" --role $(or $(ROLE),engineer)

test:    ## run the tool smoke tests (no API key needed)
	python -m pytest -q

report:  ## run the 10-query eval and write report.md (needs GOOGLE_API_KEY)
	python scripts/run_report.py
