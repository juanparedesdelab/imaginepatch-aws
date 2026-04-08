from diagrams.custom import Custom
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import Route53, CloudFront
from diagrams.aws.compute import Lightsail
from diagrams.aws.database import RDS, ElastiCache
from diagrams.aws.storage import S3
from diagrams.aws.engagement import SES
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAM
from diagrams.onprem.client import User as Customer

graph_attr = {
    "fontsize": "12",
    "bgcolor": "white",
    "pad": "0.8",
    "splines": "curved",
    "nodesep": "0.8",
    "ranksep": "1.0",
    "dpi": "200",
}

node_attr = {
    "fontsize": "12",
    "fontname": "Arial",
    "width": "1.2",
    "height": "1.2",
    "margin": "0.4,0.3",
}

edge_attr = {
    "fontsize": "10",
    "fontname": "Arial",
}

with Diagram(
    "Imagine Patch — AWS Architecture (Phase 1)",
    filename="imaginepatch_architecture",
    outformat="png",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    direction="TB",
    show=False,
):
    # External actor
    customer = Customer("Customer")

    # AWS Cloud boundary
    with Cluster("AWS Cloud — us-east-1"):

        # Edge layer
        with Cluster("Edge Layer"):
            dns = Route53("Route 53\nimaginepatch.com")
            cdn = CloudFront("CloudFront\nCDN + SSL")

        # Compute
        with Cluster("Compute"):
            lightsail = Lightsail("Lightsail\nWordPress\n$10/month")

        # Data layer
        with Cluster("Data Layer"):
            db = RDS("RDS MySQL")
            cache = ElastiCache("ElastiCache\nRedis")
            storage = S3("S3 Bucket")

        # Integrations
        with Cluster("Integrations"):
            email = SES("SES Email")

    # External services
    with Cluster("External Services"):
        printful = Custom("Printful", "./printful.png")
        stripe = Custom("Stripe", "./stripe.png")

    # Monitoring — defined last to push it to bottom
    with Cluster("Monitoring + Security"):
        monitoring = Cloudwatch("CloudWatch")
        iam = IAM("IAM\n5 Groups")

    # Traffic flow
    customer >> Edge(label="  HTTPS  ") >> dns
    dns >> Edge(label="DNS") >> cdn
    cdn >> Edge(label="Cache miss") >> lightsail

    # Lightsail to data
    lightsail >> Edge(label="SQL") >> db
    lightsail >> Edge(label="Cache") >> cache
    lightsail >> Edge(label="Media") >> storage

    # Lightsail to integrations
    lightsail >> Edge(label="Email") >> email

    # Lightsail to external
    lightsail >> Edge(label="Orders") >> printful
    lightsail >> Edge(label="Payments") >> stripe

    # Monitoring
    lightsail >> Edge(label="Logs") >> monitoring
    iam >> Edge(label="Controls", style="dashed") >> lightsail