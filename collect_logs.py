from kubernetes import client, config
import os

config.load_kube_config()
v1 = client.CoreV1Api()
namespace = "default"

if not os.path.exists("sample_logs"):
    os.makedirs("sample_logs")

pods = v1.list_namespaced_pod(namespace=namespace)

for pod in pods.items:
    name = pod.metadata.name
    try:
        log = v1.read_namespaced_pod_log(name=name, namespace=namespace, tail_lines=100)
        with open(f"sample_logs/{name}.log", "w") as f:
            f.write(log)
        print(f"Saved logs for {name}")
    except Exception as e:
        print(f"Error: {e}")
