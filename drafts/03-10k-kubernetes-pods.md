# ~10,000 Kubernetes Pods, Mostly GPU: Lessons From Running AI Infrastructure Across Continents

*What running a multi-region, multi-cluster Kubernetes infrastructure for an AI platform actually looks like in practice. Not theory, not a tutorial. Just what we learned the hard way.*

---

When people hear "10,000 Kubernetes pods" they usually think about scale. But scale is the easy part. Kubernetes handles scale. What it doesn't handle for you is cost control when most of those pods are GPU pods, observability across multiple clusters in different continents, and keeping three different deployment models (cloud, on-prem, edge) running from the same codebase.

I work on the infrastructure behind an AI workplace safety platform that serves Fortune 500 companies in over 25 countries. Here's what I've learned.

## The Architecture

Our infrastructure is split across multiple clusters in different regions. The main region hosts two separate clusters: one for backend services (APIs, data processing, workflow orchestration) and one for GPU workloads (AI model inference). Additional GPU clusters in other regions handle inference closer to customers, reducing latency for real-time video analysis.

The majority of our pods are GPU-powered. This is not a web app that happens to use some ML on the side. AI inference is the core product. The GPU ratio shapes everything: cost structure, scheduling, node management, scaling behavior. When OpenAI published their "Scaling Kubernetes to 7,500 Nodes" post, they focused on scheduling and API server performance. Our challenge is different: it's about running thousands of GPU pods cost-effectively across regions while keeping inference latency low enough for safety-critical decisions.

On top of the cloud infrastructure, we support on-prem deployments running K3s for customers who need data to stay within their network. And we ship NVIDIA Orin edge devices (up to 275 TOPS INT8 inference) directly to customer facilities for local processing with minimal latency.

Three deployment models, one platform: multi-cluster cloud, on-prem K3s, edge devices.

## Cost Control: The GPU Tax

When most of your pods are GPU pods, cost is not a line item. It's THE line item.

Google Cloud Spot VMs save 60-91% compared to on-demand pricing. That's the difference between a sustainable infrastructure bill and a conversation with your CFO. But Spot VMs come with a 30-second termination notice, so you need to design for it.

**What we do:**

We run GPU inference workloads on Spot/preemptible nodes. Pods get killed a few times a day. For AI inference, this is acceptable: a brief interruption in video analysis is better than paying 3x for on-demand GPU nodes. Pods restart automatically, reconnect to camera streams, and resume within seconds.

Backend services and critical pipeline services run on stable, always-on nodes. Google's own guidance is clear: use Spot instances for fault-tolerant, stateless workloads with multiple replicas. Don't use them for single-replica stateful services or anything that can't handle a 30-second shutdown.

**What catches people off guard:**

Industry data shows Kubernetes clusters average 35-50% resource utilization. That means half your spend is wasted on idle resources. A single misconfigured GPU node running idle for a weekend can cost more than a month of CPU nodes.

We track resource allocation vs actual utilization separately. If you're paying for GPU time, someone better be using it. Vertical Pod Autoscaler (VPA) in recommendation mode analyzes historical usage and suggests optimal resource requests. We use this to right-size pods quarterly. It's the single highest-impact cost optimization you can make.

**Logging costs are the silent killer.** At this scale, cloud-native logging generates enormous volume. Without careful retention policies and log level management, your logging bill can rival your compute bill. We learned this the expensive way.

## Observability: Flying Blind at 10,000 Pods

If you can't see what's happening across ~10,000 pods in multiple clusters, you will eventually break something expensive and not know about it until a customer calls.

**The stack that works for us:**

For metrics, Prometheus + Grafana is the foundation. But a single Prometheus instance is designed for a single cluster. For multi-cluster setups, you need something like Thanos or Grafana Mimir to aggregate metrics centrally. Without this, you're checking dashboards per cluster, which means you'll miss cross-cluster issues.

For logs, we use cloud-native logging with aggressive filtering. Structured logging with correlation IDs from day one. When something breaks at 3 AM, you need to trace a request across 5 services in 2 clusters without guessing.

