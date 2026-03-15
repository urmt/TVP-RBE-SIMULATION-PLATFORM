#!/usr/bin/env /usr/bin/python3
"""CLI for RBE Resource Tracker."""

import argparse
import sys
import json
from .api import ResourceAPI


def cmd_add_resource(args):
    api = ResourceAPI(args.db)
    metadata = json.loads(args.metadata) if args.metadata else None
    success = api.create_resource(
        resource_id=args.id, name=args.name,
        resource_type=args.type.upper(), unit=args.unit,
        initial_quantity=args.quantity, metadata=metadata
    )
    if success:
        print(f"Resource '{args.name}' added with ID: {args.id}")
        return 0
    print(f"Error: Resource '{args.id}' already exists", file=sys.stderr)
    return 1


def cmd_list_resources(args):
    api = ResourceAPI(args.db)
    resources = api.list_resources()
    if not resources:
        print("No resources found.")
        return 0
    if args.json:
        print(json.dumps(resources, indent=2, default=str))
    else:
        print(f"{'ID':<20} {'Name':<20} {'Type':<10} {'Quantity':<15}")
        print("-" * 70)
        for r in resources:
            qty = f"{r['current_quantity']:.2f} {r['unit']}"
            print(f"{r['resource_id']:<20} {r['name']:<20} {r['resource_type']:<10} {qty:<15}")
    return 0


def cmd_get_resource(args):
    api = ResourceAPI(args.db)
    resource = api.get_resource(args.id)
    if not resource:
        print(f"Error: Resource '{args.id}' not found", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(resource, indent=2, default=str))
    else:
        for key, val in resource.items():
            print(f"{key}: {val}")
    return 0


def cmd_allocate(args):
    api = ResourceAPI(args.db)
    success = api.allocate(args.resource_id, args.amount, args.to, args.purpose)
    if success:
        print(f"Allocated {args.amount} from '{args.resource_id}'")
        return 0
    print("Error: Allocation failed", file=sys.stderr)
    return 1


def cmd_add_quantity(args):
    api = ResourceAPI(args.db)
    success = api.add_quantity(args.resource_id, args.amount)
    if success:
        print(f"Added {args.amount} to '{args.resource_id}'")
        return 0
    print("Error: Failed to add quantity", file=sys.stderr)
    return 1


def cmd_history(args):
    api = ResourceAPI(args.db)
    history = api.get_allocation_history(args.resource_id)
    if not history:
        print("No allocation history found.")
        return 0
    if args.json:
        print(json.dumps(history, indent=2, default=str))
    else:
        print(f"{'Time':<20} {'Resource':<20} {'Amount':<12} {'To':<15} {'Purpose'}")
        print("-" * 90)
        for h in history:
            time_str = str(h['allocated_at'])[:19]
            amount_str = f"{h['allocated_quantity']:.2f} {h['unit']}"
            to_str = h.get('allocated_to') or '-'
            purpose_str = h.get('purpose') or '-'
            print(f"{time_str:<20} {h['resource_name']:<20} {amount_str:<12} {to_str:<15} {purpose_str}")
    return 0


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="rbe-tracker",
        description="RBE Resource Tracker - Manage physical resources"
    )
    parser.add_argument("--db", default="rbe_resources.db", help="Database path")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Add resource
    add_parser = subparsers.add_parser("add", help="Add a new resource")
    add_parser.add_argument("id", help="Resource ID")
    add_parser.add_argument("name", help="Resource name")
    add_parser.add_argument("type", choices=["energy", "water", "material"])
    add_parser.add_argument("unit", help="Unit (kWh, m3, kg, unit)")
    add_parser.add_argument("--quantity", type=float, default=0.0)
    add_parser.add_argument("--metadata", help="JSON metadata")
    add_parser.set_defaults(func=cmd_add_resource)
    
    # List resources
    list_parser = subparsers.add_parser("list", help="List all resources")
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=cmd_list_resources)
    
    # Get resource
    get_parser = subparsers.add_parser("get", help="Get resource details")
    get_parser.add_argument("id", help="Resource ID")
    get_parser.add_argument("--json", action="store_true")
    get_parser.set_defaults(func=cmd_get_resource)
    
    # Allocate
    alloc_parser = subparsers.add_parser("allocate", help="Allocate resources")
    alloc_parser.add_argument("resource_id", help="Resource ID")
    alloc_parser.add_argument("amount", type=float, help="Amount")
    alloc_parser.add_argument("--to", help="Allocate to")
    alloc_parser.add_argument("--purpose", help="Purpose")
    alloc_parser.set_defaults(func=cmd_allocate)
    
    # Add quantity
    add_qty_parser = subparsers.add_parser("add-quantity", help="Add quantity")
    add_qty_parser.add_argument("resource_id", help="Resource ID")
    add_qty_parser.add_argument("amount", type=float, help="Amount")
    add_qty_parser.set_defaults(func=cmd_add_quantity)
    
    # History
    hist_parser = subparsers.add_parser("history", help="Show history")
    hist_parser.add_argument("--resource-id", help="Filter by resource")
    hist_parser.add_argument("--json", action="store_true")
    hist_parser.set_defaults(func=cmd_history)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
