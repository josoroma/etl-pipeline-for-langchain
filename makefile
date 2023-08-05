# Set up the project by installing the dependencies and activating the virtual environment
setup:
	poetry install
	poetry env use `which python3.11`
	poetry shell

# Add new dependencies to the project
add:
	poetry add streamlit openai langchain markdown weaviate-client luigi notebook jupytext tiktoken bs4 tqdm unstructured "pydantic>=1,<2" logging

# Start the Luigi daemon, which is needed to run the ETL pipeline
run-etl-daemon:
	poetry run luigid

# Open the Luigi visualizer to monitor the progress of the ETL pipeline
run-etl-visualizer:
	open http://localhost:8082

# Run the ETL pipeline by starting the Luigi pipeline with the orchestrator task
run-etl-orchestrator:
	poetry run python -m luigi --module orchestrator Orchestrator --local-scheduler

# Run the chat interface by starting the Streamlit application with the chat.py script
run-chat:
	poetry run streamlit run chat.py

# Clean up the project by removing the virtual environment and deleting the poetry.lock file
clean:
	rm -rf `poetry env info -p`
	rm -rf poetry.lock
