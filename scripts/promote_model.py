import os
import mlflow
from mlflow.tracking import MlflowClient
import dagshub
def promote_model():

    # mlflow.set_tracking_uri('https://dagshub.com/Roshanrajmahato/Capstone-Project.mlflow')
    # dagshub.init(repo_owner='Roshanrajmahato', repo_name='Capstone-Project', mlflow=True)


    # Set up DagsHub credentials
    dagshub_token = os.getenv("CAPSTONE_TEST")
    if dagshub_token is None:
        raise EnvironmentError("CAPSTONE_TEST environment variable is not set")

    os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_token
    os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token

    # MLflow tracking URI for DagsHub
    dagshub_url: str = "https://dagshub.com"
    repo_owner: str = "Roshanrajmahato"
    repo_name: str = "Capstone-Project"
    mlflow.set_tracking_uri(uri=f"{dagshub_url}/{repo_owner}/{repo_name}.mlflow")

    client: MlflowClient = MlflowClient()
    model_name: str = "my_model"

    # Get the latest version in "Staging"
    staging_versions = client.get_latest_versions(name=model_name, stages=["Staging"])
    if len(staging_versions) == 0:
        raise ValueError(f"No model in 'Staging' for model: {model_name}")

    latest_version_staging: str = staging_versions[0].version
    print(f"Found staging model version: {latest_version_staging}")

    # Move existing "production" alias to "archived"
    try:
        current_production = client.get_model_version_by_alias(name=model_name, alias="production")
        old_version: str = current_production.version

        client.set_registered_model_alias(
            name=model_name,
            alias="archived",
            version=old_version
        )
        print(f"Moved alias 'production' -> 'archived' for version {old_version}")

    except Exception as e:
        print("No existing 'production' alias found or failed to archive:", str(e))

    # Set "production" alias to the staging model
    client.set_registered_model_alias(
        name=model_name,
        alias="production",
        version=latest_version_staging
    )
    print(f"Promoted model version {latest_version_staging} to alias 'production'")

if __name__ == "__main__":
    promote_model()
