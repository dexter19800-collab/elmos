#!/usr/bin/env python3
"""Check Cloudera Manager services and report errors for unhealthy ones."""

import argparse
import requests


def fetch_services(host: str, port: int, username: str, password: str, cluster: str):
    """Retrieve the list of services for a given cluster from Cloudera Manager."""
    base_url = f"http://{host}:{port}/api/v19"
    url = f"{base_url}/clusters/{cluster}/services"
    response = requests.get(url, auth=(username, password))
    response.raise_for_status()
    return response.json().get("items", [])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vérifie l'état des services dans Cloudera Manager et affiche les erreurs."
    )
    parser.add_argument("--host", required=True, help="Hôte de Cloudera Manager")
    parser.add_argument("--port", type=int, default=7180, help="Port de Cloudera Manager")
    parser.add_argument("--user", required=True, help="Nom d'utilisateur API")
    parser.add_argument("--password", required=True, help="Mot de passe API")
    parser.add_argument("--cluster", required=True, help="Nom du cluster à vérifier")

    args = parser.parse_args()
    services = fetch_services(args.host, args.port, args.user, args.password, args.cluster)

    for service in services:
        name = service.get("name")
        health = service.get("healthSummary")
        if health != "GOOD":
            print(f"Service {name} est en état {health}.")
            checks = service.get("healthChecks", [])
            for check in checks:
                if check.get("summary") != "GOOD":
                    print(f"  - {check.get('name')}: {check.get('description')}")
            if not checks:
                print("  Aucun détail d'erreur disponible.")


if __name__ == "__main__":
    main()