For cost visibility, Kubecost (open-source) integrates with Prometheus and gives per-pod, per-namespace, per-label cost dashboards in Grafana. At 10K+ pods, Prometheus cardinality management becomes critical. The general recommendation is to keep total active time series under 10 million per Prometheus instance and use recording rules to pre-aggregate high-cardinality metrics.

**Business metrics matter more than system metrics.** Knowing that a pod restarted is useful. Knowing that alert latency (time from video frame to safety alert) increased by 200ms is actionable. We monitor both, but business metrics drive our incident response.

**Alerting discipline saves sanity.** We route alerts to Slack and email. The key lesson: bad alerts are worse than no alerts. If your team gets 50 alerts a day and 48 are noise, they'll start ignoring all of them. We spent real time tuning thresholds, grouping related alerts, and adding filters. A good alert tells you what's wrong, where, and what to check first.

## Pod Organization: The Details That Matter at Scale

At ~10,000 pods, how you organize the internals of each pod matters as much as how you organize your clusters.

**Init containers for setup tasks.** We use them for waiting on dependencies, pulling configs, warming caches. This keeps the main container clean. Without init containers, your application code ends up full of retry loops and "wait for database" hacks. Important detail: init container resource requests are calculated as the max of all init containers (not the sum), since they run sequentially. Plan your resource budgets accordingly.

**Sidecars for cross-cutting concerns.** Logging agents, metrics exporters, proxy containers. When we needed to add distributed tracing to every service, we added a sidecar instead of modifying 30+ services. Consistent behavior, zero application code changes.

Kubernetes 1.28 introduced native sidecar support (KEP-753, beta in 1.29). Native sidecars start before your app containers and stop after them, solving the old problem of sidecar lifecycle ordering. Before this, there was no guarantee your log collector or service mesh proxy would be ready before your app tried to use it. If you're on 1.28+, use native sidecars. If not, the workaround is init containers that check readiness of sidecar-like dependencies.

**Resource requests and limits: be precise.** A pod requesting 4 GPU cores but using 1 is wasting money. A pod with no memory limit will eventually OOM-kill its neighbors. Use Guaranteed QoS class (requests == limits) for critical workloads to prevent noisy-neighbor issues. Use LimitRange objects at the namespace level to enforce default requests and prevent teams from deploying pods without resource specifications.

## Multi-Region: Not Just "Copy Config to Another Region"

Running clusters in multiple regions introduces problems that don't exist in a single-cluster setup.

**Data residency is non-negotiable.** Some customers require data to stay within specific geographic boundaries. We support multiple object storage backends: GCS, S3, and Azure Blob. Storage is configured per customer based on their compliance requirements. If a European customer says video data can't leave the EU, we configure their pipeline to process and store everything in the EU region. For Google Cloud specifically, Assured Workloads can enforce data location constraints at the organizational policy level.

**Cross-region traffic is expensive.** We're intentional about what moves between regions. AI inference results (alerts, metadata) are small and cheap to transfer. Video data is huge. Keep processing close to the source. This single architectural decision saves more money than most optimization efforts combined.

**Rollouts are regional.** We don't push to all clusters at once. One region first, monitor, then proceed. We started with Kustomize and are gradually moving to Helm for better templating across environments. Google Cloud's Config Sync can help with GitOps-style policy distribution across fleet clusters, but we haven't fully adopted it yet.

**Replicas and availability.** Use Pod Disruption Budgets (PDBs) to ensure that during voluntary disruptions (node drain, cluster upgrade), a minimum number of replicas stays available. Note: PDBs don't protect against involuntary disruptions like node crashes or OOM kills. Use topology spread constraints with `topologyKey: topology.kubernetes.io/zone` and `maxSkew: 1` to distribute pods evenly across availability zones. Combined with PDBs, this ensures high availability during both planned and unplanned events.

## Edge Devices: Where Cloud Assumptions Break

Shipping NVIDIA Orin devices to customer factories is nothing like deploying to the cloud.

