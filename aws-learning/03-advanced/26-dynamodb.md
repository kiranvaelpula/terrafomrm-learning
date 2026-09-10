# Chapter 26: DynamoDB - Managed NoSQL

## Overview

Amazon DynamoDB is a fully managed, serverless, key-value and document NoSQL database that delivers single-digit millisecond performance at any scale.

## 📖 Understanding DynamoDB (Intuition First)

Imagine the difference between a meticulously organized filing cabinet with labeled folders and cross-referenced index cards (a relational database) versus a giant coat check at a stadium where you hand over your coat, get a numbered ticket, and instantly retrieve it later by that ticket. The relational database is powerful for complex queries and relationships, but it slows down and gets expensive as it grows to millions of items. The coat check is dead simple — give a key, get the item, blazing fast — and it stays fast whether there are 100 coats or 100 million. DynamoDB is that coat check: give it a key, it returns your item in milliseconds, no matter how big it gets.

The reason DynamoDB exists is that relational databases hit a wall at massive scale. When you have billions of records and millions of requests per second, the JOINs, flexible queries, and single-server design of a traditional database become bottlenecks. DynamoDB throws away some of that flexibility (no JOINs, limited query patterns) in exchange for something relational databases can't easily do: **predictable single-digit-millisecond performance at virtually unlimited scale**, with zero servers to manage.

The core mental shift is that in DynamoDB, **you design your data around your access patterns, not the other way around.** In SQL, you normalize data into tidy tables and figure out queries later. In DynamoDB, you must know upfront how you'll read the data — "get a user by ID," "list a user's orders by date" — and design your keys to make exactly those queries fast. Get the key design right and it's magic; get it wrong and you'll fight the database.

The magic ingredient is the **partition key**. DynamoDB spreads your data across many servers (partitions) based on a hash of the partition key. Choosing a key that distributes data and traffic evenly is everything — a good key means infinite smooth scaling; a bad key (where all traffic hits one value) creates a "hot partition" that throttles, no matter how much capacity you buy. Much of DynamoDB expertise is really about picking good keys.

The trade-off to internalize: DynamoDB is the right tool when you need massive scale, predictable low latency, and simple key-based access (user sessions, shopping carts, IoT data, gaming leaderboards, real-time bidding). It's the wrong tool when you need complex ad-hoc queries, JOINs across many entities, or strong relational integrity — that's what RDS/Aurora are for. Choosing DynamoDB vs a relational database based on access patterns is a classic architecture interview question.

---

## Core Concepts

```
TABLE       — a collection of items (like a table, but schemaless)
ITEM        — a single record (like a row), up to 400KB
ATTRIBUTE   — a field within an item (like a column, but flexible per item)

KEYS:
  Partition Key (PK)  — determines which partition stores the item (required)
  Sort Key (SK)       — orders items within a partition (optional)
  Together: Partition Key [+ Sort Key] = the primary key (must be unique)
```

## Primary Key Types

```
1. Simple (Partition key only):
   PK=user_id → one item per user_id

2. Composite (Partition key + Sort key):
   PK=user_id, SK=order_date → many orders per user, sorted by date
   Enables queries like "all orders for user X between dates"
```

## Capacity Modes

```
ON-DEMAND:
  - Pay per request, scales automatically, no capacity planning
  - Best for unpredictable/spiky traffic or new apps

PROVISIONED:
  - Set Read Capacity Units (RCU) and Write Capacity Units (WCU)
  - Cheaper for predictable, steady traffic
  - Can add auto-scaling
```

## Basic Operations (boto3)

```python
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Users")

# PUT — create/replace an item
table.put_item(Item={"user_id": "u123", "name": "Kiran", "tier": "premium"})

# GET — retrieve by primary key (fast, single-digit ms)
resp = table.get_item(Key={"user_id": "u123"})
item = resp.get("Item")

# QUERY — get items by partition key (+ sort key conditions)
from boto3.dynamodb.conditions import Key
resp = table.query(
    KeyConditionExpression=Key("user_id").eq("u123") & Key("order_date").gt("2026-01-01")
)

# UPDATE — modify attributes
table.update_item(
    Key={"user_id": "u123"},
    UpdateExpression="SET tier = :t",
    ExpressionAttributeValues={":t": "enterprise"}
)

# DELETE
table.delete_item(Key={"user_id": "u123"})
```

## Query vs Scan (Critical Distinction)

```
QUERY: uses the partition key → fast, efficient, reads only matching items
SCAN:  reads the ENTIRE table then filters → slow, expensive, avoid at scale

Rule: design keys so you QUERY, never SCAN, for your main access patterns.
A Scan on a large table is a common performance/cost mistake.
```

## Secondary Indexes (query by other attributes)

```
GLOBAL SECONDARY INDEX (GSI):
  - Different partition + sort key than the table
  - Query by attributes other than the primary key
  - Has its own capacity; eventually consistent

LOCAL SECONDARY INDEX (LSI):
  - Same partition key, different sort key
  - Must be created at table creation time
```

## Advanced Features

```
DynamoDB Streams  — a change log of item modifications (like a CDC feed);
                    trigger Lambda on inserts/updates/deletes
Global Tables     — multi-region, multi-active replication (near-zero RPO)
DAX               — in-memory cache, microsecond reads for hot data
TTL               — auto-expire/delete items after a timestamp (e.g., sessions)
Transactions      — ACID across multiple items when you need it
PITR              — point-in-time recovery (restore to any second in 35 days)
```

## The Hot Partition Problem

```
BAD partition key:  status ("active"/"inactive")
  → only 2 values → all traffic hits 2 partitions → throttling ("hot partition")

GOOD partition key: user_id (millions of distinct values)
  → traffic spreads evenly across many partitions → smooth scaling

Choose a high-cardinality key that distributes access evenly.
```

## DynamoDB vs RDS (When to Use Which)

| Factor | DynamoDB (NoSQL) | RDS/Aurora (Relational) |
|--------|------------------|-------------------------|
| Data model | Key-value / document | Tables with relationships |
| Scale | Virtually unlimited | Vertical + read replicas |
| Latency | Single-digit ms, predictable | Varies with query/load |
| Queries | Key-based (design upfront) | Flexible, ad-hoc, JOINs |
| Schema | Flexible/schemaless | Fixed schema |
| Best for | Sessions, carts, IoT, leaderboards, high scale | Complex queries, transactions, reporting |
| Servers | Serverless (none) | Managed instances |

---

## 🎯 Interview Quick Points

- DynamoDB = fully managed, serverless NoSQL (key-value + document) with single-digit-ms latency at any scale
- Analogy: a coat check — give a key, get the item instantly, stays fast at any size
- **Design around access patterns**, not normalized tables (opposite of SQL thinking)
- **Partition key** determines data distribution; choose high-cardinality to avoid hot partitions
- Primary key = partition key [+ optional sort key]; must be unique
- **QUERY (efficient) vs SCAN (reads whole table — avoid at scale)**
- Capacity: **on-demand** (spiky/unpredictable) vs **provisioned** (steady, cheaper)
- **GSI/LSI** let you query by non-key attributes
- Advanced: **Streams** (CDC → Lambda), **Global Tables** (multi-region), **DAX** (cache), **TTL** (auto-expire)
- Supports **ACID transactions** and **point-in-time recovery**
- **Hot partition** = a low-cardinality key causing throttling on one partition
- Choose DynamoDB for scale + key access; RDS for complex queries/JOINs/relationships

## Next Steps

Continue to [Step Functions](27-step-functions.md).
