from diagrams import Cluster, Diagram, Edge, Node
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import ElasticBlockStoreEBSSnapshot
from diagrams.aws.storage import SimpleStorageServiceS3 as S3
from diagrams.azure.database import SQLServers
from diagrams.azure.general import Helpsupport
from diagrams.azure.identity import Users
from diagrams.gcp.operations import Monitoring
from diagrams.oci.monitoring import Notifications
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow
from diagrams.onprem.database import Postgresql as PostgreSQL
from diagrams.aws.analytics import Quicksight
from diagrams.oci.monitoring import Telemetry


with Diagram(
    "Cloud Architecture Diagram",
    show=False,
    direction="LR",
    graph_attr={"rankdir": "LR", "splines": "ortho"},
):
    ingress = Users("User")
    with Cluster("Sources of Data"):
        with Cluster(""):
            geos_bucket = S3("Geos18 Bucket")
            nexrad_bucket = S3("Nexrad Bucket")

    with Cluster("Docker"):
        with Cluster("App"):
            userfacing = Docker("Streamlit")
            backend = Docker("FastAPI")

        with Cluster("Sqlite Database"):
            user_db = SQLServers("Users DB")


        with Cluster(" "):
            cloudwatch = Cloudwatch("Logs")

        with Cluster("Analytics"):
            analytics = Quicksight("Analytics")

        with Cluster("Database"):
            metadata_db = PostgreSQL("DB")

    with Cluster("Airflow Docker"):
        class DAG(Airflow):
            _type = "DAG"

        with Cluster(""):
            GEOS_DAG = DAG("Geos Dag")

        with Cluster(""):
            NEXRAD_DAG = DAG("Nexrad Dag")

        with Cluster(""):
            G_E = DAG("Great Expectations Dag")

    aws_bucket = S3("S3 Bucket")
    developers = Users("Developers")
    da = Telemetry("Data Quality Check")

    userfacing >> Edge(label="API Request", color="black") >>backend
    backend >> Edge(label="Response", color="black") >> userfacing

    user_db << Edge(label="Authorization") << backend
    cloudwatch << Edge(label="Cloud watch Logging") << backend

    backend << Edge(label="Fetching Data for Streamlit") << metadata_db

    metadata_db << Edge(label="Update Data") << GEOS_DAG
    metadata_db << Edge(label="Update Data") << NEXRAD_DAG
    metadata_db << Edge(label="Update Data") << G_E

    GEOS_DAG << Edge(label="Fetches Geos MetaData") << geos_bucket
    NEXRAD_DAG << Edge(label="Fetches Nexrad MetaData") << nexrad_bucket

    ingress >> Edge(label="Login to Dashboard", color="black") << userfacing
    da << Edge(label="Data Quality checks") << metadata_db
    da >> Edge(label="Static Hosting of Reports") >> aws_bucket
    developers << Edge(label="View Reports", color="darkgreen") << aws_bucket

    analytics << Edge(label="Using cloudwatch logs to generate Analytics", color="darkgreen") << cloudwatch
    analytics >> Edge(label="Analytics Dashboard", color="black") << userfacing
    analytics << Edge(label="Analytics Dashboard available on User login ") << ingress
    analytics << Edge(label="Analytics Dashboard available on Developer login ") << developers