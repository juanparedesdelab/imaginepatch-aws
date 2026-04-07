from diagrams import Diagram, Cluster, Edge
from diagrams.aws.network import Route53, CloudFront
from diagrams.aws.compute import Lightsail
from diagrams.aws.database import RDS, ElastiCache
from diagrams.aws.storage import S3
from diagrams.aws.engagement import SES
from diagrams.aws.management import Cloudwatch
from diagrams.aws.security import IAM
from diagrams.aws.general import User
from diagrams.onprem.client import User as ExternalUser
from diagrams.saas.payment import Stripe

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
}

with Diagram(
    "Imagine Patch — AWS Architecture (Phase 1)",
    filename="imaginepatch_architecture",
    outformat="png",
    graph_attr=graph_attr,
    direction="TB",
    show=False,
):
    # External actors
    user = ExternalUser("Customer")

    # External services
    with Cluster("External Services"):
        printful = ExternalUser("Printful API")
        stripe = Stripe("Stripe")

    # AWS Cloud
    with Cluster("AWS Cloud — us-east-1"):

        # DNS + CDN
        with Cluster("Edge Layer"):
            dns = Route53("Route 53\nimaginepatch.com")
            cdn = CloudFront("CloudFront\nCDN + SSL")

        # Compute
        with Cluster("Compute"):
            lightsail = Lightsail("Lightsail\nWordPress + WooCommerce\n$10/month")

        # Data
        with Cluster("Data Layer"):
            db = RDS("RDS MySQL\nWooCommerce DB")
            cache = ElastiCache("ElastiCache\nRedis Cache")
            storage = S3("S3\nMedia + Backups")

        # Integrations
        with Cluster("Integrations"):
            email = SES("SES\nTransactional Email")

        # Monitoring
        with Cluster("Monitoring + Security"):
            monitoring = Cloudwatch("CloudWatch\nLogs + Alerts")
            iam = IAM("IAM\n5 Groups + Policies")

    # Connections
    user >> Edge(label="HTTPS") >> dns
    dns >> Edge(label="DNS") >> cdn
    cdn >> Edge(label="Cache miss") >> lightsail
    lightsail >> Edge(label="Queries") >> db
    lightsail >> Edge(label="Cache") >> cache
    lightsail >> Edge(label="Assets") >> storage
    lightsail >> Edge(label="Orders") >> printful
    lightsail >> Edge(label="Payments") >> stripe
    lightsail >> Edge(label="Email") >> email
    lightsail >> Edge(label="Logs") >> monitoring
    iam >> Edge(label="Controls", style="dashed") >> lightsail