The devices connect directly to cameras on-site and run AI inference locally. Orin can deliver up to 275 TOPS (INT8), which is enough to run multiple DeepStream pipelines simultaneously. A single GPU in the cloud (like a T4) can process 30+ simultaneous 1080p streams. The Orin handles fewer streams but with zero network latency, which matters when your platform needs to halt a production line in real time when someone is in danger.

Fleet management is the real challenge. These devices are in factories and warehouses around the world. Remote monitoring, over-the-air updates, and graceful failure recovery without sending an engineer on-site. When a device goes offline, we need to know why before the customer calls.

We also integrate with industrial control systems. The edge device isn't just observing; it's making decisions that affect physical machinery. The reliability bar is completely different from a web API returning a 500 error.

## On-Prem K3s: Cloud Semantics, Customer Network

Some customers don't want video data leaving their network. We support on-prem deployments with K3s.

K3s is a CNCF project that passes 100% of Kubernetes conformance tests in a binary under 100 MB with a minimum of 512 MB RAM. It bundles Flannel CNI, CoreDNS, and Traefik ingress by default. For HA, it supports embedded etcd with a minimum of 3 server nodes.

The tricky part is feature parity. When we ship a new feature, it needs to work on cloud, on-prem, and edge. Services can't assume cloud-specific APIs are available. We abstract storage, logging, and configuration so the same code runs everywhere.

Customer networks are isolated by design. They can't access our cloud clusters. Data flows are one-directional where needed (alerts out, config in) with strict security boundaries.

## What I'd Tell Someone Starting This Journey

**Invest in observability from day one.** Not "add monitoring later." Structured logging, correlation IDs, health endpoints, resource tracking. Build it into every service from the start. The debugging time this saves pays for itself within the first month.

**Separate concerns physically, not just logically.** GPU workloads and backend services have fundamentally different availability and cost requirements. Separate clusters, separate scaling policies, separate cost tracking.

**Be conservative with multi-region.** Not every service needs to run in every region. Centralize backend services, distribute only what needs to be close to customers (GPU inference). Less duplication, less maintenance, lower cost.

**Pay for what you use. Actually verify it.** Set up weekly cost reviews. Track cost per cluster, per namespace, per team. A $500/day mistake found on day 1 costs $500. Found at the end of the month, it costs $15,000.

**Design for three deployment models from the start.** Cloud, on-prem, and edge all have different constraints. If you bake cloud assumptions into your code early, retrofitting on-prem support later is painful. Abstract early.

**Always have a plan B.** Use replicas for critical services. Distribute pods across zones with topology spread constraints. Use Pod Disruption Budgets. Implement health checks, graceful shutdowns, and horizontal pod autoscaling. If your system has a single point of failure, it's not a matter of if it fails. It's when.

---

## Further Reading

If you want to go deeper on any of these topics, here are the resources I found most useful:

**Kubernetes Official Docs:**
- [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [Pod Disruption Budgets](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [Resource Management for Pods](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [KEP-753: Native Sidecar Containers](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/753-sidecar-containers)

**Google Cloud:**
- [Spot VMs: Pricing and Best Practices](https://cloud.google.com/compute/docs/instances/spot)
- [GKE Cost Optimization Best Practices](https://cloud.google.com/blog/products/containers-kubernetes/best-practices-for-running-cost-optimized-kubernetes-applications-on-gke)

**Scale References:**
- [OpenAI: Scaling Kubernetes to 7,500 Nodes](https://openai.com/research/scaling-kubernetes-to-7500-nodes)
- [CNCF Case Studies](https://www.cncf.io/case-studies/)
- [FinOps Foundation: Kubernetes Cost Management](https://www.finops.org/wg/containers-kubernetes/)

**Tools:**
- [K3s Documentation](https://docs.k3s.io/)
- [Kubecost: Kubernetes Cost Monitoring](https://docs.kubecost.com/)
- [NVIDIA DeepStream SDK](https://docs.nvidia.com/metropolis/deepstream/dev-guide/)

---

*I'm Burak Hamuryen, a Senior Software Engineer in Berlin with 14+ years of experience building distributed systems, real-time video processing, and cloud-native platforms. More at [hamuryen.com](https://hamuryen.com).*
