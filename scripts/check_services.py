#!/usr/bin/env python
"""
Test connectivity to all microservices
Verifies that all services are up and running
"""
import logging
import requests
import sys
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICES = {
    "Orchestrator": "http://localhost:8000/health",
    "Job Fetcher": "http://localhost:8001/health",
    "Matching Engine": "http://localhost:8002/health",
    "Resume Engine": "http://localhost:8003/health",
    "Apply Engine": "http://localhost:8004/health",
    "Notification": "http://localhost:8005/health"
}


def check_services() -> Dict[str, bool]:
    """Check health of all services"""
    results = {}
    
    for service_name, endpoint in SERVICES.items():
        try:
            response = requests.get(endpoint, timeout=5)
            is_healthy = response.status_code == 200
            results[service_name] = is_healthy
            status = "✓ HEALTHY" if is_healthy else "✗ UNHEALTHY"
            logger.info(f"{service_name}: {status}")
        except Exception as e:
            results[service_name] = False
            logger.error(f"{service_name}: ✗ UNREACHABLE ({e})")
    
    return results


def main():
    """Run service health checks"""
    logger.info("Checking microservices health...\n")
    results = check_services()
    
    healthy = sum(1 for v in results.values() if v)
    total = len(results)
    
    logger.info(f"\nSummary: {healthy}/{total} services healthy")
    
    if healthy == total:
        logger.info("All services operational!")
        return 0
    else:
        logger.warning(f"{total - healthy} services are down")
        return 1


if __name__ == "__main__":
    sys.exit(main())
